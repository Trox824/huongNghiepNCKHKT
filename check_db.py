"""
Check database users table structure
Run with: python3 -m streamlit run check_db.py
"""
import streamlit as st
from sqlalchemy import text, inspect
from app.config.database import engine
from app.services.logger import logger


st.set_page_config(page_title="Database Inspector", layout="wide")

st.title("🔍 Database Inspector")
st.markdown("### Check users table structure")

st.divider()

if st.button("Check Database", type="primary", use_container_width=True):
    with st.spinner("Checking database..."):
        try:
            with engine.connect() as connection:
                # Check if users table exists
                check_table = text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'users'
                    );
                """)
                result = connection.execute(check_table)
                table_exists = result.fetchone()[0]
                
                if not table_exists:
                    st.error("❌ Users table does not exist!")
                    st.info("Run: `python3 init_db.py` to create tables")
                else:
                    st.success("✅ Users table exists")
                    
                    # Get all columns in users table
                    columns_query = text("""
                        SELECT column_name, data_type, character_maximum_length, is_nullable
                        FROM information_schema.columns
                        WHERE table_name = 'users'
                        ORDER BY ordinal_position;
                    """)
                    result = connection.execute(columns_query)
                    columns = result.fetchall()
                    
                    st.subheader("📋 Current Columns in 'users' table:")
                    
                    import pandas as pd
                    df = pd.DataFrame(columns, columns=['Column Name', 'Data Type', 'Max Length', 'Nullable'])
                    st.dataframe(df, use_container_width=True)
                    
                    # Check for specific columns
                    column_names = [col[0] for col in columns]
                    
                    st.divider()
                    st.subheader("🔎 Column Check:")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if 'hashed_password' in column_names:
                            st.warning("⚠️ Found OLD column: `hashed_password`")
                            st.info("**Action needed:** Run migration to rename this column")
                        else:
                            st.success("✅ OLD column `hashed_password` not found")
                    
                    with col2:
                        if 'password' in column_names:
                            st.success("✅ Found NEW column: `password`")
                            st.info("Migration already completed!")
                        else:
                            st.error("❌ NEW column `password` not found")
                            st.info("**Action needed:** Run migration to create/rename column")
                    
                    # Count users
                    count_query = text("SELECT COUNT(*) FROM users;")
                    result = connection.execute(count_query)
                    user_count = result.fetchone()[0]
                    
                    st.divider()
                    st.metric("Total Users", user_count)
                    
                    if user_count > 0:
                        st.warning("⚠️ There are existing users in the database. Migration will preserve their data.")
                    
        except Exception as e:
            st.error(f"❌ Error checking database: {e}")
            logger.exception("Database check error")

st.divider()

# Show migration button
st.markdown("### 🔄 Need to run migration?")

migration_code = """
1. Stop this app
2. Run: python3 -m streamlit run run_migration.py
3. Click "Run Migration" button
4. Come back here to verify
"""

st.code(migration_code, language="bash")

