"""
Compare grade trends between two students to understand why they have similar C scores
"""
import os
import sys
import pandas as pd
import numpy as np

# Add parent directory to path
parent_dir = os.path.dirname(os.path.abspath(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from app.config.database import get_db_connection
from app.services.database_service import DatabaseService

def analyze_grade_trends():
    """Analyze and compare grade trends"""
    print("📊 COMPARING GRADE TRENDS: HS001 vs ST004")
    print("="*80)
    
    db = get_db_connection()
    db_service = DatabaseService(db)
    
    # Get grades for both students
    grades1_df = db_service.get_student_grades_df("HS001")
    grades2_df = db_service.get_student_grades_df("ST004")
    
    # Calculate average scores by subject
    print("\n📈 AVERAGE SCORES BY SUBJECT:")
    print("-"*80)
    
    # HS001 averages
    if not grades1_df.empty:
        hs001_avg = grades1_df.groupby('subject')['score'].mean().sort_values(ascending=False)
        print(f"\nHS001 (Nguyễn Văn An) - Average Scores:")
        for subject, avg_score in hs001_avg.items():
            count = len(grades1_df[grades1_df['subject'] == subject])
            print(f"  {subject:20s}: {avg_score:5.2f} (from {count} records)")
    
    # ST004 averages
    if not grades2_df.empty:
        st004_avg = grades2_df.groupby('subject')['score'].mean().sort_values(ascending=False)
        print(f"\nST004 (Nguyễn Tuấn Bách) - Average Scores:")
        for subject, avg_score in st004_avg.items():
            count = len(grades2_df[grades2_df['subject'] == subject])
            print(f"  {subject:20s}: {avg_score:5.2f} (from {count} records)")
    
    # Compare key subjects for C category
    print(f"\n{'='*80}")
    print("KEY SUBJECTS FOR C (CONVENTIONAL) CATEGORY:")
    print(f"{'='*80}")
    
    key_subjects_c = ['Toán', 'toán', 'Tin học', 'tin học', 'Công nghệ', 'công nghệ', 
                      'Hóa học', 'hoá học', 'Vật lý', 'vật lý', 'vật lí']
    
    print(f"\n{'Subject':<20} {'HS001 Avg':<15} {'ST004 Avg':<15} {'Difference':<15}")
    print("-"*80)
    
    all_subjects = set()
    if not grades1_df.empty:
        all_subjects.update(grades1_df['subject'].unique())
    if not grades2_df.empty:
        all_subjects.update(grades2_df['subject'].unique())
    
    for subject in sorted(all_subjects):
        # Check if this is a key subject for C
        is_key = any(key in subject for key in key_subjects_c)
        
        avg1 = grades1_df[grades1_df['subject'] == subject]['score'].mean() if not grades1_df.empty else None
        avg2 = grades2_df[grades2_df['subject'] == subject]['score'].mean() if not grades2_df.empty else None
        
        if avg1 is not None or avg2 is not None:
            marker = "⭐" if is_key else "  "
            avg1_str = f"{avg1:.2f}" if avg1 is not None else "N/A"
            avg2_str = f"{avg2:.2f}" if avg2 is not None else "N/A"
            diff = abs(avg1 - avg2) if (avg1 is not None and avg2 is not None) else None
            diff_str = f"{diff:.2f}" if diff is not None else "N/A"
            
            print(f"{marker} {subject:<18} {avg1_str:<15} {avg2_str:<15} {diff_str:<15}")
    
    # Analyze grade trends over time
    print(f"\n{'='*80}")
    print("GRADE TRENDS OVER TIME (Key Subjects):")
    print(f"{'='*80}")
    
    key_subjects = ['Toán', 'toán', 'Tin học', 'tin học']
    
    for subject_key in key_subjects:
        # Find matching subjects
        subjects1 = [s for s in grades1_df['subject'].unique() if subject_key.lower() in s.lower()] if not grades1_df.empty else []
        subjects2 = [s for s in grades2_df['subject'].unique() if subject_key.lower() in s.lower()] if not grades2_df.empty else []
        
        if subjects1 or subjects2:
            print(f"\n{subject_key.upper()}:")
            
            # HS001 trend
            if subjects1:
                for subj in subjects1:
                    subj_grades = grades1_df[grades1_df['subject'] == subj].sort_values('grade_level')
                    if not subj_grades.empty:
                        trend = subj_grades.groupby('grade_level')['score'].mean()
                        print(f"  HS001 ({subj}): {dict(trend)}")
                        print(f"    Trend: {'↑ Improving' if trend.iloc[-1] > trend.iloc[0] else '↓ Declining' if trend.iloc[-1] < trend.iloc[0] else '→ Stable'}")
            
            # ST004 trend
            if subjects2:
                for subj in subjects2:
                    subj_grades = grades2_df[grades2_df['subject'] == subj].sort_values('grade_level')
                    if not subj_grades.empty:
                        trend = subj_grades.groupby('grade_level')['score'].mean()
                        print(f"  ST004 ({subj}): {dict(trend)}")
                        print(f"    Trend: {'↑ Improving' if trend.iloc[-1] > trend.iloc[0] else '↓ Declining' if trend.iloc[-1] < trend.iloc[0] else '→ Stable'}")
    
    # Overall statistics
    print(f"\n{'='*80}")
    print("OVERALL STATISTICS:")
    print(f"{'='*80}")
    
    if not grades1_df.empty:
        print(f"\nHS001:")
        print(f"  Total grade records: {len(grades1_df)}")
        print(f"  Overall average: {grades1_df['score'].mean():.2f}")
        print(f"  Grade range: {grades1_df['score'].min():.2f} - {grades1_df['score'].max():.2f}")
        print(f"  Standard deviation: {grades1_df['score'].std():.2f}")
        print(f"  Consistency (lower std = more consistent): {grades1_df['score'].std():.2f}")
    
    if not grades2_df.empty:
        print(f"\nST004:")
        print(f"  Total grade records: {len(grades2_df)}")
        print(f"  Overall average: {grades2_df['score'].mean():.2f}")
        print(f"  Grade range: {grades2_df['score'].min():.2f} - {grades2_df['score'].max():.2f}")
        print(f"  Standard deviation: {grades2_df['score'].std():.2f}")
        print(f"  Consistency (lower std = more consistent): {grades2_df['score'].std():.2f}")
    
    # Check if both students meet C category requirements
    print(f"\n{'='*80}")
    print("C (CONVENTIONAL) CATEGORY REQUIREMENTS CHECK:")
    print(f"{'='*80}")
    
    c_requirements = {
        'Math': {'threshold': 7.5, 'subjects': ['Toán', 'toán']},
        'All': {'threshold': 7.0, 'subjects': 'all'},
        'Chemistry': {'threshold': 7.5, 'subjects': ['Hóa học', 'hoá học']}
    }
    
    print("\nC Questions check if students:")
    print("1. Have good math scores (>= 7.5)")
    print("2. Show consistency across all subjects (>= 7.0-7.5)")
    print("3. Excel in structured subjects")
    
    # Check math scores
    math_subjects1 = [s for s in grades1_df['subject'].unique() if 'toán' in s.lower() or 'math' in s.lower()] if not grades1_df.empty else []
    math_subjects2 = [s for s in grades2_df['subject'].unique() if 'toán' in s.lower() or 'math' in s.lower()] if not grades2_df.empty else []
    
    if math_subjects1:
        math_avg1 = grades1_df[grades1_df['subject'].isin(math_subjects1)]['score'].mean()
        print(f"\nHS001 Math average: {math_avg1:.2f} {'✓ Meets threshold' if math_avg1 >= 7.5 else '✗ Below threshold'}")
    
    if math_subjects2:
        math_avg2 = grades2_df[grades2_df['subject'].isin(math_subjects2)]['score'].mean()
        print(f"ST004 Math average: {math_avg2:.2f} {'✓ Meets threshold' if math_avg2 >= 7.5 else '✗ Below threshold'}")
    
    # Overall consistency
    if not grades1_df.empty:
        overall_avg1 = grades1_df['score'].mean()
        print(f"\nHS001 Overall average: {overall_avg1:.2f} {'✓ Meets threshold' if overall_avg1 >= 7.5 else '✗ Below threshold'}")
    
    if not grades2_df.empty:
        overall_avg2 = grades2_df['score'].mean()
        print(f"ST004 Overall average: {overall_avg2:.2f} {'✓ Meets threshold' if overall_avg2 >= 7.5 else '✗ Below threshold'}")

if __name__ == "__main__":
    analyze_grade_trends()

