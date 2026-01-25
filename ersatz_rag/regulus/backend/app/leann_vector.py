from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any

class LEANNVectorDB:
    def __init__(self, host: str = "localhost", port: int = 6333, collection_name: str = "leann_chunks"):
        self.client = QdrantClient(host=host, port=port)
        self.collection_name = collection_name
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        self._ensure_collection()

    def _ensure_collection(self):
        if self.collection_name not in self.client.get_collections().collections:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=qmodels.VectorParams(size=384, distance=qmodels.Distance.COSINE)
            )

    def upsert_chunks(self, chunks: List[Dict[str, Any]]):
        texts = [c["text"] for c in chunks]
        embeddings = self.embedder.encode(texts, show_progress_bar=False)
        points = [
            qmodels.PointStruct(
                id=c["id"],
                vector=emb.tolist(),
                payload=c
            ) for c, emb in zip(chunks, embeddings)
        ]
        self.client.upsert(collection_name=self.collection_name, points=points)

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        query_vec = self.embedder.encode([query])[0]
        results = self.client.search(collection_name=self.collection_name, query_vector=query_vec, limit=limit)
        return [r.payload for r in results]
