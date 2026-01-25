import hashlib
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any

import fitz  # PyMuPDF
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from opensearchpy import OpenSearch, helpers

from .config import (
    HYBRID_EMBEDDING_MODEL,
    QDRANT_URL,
    QDRANT_COLLECTION,
    OPENSEARCH_URL,
    OPENSEARCH_INDEX,
    EMBED_BATCH_SIZE,
    CHUNK_PARAS,
    CHUNK_OVERLAP,
)


@dataclass
class IngestResult:
    doc_id: str
    source_file: str
    qdrant_points: int
    opensearch_docs: int
    chunks: int
    sha256: str


def _hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def _split_paragraphs(text: str) -> List[str]:
    # Normalize newlines and split on blank lines
    lines = [ln.strip() for ln in text.splitlines()]
    paras: List[str] = []
    cur: List[str] = []
    for ln in lines:
        if ln:
            cur.append(ln)
        else:
            if cur:
                paras.append(" ".join(cur))
                cur = []
    if cur:
        paras.append(" ".join(cur))
    return [p for p in paras if p]


def _chunk_paragraphs(paras: List[str], k: int, overlap: int) -> List[Dict[str, Any]]:
    chunks: List[Dict[str, Any]] = []
    if k <= 0:
        k = 2
    if overlap < 0:
        overlap = 0
    start = 0
    while start < len(paras):
        end = min(len(paras), start + k)
        block = paras[start:end]
        text = "\n\n".join(block)
        chunks.append({
            "text": text,
            "para_start": start,
            "para_end": end - 1,
        })
        if end == len(paras):
            break
        start = end - overlap
        if start < 0:
            start = 0
    return chunks


class HybridIngestor:
    def __init__(self) -> None:
        self.model = SentenceTransformer(HYBRID_EMBEDDING_MODEL)
        self.qdrant = QdrantClient(url=QDRANT_URL)
        self.os = OpenSearch(OPENSEARCH_URL, timeout=30, use_ssl=False, verify_certs=False)
        # Ensure indices exist
        self._ensure_qdrant_collection()
        self._ensure_opensearch_index()

    def _ensure_qdrant_collection(self) -> None:
        dim = self.model.get_sentence_embedding_dimension()
        try:
            self.qdrant.get_collection(QDRANT_COLLECTION)
        except Exception:
            self.qdrant.recreate_collection(
                collection_name=QDRANT_COLLECTION,
                vectors_config=qmodels.VectorParams(size=dim, distance=qmodels.Distance.COSINE),
            )

    def _ensure_opensearch_index(self) -> None:
        if not self.os.indices.exists(index=OPENSEARCH_INDEX):
            mapping = {
                "settings": {
                    "index": {"number_of_shards": 1, "number_of_replicas": 0},
                    "analysis": {
                        "analyzer": {
                            "english_custom": {
                                "type": "standard",
                                "stopwords": "_english_"
                            }
                        }
                    }
                },
                "mappings": {
                    "properties": {
                        "doc_id": {"type": "keyword"},
                        "chunk_id": {"type": "keyword"},
                        "title": {"type": "text", "analyzer": "english_custom"},
                        "section_path": {"type": "keyword"},
                        "source_file": {"type": "keyword"},
                        "body": {"type": "text", "analyzer": "english_custom"},
                        "page": {"type": "integer"},
                    }
                }
            }
            self.os.indices.create(index=OPENSEARCH_INDEX, body=mapping)

    def _read_pdf(self, pdf_path: Path) -> List[Dict[str, Any]]:
        doc = fitz.open(str(pdf_path))
        try:
            pieces: List[Dict[str, Any]] = []
            for i, page in enumerate(doc):
                text = page.get_text("text") or ""
                paras = _split_paragraphs(text)
                chunks = _chunk_paragraphs(paras, CHUNK_PARAS, CHUNK_OVERLAP)
                for j, ch in enumerate(chunks):
                    pieces.append({
                        "page": i + 1,
                        "title": f"Page {i+1}",
                        "body": ch["text"],
                        "section_path": f"page.{i+1}",
                        "para_start": ch["para_start"],
                        "para_end": ch["para_end"],
                    })
            return pieces
        finally:
            doc.close()

    def ingest_pdf(self, pdf_path: str, source_file: str | None = None) -> IngestResult:
        pdf = Path(pdf_path)
        sha = _hash_file(pdf)
        doc_ns = uuid.UUID(hashlib.sha1(sha.encode()).hexdigest()[0:32])
        doc_id = str(doc_ns)
        pieces = self._read_pdf(pdf)
        texts = [p["body"] for p in pieces]

        # Embeddings
        vectors: List[List[float]] = []
        for i in tqdm(range(0, len(texts), EMBED_BATCH_SIZE), desc="Embeddings"):
            batch = texts[i:i+EMBED_BATCH_SIZE]
            vecs = self.model.encode(batch, normalize_embeddings=True).tolist()
            vectors.extend(vecs)

        # Qdrant upsert
        q_points: List[qmodels.PointStruct] = []
        for idx, p in enumerate(pieces):
            chunk_uuid = uuid.uuid5(doc_ns, f"chunk-{idx}")
            payload = {
                "doc_id": doc_id,
                "chunk_id": str(chunk_uuid),
                "title": p["title"],
                "source_file": source_file or pdf.name,
                "section_path": p["section_path"],
                "page": p["page"],
                "para_start": p["para_start"],
                "para_end": p["para_end"],
            }
            q_points.append(qmodels.PointStruct(id=str(chunk_uuid), vector=vectors[idx], payload=payload))
        if q_points:
            self.qdrant.upsert(collection_name=QDRANT_COLLECTION, points=q_points)

        # OpenSearch bulk index
        actions = []
        for idx, p in enumerate(pieces):
            chunk_uuid = uuid.uuid5(doc_ns, f"chunk-{idx}")
            actions.append({
                "_index": OPENSEARCH_INDEX,
                "_id": str(chunk_uuid),
                "_source": {
                    "doc_id": doc_id,
                    "chunk_id": str(chunk_uuid),
                    "title": p["title"],
                    "section_path": p["section_path"],
                    "source_file": source_file or pdf.name,
                    "body": p["body"],
                    "page": p["page"],
                },
            })
        if actions:
            helpers.bulk(self.os, actions)
            # Force a refresh so that subsequent count/search sees the documents immediately
            try:
                self.os.indices.refresh(index=OPENSEARCH_INDEX)
            except Exception:
                pass

        return IngestResult(
            doc_id=doc_id,
            source_file=source_file or pdf.name,
            qdrant_points=len(q_points),
            opensearch_docs=len(actions),
            chunks=len(pieces),
            sha256=sha,
        )
