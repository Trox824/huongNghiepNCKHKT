"""
Visualize how continuous confidence-based scoring creates more variation
"""
import numpy as np

def visualize_continuous_scoring():
    """Show how confidence scores create continuous variation"""
    
    print("="*80)
    print("CONTINUOUS SCORING SYSTEM - VARIATION COMPARISON")
    print("="*80)
    
    # Old system: Discrete scores
    print("\n📊 OLD SYSTEM: Discrete Scores (Yes=1.0, Partial=0.5, No=0.0)")
    print("-"*80)
    print("Possible scores for a category with 7 questions:")
    print("  - All Yes:    100.00")
    print("  - 6 Yes, 1 Partial:  92.86")
    print("  - 5 Yes, 2 Partial:  85.71")
    print("  - 4 Yes, 3 Partial:  78.57")
    print("  - All Partial: 50.00")
    print("  - 3 Partial, 4 No:   21.43")
    print("  - All No:     0.00")
    print("\n⚠️  Limited variation - only ~7-8 possible score values!")
    
    # New system: Continuous scores with confidence
    print("\n" + "="*80)
    print("📊 NEW SYSTEM: Continuous Scores with Confidence")
    print("-"*80)
    
    # Example: C category with 7 questions
    questions = [
        {'id': 66, 'weight': 0.9},
        {'id': 67, 'weight': 0.9},
        {'id': 68, 'weight': 0.8},
        {'id': 69, 'weight': 0.9},
        {'id': 70, 'weight': 0.8},
        {'id': 71, 'weight': 0.7},
        {'id': 72, 'weight': 0.9},
    ]
    
    total_weight = sum(q['weight'] for q in questions)
    
    print(f"\nExample: C (Conventional) Category - 7 questions, total weight: {total_weight}")
    print("\n" + "-"*80)
    print("SCENARIO 1: All 'Yes' with varying confidence")
    print("-"*80)
    
    scenarios = [
        {
            'name': 'Very Strong Evidence',
            'answers': [
                {'answer': 'Yes', 'confidence': 0.95},
                {'answer': 'Yes', 'confidence': 0.92},
                {'answer': 'Yes', 'confidence': 0.90},
                {'answer': 'Yes', 'confidence': 0.88},
                {'answer': 'Yes', 'confidence': 0.93},
                {'answer': 'Yes', 'confidence': 0.91},
                {'answer': 'Yes', 'confidence': 0.94},
            ]
        },
        {
            'name': 'Strong Evidence',
            'answers': [
                {'answer': 'Yes', 'confidence': 0.85},
                {'answer': 'Yes', 'confidence': 0.82},
                {'answer': 'Yes', 'confidence': 0.80},
                {'answer': 'Yes', 'confidence': 0.78},
                {'answer': 'Yes', 'confidence': 0.83},
                {'answer': 'Yes', 'confidence': 0.81},
                {'answer': 'Yes', 'confidence': 0.84},
            ]
        },
        {
            'name': 'Moderate Evidence',
            'answers': [
                {'answer': 'Yes', 'confidence': 0.75},
                {'answer': 'Yes', 'confidence': 0.72},
                {'answer': 'Yes', 'confidence': 0.70},
                {'answer': 'Yes', 'confidence': 0.68},
                {'answer': 'Yes', 'confidence': 0.73},
                {'answer': 'Yes', 'confidence': 0.71},
                {'answer': 'Yes', 'confidence': 0.74},
            ]
        },
        {
            'name': 'Mixed Evidence (Some Partial)',
            'answers': [
                {'answer': 'Yes', 'confidence': 0.85},
                {'answer': 'Partial', 'confidence': 0.80},
                {'answer': 'Yes', 'confidence': 0.75},
                {'answer': 'Partial', 'confidence': 0.70},
                {'answer': 'Yes', 'confidence': 0.80},
                {'answer': 'Partial', 'confidence': 0.65},
                {'answer': 'Yes', 'confidence': 0.78},
            ]
        },
    ]
    
    for scenario in scenarios:
        total_score = 0.0
        print(f"\n{scenario['name']}:")
        print(f"  {'Question':<10} {'Answer':<10} {'Confidence':<12} {'Base':<8} {'Final':<10} {'Weight':<8} {'Contribution':<15}")
        print("  " + "-"*75)
        
        for i, q in enumerate(questions):
            ans = scenario['answers'][i]
            base = 1.0 if ans['answer'] == 'Yes' else (0.5 if ans['answer'] == 'Partial' else 0.0)
            final = base * ans['confidence']
            contribution = final * q['weight']
            total_score += contribution
            
            print(f"  Q{q['id']:<9} {ans['answer']:<10} {ans['confidence']:<12.2f} {base:<8.1f} {final:<10.2f} {q['weight']:<8.1f} {contribution:<15.2f}")
        
        final_score = (total_score / total_weight) * 100
        print(f"  {'TOTAL':<10} {'':<10} {'':<12} {'':<8} {'':<10} {total_weight:<8.1f} {total_score:<15.2f}")
        print(f"  Final C Score: {final_score:.2f}")
    
    print("\n" + "="*80)
    print("📈 COMPARISON: Old vs New System")
    print("-"*80)
    
    print("\nOld System (Discrete):")
    print("  - All Yes: 100.00")
    print("  - 6 Yes, 1 Partial: 92.86")
    print("  - 5 Yes, 2 Partial: 85.71")
    print("  - All Partial: 50.00")
    print("  → Only ~7-8 possible values")
    
    print("\nNew System (Continuous):")
    print("  - Very Strong Evidence: ~92-95")
    print("  - Strong Evidence: ~82-85")
    print("  - Moderate Evidence: ~72-75")
    print("  - Mixed Evidence: ~65-75")
    print("  → Continuous range from 0-100 with fine-grained variation")
    
    print("\n" + "="*80)
    print("💡 KEY BENEFITS")
    print("-"*80)
    print("1. ✅ More granular differentiation between students")
    print("2. ✅ Reflects strength of evidence, not just binary Yes/No")
    print("3. ✅ Better handles edge cases (strong vs weak 'Yes')")
    print("4. ✅ Reduces clustering at 0, 50, 100")
    print("5. ✅ More accurate representation of student profiles")
    
    print("\n" + "="*80)
    print("📐 FORMULA")
    print("-"*80)
    print("Final Score = Base Score × Confidence Score")
    print("  - Yes: Base = 1.0 → Final = 1.0 × confidence (0.0-1.0)")
    print("  - Partial: Base = 0.5 → Final = 0.5 × confidence (0.0-0.5)")
    print("  - No: Base = 0.0 → Final = 0.0 (always)")
    print("\nCategory Score = (Sum of Contributions / Total Weight) × 100")

if __name__ == "__main__":
    visualize_continuous_scoring()

