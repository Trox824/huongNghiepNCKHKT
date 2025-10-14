"""
Student Management Page - CRUD operations for students and grades
"""
import streamlit as st
import pandas as pd
from app.config.database import get_db_connection
from app.services.database_service import DatabaseService

st.set_page_config(page_title="Student Management", page_icon="📚", layout="wide")

# Add Font Awesome
st.markdown("""
<style>
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
    .icon { margin-right: 8px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1><i class="fas fa-users icon"></i>Student Management</h1>', unsafe_allow_html=True)
st.markdown("Manage student profiles and grade records")

# Get database connection
db = get_db_connection()
db_service = DatabaseService(db)

# Check if student is selected
if 'student_id' not in st.session_state or not st.session_state.get('student_id'):
    st.warning(" Please select a student from the home page first")
    st.stop()

student_id = st.session_state['student_id']
student = db_service.get_student(student_id)

if not student:
    st.error(f"Student {student_id} not found")
    st.stop()

# Tabs for different management functions
tab1, tab2, tab3 = st.tabs([" Edit Profile", " Manage Grades", " Import Data"])

# =============================
# TAB 1: EDIT PROFILE
# =============================
with tab1:
    st.subheader(f"Edit Profile: {student.name}")
    
    with st.form("edit_profile_form"):
        name = st.text_input("Full Name", value=student.name)
        age = st.number_input("Age", min_value=10, max_value=25, value=student.age)
        school = st.text_input("School", value=student.school or "")
        notes = st.text_area("Notes", value=student.notes or "", height=150)
        
        col1, col2 = st.columns(2)
        with col1:
            update_btn = st.form_submit_button(" Update Profile", use_container_width=True, type="primary")
        with col2:
            delete_btn = st.form_submit_button(" Delete Student", use_container_width=True)
        
        if update_btn:
            try:
                db_service.update_student(
                    student_id=student_id,
                    name=name,
                    age=age,
                    school=school,
                    notes=notes
                )
                st.success(" Profile updated successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error updating profile: {e}")
        
        if delete_btn:
            st.session_state['confirm_delete'] = True

    # Confirm delete
    if st.session_state.get('confirm_delete', False):
        st.warning(f" Are you sure you want to delete {student.name}? This will delete all grades, predictions, and assessments.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes, Delete", type="primary"):
                try:
                    db_service.delete_student(student_id)
                    st.success(" Student deleted")
                    st.session_state['student_id'] = None
                    st.session_state['confirm_delete'] = False
                    st.switch_page("app/main_new.py")
                except Exception as e:
                    st.error(f"Error deleting student: {e}")
        with col2:
            if st.button("Cancel"):
                st.session_state['confirm_delete'] = False
                st.rerun()

# =============================
# TAB 2: MANAGE GRADES
# =============================
with tab2:
    st.subheader(f"Manage Grades: {student.name}")
    
    # Add new grade
    with st.expander("+ Add New Grade", expanded=False):
        with st.form("add_grade_form"):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                subject = st.text_input("Subject*", placeholder="e.g., Math")
            with col2:
                grade_level = st.number_input("Grade Level*", min_value=1, max_value=11, value=9)
            with col3:
                score = st.number_input("Score*", min_value=0.0, max_value=10.0, value=7.0, step=0.1, format="%.1f")
            with col4:
                semester = st.selectbox("Semester", options=[None, 1, 2])
            
            add_grade_btn = st.form_submit_button("Add Grade", use_container_width=True, type="primary")
            
            if add_grade_btn:
                if not subject:
                    st.error("Please enter a subject")
                else:
                    try:
                        db_service.add_grade(
                            student_id=student_id,
                            subject=subject,
                            grade_level=grade_level,
                            score=score,
                            semester=semester
                        )
                        st.success(f" Added: {subject} Grade {grade_level} = {score}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding grade: {e}")
    
    # Display existing grades
    grades_df = db_service.get_student_grades_df(student_id)
    
    if grades_df.empty:
        st.info("No grade records found. Add grades above or import from CSV.")
    else:
        st.markdown(f"**Total Records:** {len(grades_df)}")
        
        # Make editable dataframe
        edited_df = st.data_editor(
            grades_df,
            column_config={
                "id": st.column_config.NumberColumn("ID", disabled=True),
                "student_id": st.column_config.TextColumn("Student ID", disabled=True),
                "subject": st.column_config.TextColumn("Subject", required=True),
                "grade_level": st.column_config.NumberColumn("Grade", min_value=1, max_value=11, required=True),
                "score": st.column_config.NumberColumn("Score", min_value=0.0, max_value=10.0, format="%.1f", required=True),
                "semester": st.column_config.NumberColumn("Semester", min_value=1, max_value=2)
            },
            hide_index=True,
            use_container_width=True,
            num_rows="dynamic"
        )
        
        # Update button
        if st.button(" Save Changes", type="primary"):
            try:
                # Compare and update changed rows
                changes_made = False
                for idx, row in edited_df.iterrows():
                    original_row = grades_df.loc[grades_df['id'] == row['id']]
                    if not original_row.empty:
                        original = original_row.iloc[0]
                        if (row['subject'] != original['subject'] or 
                            row['grade_level'] != original['grade_level'] or
                            row['score'] != original['score'] or
                            row['semester'] != original['semester']):
                            db_service.update_grade(
                                grade_id=int(row['id']),
                                subject=row['subject'],
                                grade_level=int(row['grade_level']),
                                score=float(row['score']),
                                semester=int(row['semester']) if pd.notna(row['semester']) else None
                            )
                            changes_made = True
                
                if changes_made:
                    st.success(" Changes saved successfully!")
                    st.rerun()
                else:
                    st.info("No changes detected")
            except Exception as e:
                st.error(f"Error saving changes: {e}")
        
        # Delete grades
        with st.expander(" Delete Grades"):
            if st.button("Delete All Grades", type="primary"):
                try:
                    count = db_service.delete_student_grades(student_id)
                    st.success(f" Deleted {count} grade records")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error deleting grades: {e}")

# =============================
# TAB 3: IMPORT DATA
# =============================
with tab3:
    st.subheader(" Import Student Data from CSV")
    
    st.markdown("""
    ### CSV Format
    Your CSV file should have the following columns:
    - `student_id`: Student ID (will use current student if matches, or create new)
    - `student_name`: Student name
    - `age`: Age
    - `school`: School name
    - `notes`: Additional notes
    - `subject`: Subject name
    - `grade_level`: Grade level (1-11)
    - `score`: Score (0-10)
    - `semester`: (Optional) Semester (1 or 2)
    """)
    
    uploaded_file = st.file_uploader("Choose CSV file", type=['csv'])
    
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            st.success(f" Loaded {len(df)} records")
            st.dataframe(df.head(10), use_container_width=True)
            
            if st.button("Import Data", type="primary"):
                try:
                    # Save temporarily and import
                    import tempfile
                    import os
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='wb') as tmp:
                        tmp.write(uploaded_file.getvalue())
                        tmp_path = tmp.name
                    
                    count = db_service.import_students_from_csv(tmp_path)
                    
                    # Clean up temp file
                    os.unlink(tmp_path)
                    
                    st.success(f" Imported data for {count} student(s)")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error importing data: {e}")
        except Exception as e:
            st.error(f"Error reading CSV: {e}")
    
    # Download sample CSV
    st.divider()
    st.markdown("###  Download Sample CSV")
    sample_data = pd.DataFrame([
        {
            'student_id': student_id,
            'student_name': student.name,
            'age': student.age,
            'school': student.school,
            'notes': student.notes or '',
            'subject': 'Math',
            'grade_level': 9,
            'score': 8.5,
            'semester': 1
        }
    ])
    
    csv = sample_data.to_csv(index=False)
    st.download_button(
        label="Download Sample CSV",
        data=csv,
        file_name=f"sample_student_data_{student_id}.csv",
        mime="text/csv"
    )

