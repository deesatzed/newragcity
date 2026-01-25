import json
import pickle
from pathlib import Path
from typing import List, Dict, Any

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

class SimpleFaissBackend:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.chunks = []
        self.metadata = []
        
    def add_chunk(self, text: str, doc_metadata: Dict[str, Any]):
        """Add a text chunk with metadata"""
        # Encode the text
        embedding = self.model.encode(text)
        
        # Store chunk and metadata
        self.chunks.append(text)
        self.metadata.append(doc_metadata)
        
        # Add to FAISS index
        if self.index is None:
            dimension = embedding.shape[0]
            self.index = faiss.IndexFlatIP(dimension)  # Inner product similarity
            
        # Normalize embedding for cosine similarity
        embedding = embedding / np.linalg.norm(embedding)
        self.index.add(np.array([embedding]).astype('float32'))
        
    def build_index(self, index_path: str):
        """Save the index to disk"""
        if self.index is None:
            raise ValueError("No index to build")
            
        # Save FAISS index
        faiss.write_index(self.index, f"{index_path}.faiss")
        
        # Save chunks and metadata
        with open(f"{index_path}.chunks", 'wb') as f:
            pickle.dump(self.chunks, f)
            
        with open(f"{index_path}.metadata", 'wb') as f:
            pickle.dump(self.metadata, f)
            
    def search(self, query: str, k: int = 10):
        """Search for similar chunks"""
        if self.index is None:
            return []
            
        # Encode query
        query_embedding = self.model.encode(query)
        query_embedding = query_embedding / np.linalg.norm(query_embedding)
        
        # Search
        scores, indices = self.index.search(
            np.array([query_embedding]).astype('float32'), k
        )
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.chunks):
                results.append({
                    'content': self.chunks[idx],
                    'metadata': self.metadata[idx],
                    'score': float(score)
                })
                
        return results

class SimpleLeannSearcher:
    def __init__(self, index_path: str):
        self.index_path = index_path
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.chunks = []
        self.metadata = []
        self._load_index()
        
    def _load_index(self):
        """Load the index from disk"""
        try:
            # Load FAISS index
            self.index = faiss.read_index(f"{self.index_path}.faiss")
            
            # Load chunks and metadata
            with open(f"{self.index_path}.chunks", 'rb') as f:
                self.chunks = pickle.load(f)
                
            with open(f"{self.index_path}.metadata", 'rb') as f:
                self.metadata = pickle.load(f)
        except FileNotFoundError:
            # Index doesn't exist yet
            pass
            
    def search(self, query: str, k: int = 10):
        """Search for similar chunks"""
        if self.index is None:
            return []
            
        # Encode query
        query_embedding = self.model.encode(query)
        query_embedding = query_embedding / np.linalg.norm(query_embedding)
        
        # Search
        scores, indices = self.index.search(
            np.array([query_embedding]).astype('float32'), k
        )
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.chunks):
                results.append({
                    'content': self.chunks[idx],
                    'metadata': self.metadata[idx],
                    'score': float(score)
                })
                
        return results