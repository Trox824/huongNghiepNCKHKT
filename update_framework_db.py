"""
Script to update the framework table in PostgreSQL database with Vietnamese questions
"""
import os
import sys

# Add parent directory to path
parent_dir = os.path.dirname(os.path.abspath(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import pandas as pd
from app.config.database import get_db_connection
from app.services.database_service import DatabaseService
from app.database.models import Framework

def update_framework_from_csv(db_service, csv_path: str) -> int:
    """Update existing framework questions from CSV without deleting"""
    # Read CSV
    df = pd.read_csv(csv_path)
    
    # Get existing framework questions ordered by ID
    existing_frameworks = db_service.db.query(Framework).order_by(Framework.id).all()
    
    if len(existing_frameworks) != len(df):
        print(f"⚠️  Warning: CSV has {len(df)} questions but database has {len(existing_frameworks)} questions")
        print("   Updating based on order...")
    
    # Update existing questions
    count = 0
    for idx, row in df.iterrows():
        if idx < len(existing_frameworks):
            # Update existing record
            framework = existing_frameworks[idx]
            framework.riasec_code = row['riasec_code']
            framework.career_category = row['career_category']
            framework.question = row['question']
            framework.key_subjects = row.get('key_subjects', '')
            framework.required_grades = row.get('required_grades', '')
            framework.weight = float(row.get('weight', 1.0))
            framework.description = row.get('description', '')
            count += 1
        else:
            # Add new record if CSV has more questions
            framework = Framework(
                riasec_code=row['riasec_code'],
                career_category=row['career_category'],
                question=row['question'],
                key_subjects=row.get('key_subjects', ''),
                required_grades=row.get('required_grades', ''),
                weight=float(row.get('weight', 1.0)),
                description=row.get('description', '')
            )
            db_service.db.add(framework)
            count += 1
    
    db_service.db.commit()
    return count

def main():
    print("🔄 Updating Framework Table with Vietnamese Questions...")
    print()
    
    try:
        # Get database connection
        print("1️⃣ Connecting to PostgreSQL database...")
        db = get_db_connection()
        db_service = DatabaseService(db)
        print("✅ Connected successfully")
        print()
        
        # Load framework from CSV
        print("2️⃣ Loading Vietnamese framework from CSV...")
        framework_path = os.path.join("asset", "RIASEC_Career_Framework.csv")
        
        if not os.path.exists(framework_path):
            print(f"❌ Framework file not found at: {framework_path}")
            return
        
        # Update existing framework questions
        count = update_framework_from_csv(db_service, framework_path)
        print(f"✅ Successfully updated {count} framework questions in database")
        print()
        
        # Verify the update
        print("3️⃣ Verifying update...")
        framework_df = db_service.get_framework_df()
        if not framework_df.empty:
            print(f"✅ Verified: {len(framework_df)} questions in database")
            print()
            print("Sample questions (Vietnamese):")
            for idx, row in framework_df.head(3).iterrows():
                print(f"  - {row['riasec_code']} ({row['career_category']}): {row['question'][:60]}...")
        else:
            print("⚠️  Warning: Framework table appears to be empty")
        
        print()
        print("✅ Framework update completed successfully!")
        
    except Exception as e:
        print(f"❌ Error updating framework: {e}")
        import traceback
        traceback.print_exc()
        return

if __name__ == "__main__":
    main()
