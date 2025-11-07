"""
Check C (Conventional) category questions and responses
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

def check_c_questions():
    """Check C category questions"""
    print("🔍 CHECKING C (CONVENTIONAL) CATEGORY QUESTIONS")
    print("="*80)
    
    db = get_db_connection()
    db_service = DatabaseService(db)
    
    # Get framework
    framework_df = db_service.get_framework_df()
    
    # Get C questions
    c_questions = framework_df[framework_df['riasec_code'] == 'C'].sort_values('id')
    
    print(f"\nFound {len(c_questions)} C (Conventional) questions:\n")
    
    # Get responses for both students
    responses1 = db_service.get_student_assessments("HS001")
    responses2 = db_service.get_student_assessments("ST004")
    
    resp1_dict = {r.question_id: r for r in responses1}
    resp2_dict = {r.question_id: r for r in responses2}
    
    for idx, row in c_questions.iterrows():
        qid = row['id']
        question = row['question']
        weight = row['weight']
        
        r1 = resp1_dict.get(qid)
        r2 = resp2_dict.get(qid)
        
        print(f"Question ID {qid} (Weight: {weight}):")
        print(f"  Question: {question[:100]}...")
        print(f"  HS001: {r1.answer if r1 else 'MISSING'}")
        if r1:
            print(f"    Reasoning: {r1.reasoning[:150]}...")
        print(f"  ST004: {r2.answer if r2 else 'MISSING'}")
        if r2:
            print(f"    Reasoning: {r2.reasoning[:150]}...")
        print()

if __name__ == "__main__":
    check_c_questions()

