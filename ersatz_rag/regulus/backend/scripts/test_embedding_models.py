#!/usr/bin/env python3
"""
Test script to demonstrate different embedding models with the same content
"""
import os
import sys
import fitz

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.indexing import IndexingService
from app.config import EMBEDDING_MODELS, get_embedding_model
from leann.api import LeannSearcher

def test_embedding_model_comparison():
    """Compare different embedding models on the same content"""
    
    print("=== EMBEDDING MODEL COMPARISON TEST ===")
    print()
    
    # Test PDF path
    pdf_path = "/Volumes/WS4TB/ERSATZ_RAG/WS_ED/Acceptable Uses and Governance of Artificial Intelligence Policy_FINAL_2-14-24.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ Test PDF not found: {pdf_path}")
        return
    
    # Test queries
    test_queries = [
        "artificial intelligence acceptable uses",
        "confidential information handling"
    ]
    
    # Models to test (subset for demonstration)
    models_to_test = {
        "granite": "ibm-granite/granite-embedding-english-r2",
        "contriever": "facebook/contriever"
    }
    
    results_comparison = {}
    
    for model_key, model_name in models_to_test.items():
        print(f"🧠 TESTING MODEL: {model_name}")
        print("-" * 60)
        
        try:
            # Initialize indexing service with specific model
            service = IndexingService(embedding_model=model_key)
            
            # Create temporary index for this model
            from pathlib import Path
            temp_pdf = Path(pdf_path)
            index_path = service.run_indexing([temp_pdf])
            
            print(f"✅ Index created: {index_path}")
            
            # Test search with this model
            searcher = LeannSearcher(index_path.replace('.leann', ''))
            
            model_results = []
            for query in test_queries:
                print(f"🔍 Query: '{query}'")
                
                results = searcher.search(query, top_k=1)
                if results:
                    result = results[0]
                    score = result.score
                    node_id = result.metadata.get('node_id', 'N/A')
                    
                    print(f"   📊 Score: {score:.4f}")
                    print(f"   🏷️  Node: {node_id}")
                    
                    model_results.append({
                        'query': query,
                        'score': score,
                        'node_id': node_id,
                        'model': model_name
                    })
                else:
                    print("   ❌ No results")
                    
            results_comparison[model_key] = model_results
            print()
            
        except Exception as e:
            print(f"❌ Error with {model_name}: {e}")
            print()
    
    # Compare results across models
    print("📊 EMBEDDING MODEL COMPARISON RESULTS:")
    print("=" * 50)
    
    for query in test_queries:
        print(f"\\nQuery: '{query}'")
        print("-" * 30)
        
        for model_key in models_to_test.keys():
            if model_key in results_comparison:
                query_results = [r for r in results_comparison[model_key] if r['query'] == query]
                if query_results:
                    result = query_results[0]
                    print(f"  {model_key:12}: {result['score']:8.4f} ({result['node_id']})")
    
    print()
    print("🎯 RECOMMENDATIONS:")
    print("- IBM Granite: Best for enterprise/healthcare applications")
    print("- PubMed BERT: Optimal for medical/research content")  
    print("- Contriever: Good general-purpose retrieval")
    print("- Configure via EMBEDDING_MODEL environment variable")

if __name__ == "__main__":
    test_embedding_model_comparison()