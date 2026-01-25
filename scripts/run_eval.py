import json
import argparse
import time
import asyncio
from pathlib import Path
from datetime import datetime

# Mock Client if fastmcp is missing for demo purposes
try:
    from fastmcp import Client
except ImportError:
    Client = None
    print("Warning: fastmcp not found. Running in simulation mode.")

async def run_pipeline_inference(question: str) -> dict:
    """
    Simulate the pipeline execution for a single question.
    Returns the result and latency.
    """
    start_time = time.time()
    
    # Simulate processing time
    time.sleep(0.1)
    
    # Placeholder result
    result = {
        "answer": "Simulated Answer",
        "citations": ["PROOF_OF_LIFE"], 
        "latency": time.time() - start_time
    }
    return result

def score_result(prediction: dict, ground_truth: dict) -> dict:
    """
    Compare prediction to ground truth.
    """
    # Simple check: is the source file cited?
    cited = False
    if "citations" in prediction:
        # Check if ground truth citation is in prediction citations
        cited = ground_truth["citation"] in prediction["citations"]
        
    return {
        "correct_retrieval": cited,
        "latency": prediction['latency']
    }

async def main():
    parser = argparse.ArgumentParser(description="Run Evaluation on Golden Set")
    parser.add_argument("--golden_set", default="TheVault/data/golden_set.json", help="Path to golden set")
    parser.add_argument("--metrics_out", default="TheVault/data/metrics.json", help="Output metrics file")
    
    args = parser.parse_args()
    
    gs_path = Path(args.golden_set)
    if not gs_path.exists():
        print("Golden set not found.")
        return
        
    with open(gs_path, "r") as f:
        golden_set = json.load(f)
        
    metrics = {
        "timestamp": datetime.now().isoformat(),
        "total_queries": len(golden_set),
        "results": []
    }
    
    print(f"Running evaluation on {len(golden_set)} queries...")
    
    for item in golden_set:
        print(f"Testing: {item['question']}")
        # Run inference
        prediction = await run_pipeline_inference(item['question'])
        
        # Score
        score = score_result(prediction, item)
        
        metrics["results"].append({
            "question": item['question'],
            "score": score
        })
    
    # Calculate aggregate stats
    total_correct = sum(1 for r in metrics["results"] if r["score"]["correct_retrieval"])
    avg_latency = sum(r["score"]["latency"] for r in metrics["results"]) / len(metrics["results"])
    
    metrics["summary"] = {
        "accuracy": total_correct / len(golden_set),
        "avg_latency": avg_latency
    }

    # Save metrics
    with open(args.metrics_out, "w") as f:
        json.dump(metrics, f, indent=2)
        
    print(f"Metrics saved to {args.metrics_out}")
    print(f"Accuracy: {metrics['summary']['accuracy']:.1%}")
    print(f"Avg Latency: {metrics['summary']['avg_latency']:.3f}s")

if __name__ == "__main__":
    asyncio.run(main())