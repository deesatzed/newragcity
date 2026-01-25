from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from opensearchpy import OpenSearch

from .config import (
    HYBRID_EMBEDDING_MODEL,
    QDRANT_URL,
    QDRANT_COLLECTION,
    OPENSEARCH_URL,
    OPENSEARCH_INDEX,
)


@dataclass
class HybridResult:
    chunk_id: str
    doc_id: str
    title: str | None
    source_file: str | None
    page: int | None
    body: str
    score: float


def rrf_fuse(rank_lists: List[List[str]], k: float = 60.0) -> Dict[str, float]:
    scores: Dict[str, float] = {}
    for ranks in rank_lists:
        for r, cid in enumerate(ranks, start=1):
            scores[cid] = scores.get(cid, 0.0) + 1.0 / (k + r)
    return scores


class HybridRetriever:
    def __init__(self) -> None:
        self.embedder = SentenceTransformer(HYBRID_EMBEDDING_MODEL)
        self.cross = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        self.q = QdrantClient(url=QDRANT_URL)
        self.os = OpenSearch(OPENSEARCH_URL, timeout=30, use_ssl=False, verify_certs=False)

    def _search_opensearch(self, query: str, topk: int) -> Tuple[List[str], Dict[str, HybridResult]]:
        body = {
            "size": topk,
            "query": {"match": {"body": query}},
            "_source": ["doc_id", "chunk_id", "title", "source_file", "body", "page"],
        }
        resp = self.os.search(index=OPENSEARCH_INDEX, body=body)
        ids: List[str] = []
        by_id: Dict[str, HybridResult] = {}
        for hit in resp.get("hits", {}).get("hits", []):
            src = hit.get("_source", {})
            cid = src.get("chunk_id") or hit.get("_id")
            ids.append(cid)
            by_id[cid] = HybridResult(
                chunk_id=cid,
                doc_id=src.get("doc_id"),
                title=src.get("title"),
                source_file=src.get("source_file"),
                page=src.get("page"),
                body=src.get("body", ""),
                score=float(hit.get("_score", 0.0)),
            )
        return ids, by_id

    def _fetch_os_by_id(self, chunk_id: str) -> HybridResult | None:
        try:
            doc = self.os.get(index=OPENSEARCH_INDEX, id=chunk_id)
            src = doc.get("_source", {})
            return HybridResult(
                chunk_id=chunk_id,
                doc_id=src.get("doc_id"),
                title=src.get("title"),
                source_file=src.get("source_file"),
                page=src.get("page"),
                body=src.get("body", ""),
                score=0.0,
            )
        except Exception:
            return None

    def _search_qdrant(self, query: str, topk: int) -> List[Tuple[str, float]]:
        vec = self.embedder.encode([query], normalize_embeddings=True)[0]
        res = self.q.search(
            collection_name=QDRANT_COLLECTION,
            query_vector=vec,
            limit=topk,
            with_payload=True,
        )
        out: List[Tuple[str, float]] = []
        for p in res:
            cid = str(p.id)
            score = float(p.score)
            out.append((cid, score))
        return out

    def search(self, query: str, k_lex: int = 100, k_vec: int = 100, rerank_k: int = 50, final_k: int = 10) -> List[HybridResult]:
        # 1) Candidate generation
        lex_ids, lex_map = self._search_opensearch(query, k_lex)
        vec_pairs = self._search_qdrant(query, k_vec)
        vec_ids = [cid for cid, _ in vec_pairs]

        # 2) RRF fusion
        fused_scores = rrf_fuse([lex_ids, vec_ids])

        # 3) Collect candidate details; fetch body from OS when missing
        candidates: Dict[str, HybridResult] = {}
        for cid in set(list(fused_scores.keys())):
            if cid in lex_map:
                hr = lex_map[cid]
            else:
                hr = self._fetch_os_by_id(cid)
                if hr is None:
                    continue
            hr.score = fused_scores.get(cid, 0.0)
            candidates[cid] = hr

        # 4) Cross-encoder rerank top rerank_k by fused score
        prelim = sorted(candidates.values(), key=lambda x: x.score, reverse=True)[:rerank_k]
        pairs = [(query, c.body) for c in prelim]
        if pairs:
            ce_scores = self.cross.predict(pairs).tolist()
            for c, s in zip(prelim, ce_scores):
                c.score = float(s)

        # 5) Final selection
        final = sorted(prelim, key=lambda x: x.score, reverse=True)[:final_k]
        return final
