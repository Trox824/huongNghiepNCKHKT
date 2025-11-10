"""
Simple database migration script
Run with: python3 -m streamlit run run_migration.py
"""
import streamlit as st
from sqlalchemy import text
from app.config.database import engine
from app.services.logger import logger


st.set_page_config(page_title="Database Migration", layout="centered")

st.title("🔄 Database Migration")
st.markdown("### Rename 'hashed_password' to 'password' in users table")

st.divider()

if st.button("Run Migration", type="primary", use_container_width=True):
    with st.spinner("Running migration..."):
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
                        st.info("✅ Found 'hashed_password' column")
                        
                        # Rename the column
                        rename_query = text("""
                            ALTER TABLE users 
                            RENAME COLUMN hashed_password TO password
                        """)
                        connection.execute(rename_query)
                        st.success("✅ Renamed column from 'hashed_password' to 'password'")
                        
                        trans.commit()
                        st.success("🎉 Migration completed successfully!")
                        
                        st.info("""
                        **Next steps:**
                        1. Close this migration page
                        2. Run: `streamlit run app/main.py`
                        3. Register a new account
                        4. Log in and start using the system
                        """)
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
                            st.success("✅ Column 'password' already exists")
                            st.info("⏭️ No migration needed")
                        else:
                            st.warning("⚠️ Neither 'hashed_password' nor 'password' column found")
                            st.info("Creating 'password' column...")
                            
                            create_query = text("""
                                ALTER TABLE users 
                                ADD COLUMN password VARCHAR(255) NOT NULL DEFAULT ''
                            """)
                            connection.execute(create_query)
                            st.success("✅ Created 'password' column")
                            
                            trans.commit()
                            st.success("🎉 Migration completed successfully!")
                    
                except Exception as e:
                    trans.rollback()
                    raise e
                    
        except Exception as e:
            st.error(f"❌ Migration failed: {e}")
            logger.exception("Migration error")
            st.error("""
            **Troubleshooting:**
            - Check your database connection
            - Verify the users table exists
            - Check database permissions
            """)

st.divider()

st.markdown("""
### What does this migration do?

This script renames the `hashed_password` column to `password` in the `users` table.
This is necessary because the authentication system was updated to use plain password storage
instead of hashed passwords.

**Note:** This is a one-time migration. Once completed, you can delete this file.
""")

# Display current database connection info (without credentials)
st.caption("Connected to: Railway PostgreSQL Database")

