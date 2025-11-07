"""
Test the adjusted scoring formula to show it prevents scores from being too low
"""
def test_scoring_formula():
    """Compare old vs new formula"""
    
    print("="*80)
    print("ADJUSTED SCORING FORMULA - PREVENTS TOO LOW SCORES")
    print("="*80)
    
    print("\n📊 OLD FORMULA: base_score × confidence")
    print("-"*80)
    print("Problem: Low confidence scores create very low final scores")
    print(f"{'Answer':<10} {'Base':<8} {'Confidence':<12} {'Final (Old)':<15} {'Issue'}")
    print("-"*80)
    
    test_cases = [
        ('Yes', 1.0, 1.0),
        ('Yes', 1.0, 0.8),
        ('Yes', 1.0, 0.6),
        ('Yes', 1.0, 0.4),
        ('Yes', 1.0, 0.2),
        ('Partial', 0.5, 0.8),
        ('Partial', 0.5, 0.6),
        ('Partial', 0.5, 0.4),
        ('Partial', 0.5, 0.2),
    ]
    
    for answer, base, conf in test_cases:
        old_final = base * conf
        issue = "Too low!" if old_final < 0.5 and base == 1.0 else ("OK" if old_final >= 0.3 else "Very low")
        print(f"{answer:<10} {base:<8.1f} {conf:<12.2f} {old_final:<15.2f} {issue}")
    
    print("\n" + "="*80)
    print("📊 NEW FORMULA: base_score × (0.5 + 0.5 × confidence)")
    print("-"*80)
    print("Benefit: Ensures minimum 50% of base score, prevents too low scores")
    print(f"{'Answer':<10} {'Base':<8} {'Confidence':<12} {'Final (New)':<15} {'Improvement'}")
    print("-"*80)
    
    for answer, base, conf in test_cases:
        new_final = base * (0.5 + 0.5 * conf)
        old_final = base * conf
        improvement = new_final - old_final
        print(f"{answer:<10} {base:<8.1f} {conf:<12.2f} {new_final:<15.2f} +{improvement:.2f}")
    
    print("\n" + "="*80)
    print("📈 EXAMPLE: C Category with 7 Questions")
    print("-"*80)
    
    # Simulate a scenario with mixed confidence
    print("\nScenario: All 'Yes' answers with varying confidence:")
    print(f"{'Question':<10} {'Answer':<10} {'Confidence':<12} {'Old Final':<15} {'New Final':<15}")
    print("-"*80)
    
    confidences = [0.9, 0.85, 0.8, 0.75, 0.7, 0.65, 0.6]
    total_weight = 5.9
    
    old_total = 0.0
    new_total = 0.0
    
    for i, conf in enumerate(confidences, 66):
        base = 1.0  # Yes
        old_final = base * conf
        new_final = base * (0.5 + 0.5 * conf)
        weight = 0.9 if i in [66, 67, 69, 72] else (0.8 if i in [68, 70] else 0.7)
        
        old_total += old_final * weight
        new_total += new_final * weight
        
        print(f"Q{i:<9} Yes         {conf:<12.2f} {old_final:<15.2f} {new_final:<15.2f}")
    
    old_score = (old_total / total_weight) * 100
    new_score = (new_total / total_weight) * 100
    
    print("-"*80)
    print(f"{'TOTAL':<10} {'':<10} {'':<12} {old_total:<15.2f} {new_total:<15.2f}")
    print(f"\nOld Score: {old_score:.1f}/100")
    print(f"New Score: {new_score:.1f}/100")
    print(f"Difference: +{new_score - old_score:.1f} points")
    
    print("\n" + "="*80)
    print("💡 KEY BENEFITS")
    print("-"*80)
    print("1. ✅ Prevents scores from being too low (< 30)")
    print("2. ✅ Yes answers always contribute at least 50% (0.5)")
    print("3. ✅ Partial answers contribute 25-50% (0.25-0.5)")
    print("4. ✅ Still allows variation based on confidence")
    print("5. ✅ More realistic score distribution (30-100 instead of 0-100)")

if __name__ == "__main__":
    test_scoring_formula()

