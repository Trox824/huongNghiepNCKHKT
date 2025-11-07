"""
Debug script to analyze RIASEC scores for two students
"""
import os
import sys
import pandas as pd

# Add parent directory to path
parent_dir = os.path.dirname(os.path.abspath(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from app.config.database import get_db_connection
from app.services.database_service import DatabaseService
from app.services.career_service import CareerAssessmentService

def analyze_student_scores(student_id: str, student_name: str, db_service: DatabaseService):
    """Analyze RIASEC scores for a student"""
    print(f"\n{'='*80}")
    print(f"ANALYZING: {student_name} (ID: {student_id})")
    print(f"{'='*80}")
    
    # Get assessment responses
    responses = db_service.get_student_assessments(student_id)
    print(f"\nTotal assessment responses: {len(responses)}")
    
    if not responses:
        print("⚠️  No assessment responses found!")
        return None
    
    # Get framework
    framework_df = db_service.get_framework_df()
    print(f"Framework questions: {len(framework_df)}")
    
    # Convert responses to dict format
    assessment_responses = []
    for resp in responses:
        assessment_responses.append({
            'question_id': resp.question_id,
            'answer': resp.answer,
            'reasoning': resp.reasoning
        })
    
    # Calculate scores manually
    riasec_scores = {
        'R': 0.0, 'I': 0.0, 'A': 0.0, 'S': 0.0, 'E': 0.0, 'C': 0.0
    }
    riasec_weights = {code: 0.0 for code in riasec_scores.keys()}
    riasec_counts = {code: {'Yes': 0, 'Partial': 0, 'No': 0} for code in riasec_scores.keys()}
    
    # Calculate weighted scores
    for response in assessment_responses:
        # Find corresponding question
        question_row = framework_df[framework_df['id'] == response['question_id']]
        if question_row.empty:
            print(f"⚠️  Warning: Question ID {response['question_id']} not found in framework!")
            continue
        
        question = question_row.iloc[0]
        riasec_code = question['riasec_code']
        weight = float(question['weight'])
        
        # Calculate score contribution
        if response['answer'] == 'Yes':
            score = 1.0
            riasec_counts[riasec_code]['Yes'] += 1
        elif response['answer'] == 'Partial':
            score = 0.5
            riasec_counts[riasec_code]['Partial'] += 1
        else:  # No or Error
            score = 0.0
            riasec_counts[riasec_code]['No'] += 1
        
        riasec_scores[riasec_code] += score * weight
        riasec_weights[riasec_code] += weight
    
    # Normalize scores
    for code in riasec_scores.keys():
        if riasec_weights[code] > 0:
            riasec_scores[code] = (riasec_scores[code] / riasec_weights[code]) * 100
    
    # Print detailed breakdown
    print(f"\n{'RIASEC Score Breakdown':^80}")
    print(f"{'-'*80}")
    print(f"{'Code':<10} {'Score':<15} {'Weight':<15} {'Yes':<10} {'Partial':<10} {'No':<10}")
    print(f"{'-'*80}")
    
    for code in ['R', 'I', 'A', 'S', 'E', 'C']:
        print(f"{code:<10} {riasec_scores[code]:<15.2f} {riasec_weights[code]:<15.2f} "
              f"{riasec_counts[code]['Yes']:<10} {riasec_counts[code]['Partial']:<10} {riasec_counts[code]['No']:<10}")
    
    # Get top 3 codes
    sorted_scores = sorted(riasec_scores.items(), key=lambda x: x[1], reverse=True)
    top_3 = "".join([code for code, _ in sorted_scores[:3]])
    
    print(f"\nTop 3 RIASEC Profile: {top_3}")
    print(f"\nSorted Scores:")
    for code, score in sorted_scores:
        print(f"  {code}: {score:.2f}")
    
    return {
        'scores': riasec_scores,
        'weights': riasec_weights,
        'counts': riasec_counts,
        'profile': top_3
    }

def main():
    print("🔍 DEBUGGING RIASEC SCORES")
    print("="*80)
    
    try:
        # Connect to database
        db = get_db_connection()
        db_service = DatabaseService(db)
        
        # Analyze both students
        student1_id = "HS001"
        student1_name = "Nguyễn Văn An"
        
        student2_id = "ST004"
        student2_name = "Nguyễn Tuấn Bách"
        
        result1 = analyze_student_scores(student1_id, student1_name, db_service)
        result2 = analyze_student_scores(student2_id, student2_name, db_service)
        
        # Compare results
        if result1 and result2:
            print(f"\n{'='*80}")
            print("COMPARISON")
            print(f"{'='*80}")
            print(f"\n{'Code':<10} {'HS001 Score':<20} {'ST004 Score':<20} {'Difference':<15}")
            print(f"{'-'*80}")
            
            for code in ['R', 'I', 'A', 'S', 'E', 'C']:
                score1 = result1['scores'][code]
                score2 = result2['scores'][code]
                diff = abs(score1 - score2)
                print(f"{code:<10} {score1:<20.2f} {score2:<20.2f} {diff:<15.2f}")
            
            print(f"\nHS001 Profile: {result1['profile']}")
            print(f"ST004 Profile: {result2['profile']}")
            
            if result1['profile'] == result2['profile']:
                print("\n⚠️  WARNING: Both students have the same RIASEC profile!")
            else:
                print(f"\n✅ Students have different profiles")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

