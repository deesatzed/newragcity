#!/usr/bin/env python3
"""
Test the approval system non-interactively
"""

from approve import ApprovalGate

def test_approval_system():
    """Test approval system with sample component"""
    
    print("🧪 TESTING APPROVAL SYSTEM")
    print("="*50)
    
    # Test confidence calibration component
    gate = ApprovalGate("confidence_calibration")
    test_results = gate.run_tests("confidence_calibration")
    
    print("📊 TEST RESULTS:")
    for key, value in test_results.items():
        print(f"   {key}: {value}")
    
    print("\n" + "="*50)
    print("APPROVAL ANALYSIS:")
    print("="*50)
    
    # Analyze results
    status = test_results.get("status")
    accuracy = test_results.get("accuracy", 0)
    
    if status == "passed" and accuracy > 95:
        recommendation = "RECOMMEND APPROVAL"
        reason = f"High accuracy ({accuracy}%) and all tests passed"
    elif status == "warning":
        recommendation = "CONDITIONAL APPROVAL"
        reason = "Some concerns but may be acceptable"
    else:
        recommendation = "RECOMMEND REJECTION" 
        reason = "Does not meet criteria"
    
    print(f"✅ Recommendation: {recommendation}")
    print(f"📝 Reason: {reason}")
    print(f"💰 Value: {test_results.get('value_delivered')}")
    
    # Show what would happen with each decision
    print("\n" + "="*50)
    print("DECISION OUTCOMES:")
    print("="*50)
    print("If 'yes'  → Component moves to Thalamus with medical-grade confidence")
    print("If 'no'   → Component stays in Cognitron, medical features removed")  
    print("If 'test' → More validation needed before decision")
    
    return test_results, recommendation

if __name__ == "__main__":
    test_approval_system()