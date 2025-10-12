"""
Database initialization script
Run this to create all database tables and load the RIASEC framework
"""
import os
from app.config.database import init_database, get_db_connection
from app.services.database_service import DatabaseService

def main():
    print("🚀 Initializing Student Career Guidance System Database...")
    print()
    
    # Initialize database tables
    print("1️⃣ Creating database tables...")
    try:
        init_database()
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return
    
    print()
    
    # Load RIASEC framework
    print("2️⃣ Loading RIASEC Career Framework...")
    try:
        db = get_db_connection()
        db_service = DatabaseService(db)
        
        framework_path = os.path.join("asset", "RIASEC_Career_Framework.csv")
        
        if os.path.exists(framework_path):
            count = db_service.load_framework_from_csv(framework_path)
            print(f"✅ Loaded {count} RIASEC framework questions")
        else:
            print(f"⚠️  Framework file not found at: {framework_path}")
            print("   The framework will be loaded automatically when you run the app")
    except Exception as e:
        print(f"❌ Error loading framework: {e}")
        return
    
    print()
    
    # Optional: Load sample data
    print("3️⃣ Load sample data? (optional)")
    print("   Sample data file: asset/sample_student_data.csv")
    response = input("   Load sample data? (y/N): ").lower()
    
    if response == 'y':
        try:
            sample_path = os.path.join("asset", "sample_student_data.csv")
            if os.path.exists(sample_path):
                count = db_service.import_students_from_csv(sample_path)
                print(f"✅ Imported sample data for {count} student(s)")
            else:
                print(f"⚠️  Sample data file not found at: {sample_path}")
        except Exception as e:
            print(f"❌ Error loading sample data: {e}")
    else:
        print("⏭️  Skipped sample data import")
    
    print()
    print("🎉 Database initialization complete!")
    print()
    print("Next steps:")
    print("  1. Run: streamlit run app/main.py")
    print("  2. Open browser at: http://localhost:8501")
    print("  3. Create students and add grades")
    print("  4. Run career assessments")
    print()

if __name__ == "__main__":
    main()

