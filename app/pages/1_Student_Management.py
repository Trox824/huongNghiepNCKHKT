"""
Student Management Page - CRUD operations for students and grades
"""
import sys
import os
# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import streamlit as st
import pandas as pd
from app.config.database import get_db_connection
from app.services.database_service import DatabaseService

st.set_page_config(page_title="QUẢN LÝ HỌC SINH", layout="wide")

# Add Font Awesome
st.markdown("""
<style>
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
    .icon { margin-right: 8px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1><i class="fas fa-users icon"></i>QUẢN LÝ HỌC SINH</h1>', unsafe_allow_html=True)
st.markdown("QUẢN LÝ HỒ SƠ HỌC SINH VÀ BẢN GHI ĐIỂM")

# Get database connection
db = get_db_connection()
db_service = DatabaseService(db)

# Check if student is selected
if 'student_id' not in st.session_state or not st.session_state.get('student_id'):
    st.warning("VUI LÒNG CHỌN HỌC SINH TỪ TRANG CHỦ TRƯỚC")
    st.stop()

student_id = st.session_state['student_id']
student = db_service.get_student(student_id)

if not student:
    st.error(f"KHÔNG TÌM THẤY HỌC SINH {student_id}")
    st.stop()

# Tabs for different management functions
tab1, tab2 = st.tabs(["CHỈNH SỬA HỒ SƠ", "QUẢN LÝ ĐIỂM"])

# =============================
# TAB 1: EDIT PROFILE
# =============================
with tab1:
    st.subheader(f"CHỈNH SỬA HỒ SƠ: {student.name}")
    
    with st.form("edit_profile_form"):
        name = st.text_input("HỌ VÀ TÊN", value=student.name)
        age = st.number_input("TUỔI", min_value=10, max_value=25, value=student.age)
        school = st.text_input("TRƯỜNG", value=student.school or "")
        notes = st.text_area("GHI CHÚ", value=student.notes or "", height=150)
        
        col1, col2 = st.columns(2)
        with col1:
            update_btn = st.form_submit_button("CẬP NHẬT HỒ SƠ", use_container_width=True, type="primary")
        with col2:
            delete_btn = st.form_submit_button("XÓA HỌC SINH", use_container_width=True)
        
        if update_btn:
            try:
                db_service.update_student(
                    student_id=student_id,
                    name=name,
                    age=age,
                    school=school,
                    notes=notes
                )
                st.success("CẬP NHẬT HỒ SƠ THÀNH CÔNG!")
                st.rerun()
            except Exception as e:
                st.error(f"LỖI KHI CẬP NHẬT HỒ SƠ: {e}")
        
        if delete_btn:
            st.session_state['confirm_delete'] = True

    # Confirm delete
    if st.session_state.get('confirm_delete', False):
        st.warning(f"BẠN CÓ CHẮC CHẮN MUỐN XÓA {student.name}? HÀNH ĐỘNG NÀY SẼ XÓA TẤT CẢ ĐIỂM SỐ, DỰ ĐOÁN VÀ ĐÁNH GIÁ.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("CÓ, XÓA", type="primary"):
                try:
                    db_service.delete_student(student_id)
                    st.success("ĐÃ XÓA HỌC SINH")
                    st.session_state['student_id'] = None
                    st.session_state['confirm_delete'] = False
                    st.switch_page("app/main.py")
                except Exception as e:
                    st.error(f"LỖI KHI XÓA HỌC SINH: {e}")
        with col2:
            if st.button("HỦY"):
                st.session_state['confirm_delete'] = False
                st.rerun()

# =============================
# TAB 2: MANAGE GRADES
# =============================
with tab2:
    st.subheader(f"QUẢN LÝ ĐIỂM: {student.name}")
    
    # Add new grade
    with st.expander("+ THÊM ĐIỂM MỚI", expanded=False):
        with st.form("add_grade_form"):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                subject = st.text_input("MÔN HỌC*", placeholder="VD: TOÁN")
            with col2:
                grade_level = st.number_input("LỚP*", min_value=1, max_value=11, value=9)
            with col3:
                score = st.number_input("ĐIỂM*", min_value=0.0, max_value=10.0, value=7.0, step=0.1, format="%.1f")
            with col4:
                semester = st.selectbox("HỌC KỲ", options=[None, 1, 2])
            
            add_grade_btn = st.form_submit_button("THÊM ĐIỂM", use_container_width=True, type="primary")
            
            if add_grade_btn:
                if not subject:
                    st.error("VUI LÒNG NHẬP MÔN HỌC")
                else:
                    try:
                        db_service.add_grade(
                            student_id=student_id,
                            subject=subject,
                            grade_level=grade_level,
                            score=score,
                            semester=semester
                        )
                        st.success(f"ĐÃ THÊM: {subject} LỚP {grade_level} = {score}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"LỖI KHI THÊM ĐIỂM: {e}")
    
    # Display existing grades
    grades_df = db_service.get_student_grades_df(student_id)
    
    if grades_df.empty:
        st.info("KHÔNG TÌM THẤY BẢN GHI ĐIỂM. THÊM ĐIỂM Ở TRÊN HOẶC NHẬP TỪ CSV.")
    else:
        st.markdown(f"**TỔNG SỐ BẢN GHI:** {len(grades_df)}")
        
        # Make editable dataframe
        edited_df = st.data_editor(
            grades_df,
            column_config={
                "id": st.column_config.NumberColumn("ID", disabled=True),
                "student_id": st.column_config.TextColumn("MÃ HỌC SINH", disabled=True),
                "subject": st.column_config.TextColumn("MÔN HỌC", required=True),
                "grade_level": st.column_config.NumberColumn("LỚP", min_value=1, max_value=11, required=True),
                "score": st.column_config.NumberColumn("ĐIỂM", min_value=0.0, max_value=10.0, format="%.1f", required=True),
                "semester": st.column_config.NumberColumn("HỌC KỲ", min_value=1, max_value=2)
            },
            hide_index=True,
            use_container_width=True,
            num_rows="dynamic"
        )
        
        # Update button
        if st.button("LƯU THAY ĐỔI", type="primary"):
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
                    st.success("LƯU THAY ĐỔI THÀNH CÔNG!")
                    st.rerun()
                else:
                    st.info("KHÔNG PHÁT HIỆN THAY ĐỔI")
            except Exception as e:
                st.error(f"LỖI KHI LƯU THAY ĐỔI: {e}")
        
        # Delete grades
        with st.expander("XÓA ĐIỂM"):
            if st.button("XÓA TẤT CẢ ĐIỂM", type="primary"):
                try:
                    count = db_service.delete_student_grades(student_id)
                    st.success(f"ĐÃ XÓA {count} BẢN GHI ĐIỂM")
                    st.rerun()
                except Exception as e:
                    st.error(f"LỖI KHI XÓA ĐIỂM: {e}")

