"""
Direct database fix - rename hashed_password to password
Run with: python3 -m streamlit run fix_column_now.py
"""
import streamlit as st
from sqlalchemy import text
from app.config.database import engine

st.set_page_config(page_title="Fix Database Column", layout="centered")

st.title("🔧 Fix Database Column")
st.markdown("### Rename `hashed_password` → `password`")

st.warning("""
**Current Issue:**
- Database has: `hashed_password`
- Code expects: `password`

This will rename the column to fix the mismatch.
""")

st.divider()

if st.button("🚀 FIX NOW", type="primary", use_container_width=True):
    try:
        with st.spinner("Renaming column..."):
            with engine.connect() as connection:
                trans = connection.begin()
                try:
                    # Rename the column
                    rename_query = text("""
                        ALTER TABLE users 
                        RENAME COLUMN hashed_password TO password;
                    """)
                    connection.execute(rename_query)
                    trans.commit()
                    
                    st.success("✅ Successfully renamed column!")
                    st.balloons()
                    
                    st.success("""
                    ### ✅ Migration Complete!
                    
                    **Next steps:**
                    1. Close this page
                    2. Go back to your main app
                    3. Try registering again - it should work now!
                    """)
                    
                except Exception as e:
                    trans.rollback()
                    st.error(f"❌ Error: {e}")
                    
    except Exception as e:
        st.error(f"❌ Database connection error: {e}")

st.divider()

st.info("""
**What this does:**
- Renames `hashed_password` column to `password` in the `users` table
- Preserves all existing data
- One-time operation
""")

