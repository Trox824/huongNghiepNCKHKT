"""
Student Career Guidance System - Main Entry Point
"""
import sys
import os
# Add parent directory to path so 'app' module can be imported
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import streamlit as st
from app.config.database import init_database, get_db_connection
from app.services.database_service import DatabaseService

# Page configuration
st.set_page_config(
    page_title="HỆ THỐNG HƯỚNG NGHIỆP HỌC SINH",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with professional icons - Dark theme optimized
st.markdown("""
<style>
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
    
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 1rem;
    }
    .stMetric {
        background-color: rgba(255, 255, 255, 0.05);
        padding: 10px;
        border-radius: 5px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    h1 {
        color: #4dabf7;
    }
    .icon {
        margin-right: 8px;
    }
    .feature-card {
        background: rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #4dabf7;
        margin-bottom: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .nav-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        min-height: 120px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .nav-card h3 {
        color: white !important;
        font-size: 1.1rem;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize database
@st.cache_resource
def initialize_app():
    """Initialize database and load framework"""
    try:
        init_database()
        db = get_db_connection()
        db_service = DatabaseService(db)
        
        # Load RIASEC framework if not already loaded
        framework_count = len(db_service.get_framework_questions())
        if framework_count == 0:
            framework_path = os.path.join("asset", "RIASEC_Career_Framework.csv")
            if os.path.exists(framework_path):
                count = db_service.load_framework_from_csv(framework_path)
                st.success(f"✅ ĐÃ TẢI {count} CÂU HỎI KHUNG RIASEC")
            else:
                st.warning("⚠️ KHÔNG TÌM THẤY FILE KHUNG RIASEC")
        
        return True
    except Exception as e:
        st.error(f"KHỞI TẠO CƠ SỞ DỮ LIỆU THẤT BẠI: {e}")
        return False

# Initialize
if initialize_app():
    # Title and description
    st.markdown("""
    <h1><i class="fas fa-graduation-cap icon"></i>HỆ THỐNG HƯỚNG NGHIỆP HỌC SINH</h1>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <h3><i class="fas fa-sparkles icon"></i>CHÀO MỪNG ĐÊN NỀN TẢNG HƯỚNG NGHIỆP SỬ DỤNG TRÍ TUỆ NHÂN TẠO</h3>
    
    <div class="feature-card">
        <p><i class="fas fa-chart-line icon"></i><strong>PHÂN TÍCH THÀNH TÍCH HỌC TẬP</strong><br/>
        THEO DÕI VÀ DỰ ĐOÁN ĐIỂM SỐ CÁC MÔN HỌC BẰNG HỌC MÁY</p>
    </div>
    
    <div class="feature-card">
        <p><i class="fas fa-user-check icon"></i><strong>ĐÁNH GIÁ NGHỀ NGHIỆP RIASEC</strong><br/>
        ĐÁNH GIÁ TÍNH CÁCH VÀ SỞ THÍCH SỬ DỤNG KHUNG HOLLAND CODE</p>
    </div>
    
    <div class="feature-card">
        <p><i class="fas fa-brain icon"></i><strong>GỢI Ý CÁ NHÂN HÓA</strong><br/>
        NHẬN GỢI Ý NGHỀ NGHIỆP PHỤC VỤ RIÊNG CHO HỒ SƠ CỦA BẠN</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Get database connection
    db = get_db_connection()
    db_service = DatabaseService(db)
    
    # Student selector
    st.subheader("CHỌN HOẶC TẠO HỌC SINH")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        students = db_service.get_all_students()
        
        if students:
            student_options = {f"{s.name} (ID: {s.id})": s.id for s in students}
            student_options["+ THÊM HỌC SINH MỚI"] = "NEW"
            
            selected = st.selectbox(
                "CHỌN HỌC SINH:",
                options=list(student_options.keys()),
                index=0
            )
            
            selected_id = student_options[selected]
            
            if selected_id != "NEW":
                # Load selected student
                student = db_service.get_student(selected_id)
                st.session_state['current_student'] = student
                st.session_state['student_id'] = student.id
                
                # Display student info
                st.success(f"ĐÃ TẢI: **{student.name}**")
                
                # Quick stats
                grades = db_service.get_student_grades(student.id)
                predictions = db_service.get_student_predictions(student.id)
                assessment = db_service.get_student_assessments(student.id)
                
                col_a, col_b, col_c, col_d = st.columns(4)
                with col_a:
                    st.metric("TUỔI", student.age)
                with col_b:
                    st.metric("BẢN GHI ĐIỂM", len(grades))
                with col_c:
                    st.metric("DỰ ĐOÁN", len(predictions))
                with col_d:
                    st.metric("ĐÁNH GIÁ", "HOÀN THÀNH" if assessment else "ĐANG CHỜ")
                
                st.info(f"**TRƯỜNG:** {student.school}")
                if student.notes:
                    with st.expander("GHI CHÚ HỌC SINH"):
                        st.write(student.notes)
        else:
            st.info("KHÔNG TÌM THẤY HỌC SINH. VUI LÒNG THÊM HỌC SINH MỚI HOẶC NHẬP TỪ CSV.")
            st.session_state['current_student'] = None
    
    with col2:
        if st.button("+ HỌC SINH MỚI", use_container_width=True):
            st.session_state['show_new_student_form'] = True
    
    # New student form
    if st.session_state.get('show_new_student_form', False):
        st.divider()
        st.subheader("TẠO HỌC SINH MỚI")
        
        with st.form("new_student_form"):
            new_id = st.text_input("MÃ HỌC SINH*", placeholder="VD: ST001")
            new_name = st.text_input("HỌ VÀ TÊN*", placeholder="VD: NGUYỄN VĂN A")
            new_age = st.number_input("TUỔI", min_value=10, max_value=25, value=17)
            new_school = st.text_input("TRƯỜNG", placeholder="VD: TRƯỜNG THPT ABC")
            new_notes = st.text_area("GHI CHÚ (HOẠT ĐỘNG NGOẠI KHÓA, SỞ THÍCH, ...)")
            
            col_submit, col_cancel = st.columns(2)
            with col_submit:
                submitted = st.form_submit_button("TẠO HỌC SINH", use_container_width=True, type="primary")
            with col_cancel:
                cancelled = st.form_submit_button("HỦY", use_container_width=True)
            
            if submitted:
                if not new_id or not new_name:
                    st.error("VUI LÒNG NHẬP MÃ HỌC SINH VÀ TÊN")
                else:
                    try:
                        student = db_service.create_student(
                            student_id=new_id,
                            name=new_name,
                            age=new_age,
                            school=new_school,
                            notes=new_notes
                        )
                        st.success(f"ĐÃ TẠO HỌC SINH: {student.name}")
                        st.session_state['show_new_student_form'] = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"LỖI KHI TẠO HỌC SINH: {e}")
            
            if cancelled:
                st.session_state['show_new_student_form'] = False
                st.rerun()
    
    # Navigation guide
    st.divider()
    st.markdown('<h2><i class="fas fa-compass icon"></i>HƯỚNG DẪN ĐIỀU HƯỚNG</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="nav-card">
            <i class="fas fa-users fa-2x"></i>
            <h3>QUẢN LÝ HỌC SINH</h3>
            <p style="font-size: 0.9rem;">THÊM, CHỈNH SỬA, HOẶC NHẬP DỮ LIỆU HỌC SINH VÀ ĐIỂM SỐ</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="nav-card">
            <i class="fas fa-chart-bar fa-2x"></i>
            <h3>BẢNG ĐIỀU KHIỂN</h3>
            <p style="font-size: 0.9rem;">XEM XU HƯỚNG ĐIỂM SỐ VÀ DỰ ĐOÁN LỚP 12</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class="nav-card">
            <i class="fas fa-clipboard-check fa-2x"></i>
            <h3>ĐÁNH GIÁ NGHỀ NGHIỆP</h3>
            <p style="font-size: 0.9rem;">HOÀN THÀNH ĐÁNH GIÁ TÍNH CÁCH RIASEC VÀ NHẬN GỢI Ý</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: gray; padding: 20px;'>
        <p>HỖ TRỢ BỞI OPENAI GPT-4 • HỌC MÁY HỒI QUY TUYẾN TÍNH • KHUNG RIASEC HOLLAND</p>
    </div>
    """, unsafe_allow_html=True)

else:
    st.error("KHỞI TẠO ỨNG DỤNG THẤT BẠI. VUI LÒNG KIỂM TRA KẾT NỐI CƠ SỞ DỮ LIỆU.")

