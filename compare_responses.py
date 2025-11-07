"""
Compare assessment responses between two students to find discrepancies
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

def compare_responses():
    """Compare responses between two students"""
    print("🔍 COMPARING ASSESSMENT RESPONSES")
    print("="*80)
    
    db = get_db_connection()
    db_service = DatabaseService(db)
    
    # Get responses for both students
    responses1 = db_service.get_student_assessments("HS001")
    responses2 = db_service.get_student_assessments("ST004")
    
    # Get framework
    framework_df = db_service.get_framework_df()
    
    # Create dictionaries by question_id
    resp1_dict = {r.question_id: r for r in responses1}
    resp2_dict = {r.question_id: r for r in responses2}
    
    print(f"\nHS001 has {len(responses1)} responses")
    print(f"ST004 has {len(responses2)} responses")
    
    # Compare responses for each question
    print(f"\n{'Question ID':<15} {'RIASEC':<10} {'HS001 Answer':<15} {'ST004 Answer':<15} {'Match':<10}")
    print("-"*80)
    
    all_question_ids = set(resp1_dict.keys()) | set(resp2_dict.keys())
    matches = 0
    mismatches = 0
    
    for qid in sorted(all_question_ids):
        r1 = resp1_dict.get(qid)
        r2 = resp2_dict.get(qid)
        
        # Get RIASEC code
        question_row = framework_df[framework_df['id'] == qid]
        riasec_code = question_row.iloc[0]['riasec_code'] if not question_row.empty else '?'
        
        answer1 = r1.answer if r1 else "MISSING"
        answer2 = r2.answer if r2 else "MISSING"
        match = "✓" if answer1 == answer2 else "✗"
        
        if answer1 == answer2:
            matches += 1
        else:
            mismatches += 1
        
        print(f"{qid:<15} {riasec_code:<10} {answer1:<15} {answer2:<15} {match:<10}")
    
    print(f"\nMatches: {matches}, Mismatches: {mismatches}")
    
    # Check for questions with same answers but different RIASEC codes
    print(f"\n{'='*80}")
    print("ANALYZING BY RIASEC CODE")
    print(f"{'='*80}")
    
    for code in ['R', 'I', 'A', 'S', 'E', 'C']:
        questions = framework_df[framework_df['riasec_code'] == code]
        print(f"\n{code} ({len(questions)} questions):")
        
        yes1 = sum(1 for qid in questions['id'] if resp1_dict.get(qid) and resp1_dict[qid].answer == 'Yes')
        partial1 = sum(1 for qid in questions['id'] if resp1_dict.get(qid) and resp1_dict[qid].answer == 'Partial')
        no1 = sum(1 for qid in questions['id'] if resp1_dict.get(qid) and resp1_dict[qid].answer == 'No')
        
        yes2 = sum(1 for qid in questions['id'] if resp2_dict.get(qid) and resp2_dict[qid].answer == 'Yes')
        partial2 = sum(1 for qid in questions['id'] if resp2_dict.get(qid) and resp2_dict[qid].answer == 'Partial')
        no2 = sum(1 for qid in questions['id'] if resp2_dict.get(qid) and resp2_dict[qid].answer == 'No')
        
        print(f"  HS001: Yes={yes1}, Partial={partial1}, No={no1}")
        print(f"  ST004: Yes={yes2}, Partial={partial2}, No={no2}")

if __name__ == "__main__":
    compare_responses()

