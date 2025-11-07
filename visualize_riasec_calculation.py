"""
Visual example of RIASEC score calculation
"""
import pandas as pd

def visualize_calculation():
    """Show a step-by-step example of RIASEC score calculation"""
    
    print("="*80)
    print("RIASEC SCORE CALCULATION - VISUAL EXAMPLE")
    print("="*80)
    
    # Example: C (Conventional) category with 7 questions
    print("\n📋 EXAMPLE: C (Conventional) Category")
    print("-"*80)
    
    # Framework questions
    questions = [
        {'id': 66, 'riasec_code': 'C', 'weight': 0.9, 'question': 'Organization and attention to detail'},
        {'id': 67, 'riasec_code': 'C', 'weight': 0.9, 'question': 'Accuracy and precision'},
        {'id': 68, 'riasec_code': 'C', 'weight': 0.8, 'question': 'Structured tasks preference'},
        {'id': 69, 'riasec_code': 'C', 'weight': 0.9, 'question': 'Consistent performance'},
        {'id': 70, 'riasec_code': 'C', 'weight': 0.8, 'question': 'Data management skills'},
        {'id': 71, 'riasec_code': 'C', 'weight': 0.7, 'question': 'Following procedures'},
        {'id': 72, 'riasec_code': 'C', 'weight': 0.9, 'question': 'Working with numbers/data'},
    ]
    
    # Student responses
    responses = [
        {'question_id': 66, 'answer': 'Yes'},
        {'question_id': 67, 'answer': 'Yes'},
        {'question_id': 68, 'answer': 'Yes'},
        {'question_id': 69, 'answer': 'Yes'},
        {'question_id': 70, 'answer': 'Yes'},
        {'question_id': 71, 'answer': 'Yes'},
        {'question_id': 72, 'answer': 'Yes'},
    ]
    
    print("\n1️⃣ STEP 1: Map Answers to Scores")
    print("-"*80)
    print(f"{'Question ID':<12} {'Answer':<10} {'Score Value':<15} {'Weight':<10}")
    print("-"*80)
    
    answer_scores = {'Yes': 1.0, 'Partial': 0.5, 'No': 0.0}
    
    for q in questions:
        resp = next((r for r in responses if r['question_id'] == q['id']), None)
        answer = resp['answer'] if resp else 'No'
        score = answer_scores[answer]
        print(f"Q{q['id']:<11} {answer:<10} {score:<15.1f} {q['weight']:<10.1f}")
    
    print("\n2️⃣ STEP 2: Calculate Weighted Contributions")
    print("-"*80)
    print(f"{'Question ID':<12} {'Answer':<10} {'Score':<10} {'Weight':<10} {'Contribution':<15}")
    print("-"*80)
    
    total_score = 0.0
    total_weight = 0.0
    
    for q in questions:
        resp = next((r for r in responses if r['question_id'] == q['id']), None)
        answer = resp['answer'] if resp else 'No'
        score = answer_scores[answer]
        contribution = score * q['weight']
        total_score += contribution
        total_weight += q['weight']
        
        print(f"Q{q['id']:<11} {answer:<10} {score:<10.1f} {q['weight']:<10.1f} {contribution:<15.2f}")
    
    print("-"*80)
    print(f"{'TOTAL':<32} {total_weight:<10.1f} {total_score:<15.2f}")
    
    print("\n3️⃣ STEP 3: Normalize to 0-100 Scale")
    print("-"*80)
    print(f"Formula: (Total Score / Total Weight) × 100")
    print(f"Calculation: ({total_score:.2f} / {total_weight:.2f}) × 100")
    
    final_score = (total_score / total_weight) * 100
    print(f"Final C Score: {final_score:.2f}")
    
    # Example 2: Mixed answers
    print("\n" + "="*80)
    print("📋 EXAMPLE 2: Mixed Answers (More Realistic)")
    print("-"*80)
    
    responses2 = [
        {'question_id': 66, 'answer': 'Yes'},
        {'question_id': 67, 'answer': 'Partial'},
        {'question_id': 68, 'answer': 'Yes'},
        {'question_id': 69, 'answer': 'Partial'},
        {'question_id': 70, 'answer': 'Yes'},
        {'question_id': 71, 'answer': 'No'},
        {'question_id': 72, 'answer': 'Yes'},
    ]
    
    print("\n2️⃣ STEP 2: Calculate Weighted Contributions (Mixed Answers)")
    print("-"*80)
    print(f"{'Question ID':<12} {'Answer':<10} {'Score':<10} {'Weight':<10} {'Contribution':<15}")
    print("-"*80)
    
    total_score2 = 0.0
    total_weight2 = 0.0
    
    for q in questions:
        resp = next((r for r in responses2 if r['question_id'] == q['id']), None)
        answer = resp['answer'] if resp else 'No'
        score = answer_scores[answer]
        contribution = score * q['weight']
        total_score2 += contribution
        total_weight2 += q['weight']
        
        print(f"Q{q['id']:<11} {answer:<10} {score:<10.1f} {q['weight']:<10.1f} {contribution:<15.2f}")
    
    print("-"*80)
    print(f"{'TOTAL':<32} {total_weight2:<10.1f} {total_score2:<15.2f}")
    
    final_score2 = (total_score2 / total_weight2) * 100
    print(f"\nFinal C Score: {final_score2:.2f}")
    
    print("\n" + "="*80)
    print("📊 COMPARISON")
    print("-"*80)
    print(f"All 'Yes' answers:     {final_score:.2f} (Perfect match)")
    print(f"Mixed answers:          {final_score2:.2f} (Moderate match)")
    print(f"Difference:             {final_score - final_score2:.2f} points")
    
    print("\n" + "="*80)
    print("💡 KEY INSIGHTS")
    print("-"*80)
    print("1. Each question contributes proportionally to its weight")
    print("2. 'Partial' answers give 50% credit (0.5 × weight)")
    print("3. 'No' answers give 0% credit (0.0 × weight)")
    print("4. Final score is normalized to 0-100 for easy comparison")
    print("5. Higher weights = more important questions")

if __name__ == "__main__":
    visualize_calculation()

