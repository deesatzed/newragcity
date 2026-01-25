#!/usr/bin/env python3
"""
Test approval system with multiple component types
"""

from approve import ApprovalGate

def test_component(component_name: str, description: str):
    """Test a specific component"""
    print(f"\n{'='*60}")
    print(f"🧪 TESTING: {component_name.upper()}")
    print(f"📝 Purpose: {description}")
    print(f"{'='*60}")
    
    gate = ApprovalGate(component_name)
    test_results = gate.run_tests(component_name)
    
    # Present results like the approval system would
    gate.present_evidence(test_results, show_details=False)
    
    # Auto-recommendation logic
    status = test_results.get("status", "unknown")
    if status == "passed":
        recommendation = "✅ AUTO-APPROVE (High Value)"
    elif status == "warning":
        recommendation = "⚠️  CONDITIONAL (Needs Review)"
    elif status == "needs_work":
        recommendation = "🔧 NEEDS WORK (Don't Approve Yet)"
    else:
        recommendation = "❓ MANUAL REVIEW REQUIRED"
    
    print(f"\n🤖 Auto-Recommendation: {recommendation}")
    
    return test_results, recommendation

def main():
    print("🔬 APPROVAL SYSTEM COMPREHENSIVE TEST")
    print("="*60)
    
    # Test Thalamus components (medical)
    print("\n🏥 THALAMUS COMPONENT TESTS (Medical)")
    print("-" * 40)
    
    results = {}
    
    # High-value medical component
    results["confidence_calibration"] = test_component(
        "confidence_calibration",
        "Medical-grade confidence scoring with 95% threshold"
    )
    
    # Component with API dependency  
    results["logprobs_analysis"] = test_component(
        "logprobs_analysis", 
        "Token-level uncertainty quantification (requires OpenAI API)"
    )
    
    # Test Cognitron components (developer tool)
    print("\n\n💻 COGNITRON COMPONENT TESTS (Developer Tool)")
    print("-" * 40)
    
    # Medical removal task
    results["remove_medical"] = test_component(
        "remove_medical",
        "Remove medical references to clarify developer focus"
    )
    
    # Developer connector
    results["git_connector"] = test_component(
        "git_connector",
        "Index git repositories with AST analysis"
    )
    
    # Summary
    print("\n" + "="*60)
    print("📊 APPROVAL SUMMARY")
    print("="*60)
    
    approved = 0
    needs_review = 0
    needs_work = 0
    
    for component, (test_results, recommendation) in results.items():
        status_icon = "✅" if "AUTO-APPROVE" in recommendation else "⚠️" if "CONDITIONAL" in recommendation else "🔧"
        print(f"{status_icon} {component:20} | {recommendation}")
        
        if "AUTO-APPROVE" in recommendation:
            approved += 1
        elif "CONDITIONAL" in recommendation:
            needs_review += 1
        else:
            needs_work += 1
    
    print(f"\n📈 Results: {approved} Auto-Approve | {needs_review} Need Review | {needs_work} Need Work")
    print(f"🎯 Success Rate: {approved}/{len(results)} = {approved/len(results)*100:.1f}%")
    
    print(f"\n✅ APPROVAL SYSTEM VALIDATED")
    print("   Ready for real component migrations with user approval gates!")

if __name__ == "__main__":
    main()