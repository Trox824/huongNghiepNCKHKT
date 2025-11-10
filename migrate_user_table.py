"""
Database migration script to update User table
Renames hashed_password to password column
"""
from sqlalchemy import text
from app.config.database import engine, get_db_connection
from app.services.logger import logger


def migrate_user_table():
    """Migrate the users table to rename hashed_password to password."""
    print("🔄 Starting User table migration...")
    print()
    
    try:
        with engine.connect() as connection:
            # Start a transaction
            trans = connection.begin()
            
            try:
                # Check if the old column exists
                check_query = text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'users' 
                    AND column_name = 'hashed_password'
                """)
                result = connection.execute(check_query)
                old_column_exists = result.fetchone() is not None
                
                if old_column_exists:
                    print("✅ Found 'hashed_password' column")
                    
                    # Rename the column
                    rename_query = text("""
                        ALTER TABLE users 
                        RENAME COLUMN hashed_password TO password
                    """)
                    connection.execute(rename_query)
                    print("✅ Renamed column from 'hashed_password' to 'password'")
                    
                    trans.commit()
                    print()
                    print("🎉 Migration completed successfully!")
                else:
                    # Check if new column already exists
                    check_new_query = text("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = 'users' 
                        AND column_name = 'password'
                    """)
                    result = connection.execute(check_new_query)
                    new_column_exists = result.fetchone() is not None
                    
                    if new_column_exists:
                        print("✅ Column 'password' already exists")
                        print("⏭️  No migration needed")
                    else:
                        print("⚠️  Neither 'hashed_password' nor 'password' column found")
                        print("   Creating 'password' column...")
                        
                        create_query = text("""
                            ALTER TABLE users 
                            ADD COLUMN password VARCHAR(255) NOT NULL DEFAULT ''
                        """)
                        connection.execute(create_query)
                        print("✅ Created 'password' column")
                        
                        trans.commit()
                        print()
                        print("🎉 Migration completed successfully!")
                
            except Exception as e:
                trans.rollback()
                raise e
                
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        logger.exception("Migration error")
        return False
    
    print()
    print("Next steps:")
    print("  1. Run: streamlit run app/main.py")
    print("  2. Register a new account")
    print("  3. Log in and start using the system")
    print()
    
    return True


if __name__ == "__main__":
    migrate_user_table()

