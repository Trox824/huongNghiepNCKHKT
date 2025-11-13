"""
Migration script to add user_id column to students table
This links students to user accounts for role-based access control
"""
import sys
import os
# Add parent directory to path
parent_dir = os.path.dirname(os.path.abspath(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from sqlalchemy import text, inspect
from app.config.database import engine, get_db_connection
from app.services.logger import logger

def migrate_add_user_id_to_students():
    """Add user_id column to students table if it doesn't exist"""
    db = get_db_connection()
    
    try:
        # Check if user_id column already exists
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('students')]
        
        if 'user_id' in columns:
            logger.info("Column 'user_id' already exists in students table. Skipping migration.")
            return
        
        logger.info("Starting migration: Adding user_id column to students table...")
        
        # Add user_id column (nullable initially)
        with engine.connect() as connection:
            # Add the column
            connection.execute(text("""
                ALTER TABLE students 
                ADD COLUMN user_id INTEGER;
            """))
            
            # Add foreign key constraint
            connection.execute(text("""
                ALTER TABLE students 
                ADD CONSTRAINT fk_students_user_id 
                FOREIGN KEY (user_id) 
                REFERENCES users(id) 
                ON DELETE SET NULL;
            """))
            
            connection.commit()
            logger.info("✅ Successfully added user_id column and foreign key constraint to students table")
        
        # For existing students without user_id, we'll leave them as NULL
        # Admins can see all students (including those without user_id)
        # Regular users will only see students linked to their account
        
        logger.info("Migration completed successfully!")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Migration: Add user_id to students table")
    print("=" * 60)
    
    try:
        migrate_add_user_id_to_students()
        print("\n✅ Migration completed successfully!")
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        sys.exit(1)

