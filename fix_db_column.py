"""
Direct database column fix - no Streamlit needed
Run with: python3 fix_db_column.py
"""
import sys
import os
# Add parent directory to path
parent_dir = os.path.dirname(os.path.abspath(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from sqlalchemy import text
from app.config.database import engine
from app.services.logger import logger

print("🔧 Fixing database column...")
print()

try:
    with engine.connect() as connection:
        trans = connection.begin()
        try:
            # Check if hashed_password exists
            check_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                AND column_name = 'hashed_password'
            """)
            result = connection.execute(check_query)
            if result.fetchone():
                print("✅ Found 'hashed_password' column")
                
                # Rename the column
                rename_query = text("""
                    ALTER TABLE users 
                    RENAME COLUMN hashed_password TO password;
                """)
                connection.execute(rename_query)
                trans.commit()
                
                print("✅ Successfully renamed 'hashed_password' to 'password'")
                print()
                print("🎉 Migration complete!")
                print()
                print("You can now:")
                print("  1. Run: streamlit run app/main.py")
                print("  2. Register a new account")
                print("  3. It should work now!")
            else:
                # Check if password already exists
                check_password = text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'users' 
                    AND column_name = 'password'
                """)
                result = connection.execute(check_password)
                if result.fetchone():
                    print("✅ Column 'password' already exists")
                    print("⏭️  No migration needed")
                else:
                    print("❌ Neither column found. Something is wrong.")
                    trans.rollback()
                    
        except Exception as e:
            trans.rollback()
            print(f"❌ Error during migration: {e}")
            logger.exception("Migration error")
            raise
            
except Exception as e:
    print(f"❌ Database connection error: {e}")
    logger.exception("Database connection error")
    sys.exit(1)

