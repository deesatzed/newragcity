#!/usr/bin/env python3
"""
Complete demonstration of the enhanced 3-approach RAG system:
1. PageIndex (Fallback): Real-time document structure extraction
2. LEANN + Hybrid Search: Efficient vector, lexical, and reranked search
3. deepConf + Calibration: Advanced, calibrated confidence scoring

This script demonstrates a real end-to-end workflow:
- Processing a document from scratch.
- Building a search index.
- Running hybrid search queries.
- Displaying calibrated confidence scores.
"""

import sys
import os
from pathlib import Path
from app.three_approach_integration import ThreeApproachRAG

def main():
    print("🚀 COMPLETE 3-APPROACH REGULUS DEMONSTRATION (FIXED & LIVE)")
    print("=" * 60)

    # Initialize the complete system
    rag_system = ThreeApproachRAG(
        embedding_model="ibm-granite/granite-embedding-english-r2",
        confidence_threshold=0.80
    )

    # --- Step 1: Process a document and build the index ---
    print("\n" + "="*60)
    print("STEP 1: LIVE DOCUMENT PROCESSING & INDEXING")
    print("="*60)

    # Use the sample policy document included in the tests
    pdf_path = "tests/test_data/sample_policy.pdf"
    if not os.path.exists(pdf_path):
        print(f"❌ Sample document not found at {pdf_path}")
        print("   Please ensure the repository is complete.")
        return

    # Process the document to extract its structure
    document_structure = rag_system.process_document(pdf_path)
    print(f"📄 Document processed using '{document_structure['processing_metadata']['reasoning_engine']}' engine.")

    # Build the search index in a temporary location
    index_path = "/tmp/live_regulus_demo_index"
    rag_system.build_leann_index(document_structure, index_path)
    print(f"✅ Index built successfully at: {index_path}")

    # --- Step 2: Run Hybrid Search with Calibrated Confidence ---
    print(f"\n" + "="*60)
    print("STEP 2: ENHANCED HYBRID SEARCH WITH DEEPCONF CALIBRATION")
    print("="*60)

    test_queries = [
        "What is the purpose of this policy?",
        "Who does this policy apply to?",
        "What are the key principles of AI development?",
        "Are there any restricted uses of AI?",
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Query {i}: {query}")
        print("-" * 40)

        # Execute enhanced hybrid search
        results_data = rag_system.enhanced_hybrid_search(query, index_path, top_k=3)

        # Display results
        if not results_data or not results_data.get('results'):
            print("   No results found.")
            continue

        confidence_analysis = results_data.get('confidence_analysis', {})
        approach_summary = results_data.get('approach_summary', {})

        print(f"📊 Confidence Analysis:")
        if confidence_analysis:
            avg_calibrated = confidence_analysis.get('calibrated_confidence', {}).get('average', 0)
            high_conf_count = confidence_analysis.get('above_threshold_count', 0)
            print(f"   Average Calibrated Confidence: {avg_calibrated:.3f}")
            print(f"   High confidence results (>{approach_summary.get('calibrated_confidence_threshold', 0.8)}): {high_conf_count}")

        print(f"\n📈 Approach Summary:")
        if approach_summary:
            print(f"   Search Method: {results_data.get('search_method', 'N/A')}")
            print(f"   PageIndex: {approach_summary.get('pageindex_reasoning', 'N/A')}")
            print(f"   Hybrid Components: {approach_summary.get('hybrid_search_components', [])}")

        best_result = results_data['results'][0]
        print(f"\n🎯 Best Result (Calibrated Confidence: {best_result['confidence_calibration']['calibrated_confidence']:.3f}):")
        print(f"   Status: {best_result['confidence_gate_status']}")
        print(f"   Source: {best_result['metadata'].get('title', 'Unknown')}")
        print(f"   Content Preview: {best_result['content'][:250].strip()}...")

        print(f"\n🧠 deepConf Confidence Breakdown:")
        calib_profile = best_result['confidence_calibration']
        print(f"   Original Confidence: {calib_profile.get('original_confidence', 0):.3f}")
        print(f"   Calibrated Confidence: {calib_profile.get('calibrated_confidence', 0):.3f}")
        print(f"   Uncertainty Estimate: {calib_profile.get('uncertainty_estimate', 0):.3f}")

    print("\n" + "="*60)
    print("✅ COMPLETE 3-APPROACH DEMONSTRATION FINISHED!")
    print(f"📊 Summary: Processed {document_structure['processing_metadata']['total_sections']} sections from '{Path(pdf_path).name}'")
    print(f"🔍 Executed {len(test_queries)} hybrid search queries")
    print(f"🧠 Stored {len(rag_system.confidence_memory)} high-confidence cases in memory")

if __name__ == "__main__":
    main()