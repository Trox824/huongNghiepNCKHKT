"""
Debug why RIASEC scores are appearing too low
"""
import os
import sys

# Add parent directory to path
parent_dir = os.path.dirname(os.path.abspath(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from app.config.database import get_db_connection
from app.services.database_service import DatabaseService
import pandas as pd

def debug_low_scores():
    """Debug why scores are low"""
    print("🔍 DEBUGGING LOW RIASEC SCORES")
    print("="*80)
    
    db = get_db_connection()
    db_service = DatabaseService(db)
    
    # Get a student with low scores (you can change this ID)
    student_id = "HS001"  # Change to the student ID you're seeing
    
    # Get assessment responses
    responses = db_service.get_student_assessments(student_id)
    print(f"\nFound {len(responses)} assessment responses for {student_id}")
    
    if not responses:
        print("⚠️  No responses found!")
        return
    
    # Get framework
    framework_df = db_service.get_framework_df()
    
    # Analyze responses
    print("\n📊 RESPONSE ANALYSIS:")
    print("-"*80)
    
    answer_counts = {'Yes': 0, 'Partial': 0, 'No': 0, 'Error': 0}
    confidence_scores = []
    
    for resp in responses:
        answer_counts[resp.answer] = answer_counts.get(resp.answer, 0) + 1
        # Check if confidence_score is stored (might not be in old data)
        if hasattr(resp, 'confidence_score'):
            confidence_scores.append(resp.confidence_score)
    
    print(f"Answer distribution:")
    for answer, count in answer_counts.items():
        print(f"  {answer}: {count}")
    
    if confidence_scores:
        print(f"\nConfidence scores: {len(confidence_scores)} found")
        print(f"  Average: {sum(confidence_scores)/len(confidence_scores):.2f}")
        print(f"  Min: {min(confidence_scores):.2f}")
        print(f"  Max: {max(confidence_scores):.2f}")
    else:
        print("\n⚠️  No confidence scores found in database (using default 0.8)")
    
    # Calculate scores manually to see what's happening
    print("\n" + "="*80)
    print("MANUAL SCORE CALCULATION:")
    print("="*80)
    
    riasec_scores = {'R': 0.0, 'I': 0.0, 'A': 0.0, 'S': 0.0, 'E': 0.0, 'C': 0.0}
    riasec_weights = {code: 0.0 for code in riasec_scores.keys()}
    riasec_details = {code: [] for code in riasec_scores.keys()}
    
    for resp in responses:
        question_row = framework_df[framework_df['id'] == resp.question_id]
        if question_row.empty:
            continue
        
        question = question_row.iloc[0]
        riasec_code = question['riasec_code']
        weight = float(question['weight'])
        
        # Get base score
        if resp.answer == 'Yes':
            base_score = 1.0
        elif resp.answer == 'Partial':
            base_score = 0.5
        else:
            base_score = 0.0
        
        # Get confidence (default 0.8 if not stored)
        confidence = 0.8  # Default
        if hasattr(resp, 'confidence_score') and resp.confidence_score:
            confidence = resp.confidence_score
        
        # Calculate final score
        if base_score > 0:
            final_score = base_score * confidence
        else:
            final_score = 0.0
        
        contribution = final_score * weight
        
        riasec_scores[riasec_code] += contribution
        riasec_weights[riasec_code] += weight
        
        riasec_details[riasec_code].append({
            'question_id': resp.question_id,
            'answer': resp.answer,
            'base': base_score,
            'confidence': confidence,
            'final': final_score,
            'weight': weight,
            'contribution': contribution
        })
    
    # Normalize
    print("\n📈 CALCULATED SCORES:")
    print("-"*80)
    print(f"{'Code':<5} {'Total Contrib':<15} {'Total Weight':<15} {'Score':<10} {'Details'}")
    print("-"*80)
    
    for code in ['R', 'I', 'A', 'S', 'E', 'C']:
        if riasec_weights[code] > 0:
            score = (riasec_scores[code] / riasec_weights[code]) * 100
            details = riasec_details[code]
            yes_count = sum(1 for d in details if d['answer'] == 'Yes')
            partial_count = sum(1 for d in details if d['answer'] == 'Partial')
            no_count = sum(1 for d in details if d['answer'] == 'No')
            
            print(f"{code:<5} {riasec_scores[code]:<15.2f} {riasec_weights[code]:<15.2f} {score:<10.2f} "
                  f"({yes_count}Y, {partial_count}P, {no_count}N)")
            
            # Show details for low scores
            if score < 30:
                print(f"      Low score breakdown:")
                for d in details[:3]:  # Show first 3
                    print(f"        Q{d['question_id']}: {d['answer']} "
                          f"(base={d['base']:.1f}, conf={d['confidence']:.2f}, "
                          f"final={d['final']:.2f}, contrib={d['contribution']:.2f})")
        else:
            print(f"{code:<5} {'N/A':<15} {'N/A':<15} {'0.00':<10} (No questions)")
    
    print("\n" + "="*80)
    print("💡 DIAGNOSIS:")
    print("-"*80)
    
    # Check if scores are abnormally low
    max_score = max((riasec_scores[code] / riasec_weights[code] * 100) 
                    for code in riasec_scores.keys() if riasec_weights[code] > 0)
    
    if max_score < 30:
        print("⚠️  Scores are very low (< 30). Possible causes:")
        print("  1. Many 'No' or 'Partial' answers")
        print("  2. Low confidence scores (< 0.5)")
        print("  3. Calculation bug")
        print("  4. Student genuinely has low scores")
        
        # Check answer distribution
        total_yes = sum(answer_counts.get('Yes', 0))
        total_partial = sum(answer_counts.get('Partial', 0))
        total_no = sum(answer_counts.get('No', 0))
        
        if total_yes + total_partial < total_no:
            print(f"\n  → Issue: Too many 'No' answers ({total_no} vs {total_yes + total_partial} Yes/Partial)")
        elif total_partial > total_yes:
            print(f"\n  → Issue: Too many 'Partial' answers ({total_partial} vs {total_yes} Yes)")
        elif confidence_scores and sum(confidence_scores)/len(confidence_scores) < 0.5:
            print(f"\n  → Issue: Confidence scores too low (avg: {sum(confidence_scores)/len(confidence_scores):.2f})")
    else:
        print("✅ Scores appear normal")

if __name__ == "__main__":
    debug_low_scores()

