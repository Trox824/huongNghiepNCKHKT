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
    page_title="Hệ Thống AI Phân Tích Kết Quả Học Tập và Định Hướng Nghề Nghiệp cho Học Sinh THPT",
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
                st.success(f"✅ Đã tải {count} câu hỏi khung RIASEC")
            else:
                st.warning("⚠️ Không tìm thấy file khung RIASEC")
        
        return True
    except Exception as e:
        st.error(f"Khởi tạo cơ sở dữ liệu thất bại: {e}")
        return False

# Initialize
if initialize_app():
    # Title and description
    st.markdown("""
    <h1><i class="fas fa-graduation-cap icon"></i>Hệ Thống AI Phân Tích Kết Quả Học Tập và Định Hướng Nghề Nghiệp cho Học Sinh THPT</h1>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <h3><i class="fas fa-sparkles icon"></i>Chào mừng đến nền tảng hướng nghiệp sử dụng trí tuệ nhân tạo</h3>
    
    <div class="feature-card">
        <p><i class="fas fa-chart-line icon"></i><strong>Phân tích thành tích học tập</strong><br/>
        Theo dõi và dự đoán điểm số các môn học bằng học máy</p>
    </div>
    
    <div class="feature-card">
        <p><i class="fas fa-user-check icon"></i><strong>Đánh giá nghề nghiệp RIASEC</strong><br/>
        Đánh giá tính cách và sở thích sử dụng khung Holland Code</p>
    </div>
    
    <div class="feature-card">
        <p><i class="fas fa-brain icon"></i><strong>Gợi ý cá nhân hóa</strong><br/>
        Nhận gợi ý nghề nghiệp phục vụ riêng cho hồ sơ của bạn</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Get database connection
    db = get_db_connection()
    db_service = DatabaseService(db)
    
    # Student selector
    st.subheader("Chọn hoặc tạo học sinh")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        students = db_service.get_all_students()
        
        if students:
            student_options = {f"{s.name} (ID: {s.id})": s.id for s in students}
            student_options["+ Thêm học sinh mới"] = "NEW"
            
            selected = st.selectbox(
                "Chọn học sinh:",
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
                st.success(f"Đã tải: **{student.name}**")
                
                # Quick stats
                grades = db_service.get_student_grades(student.id)
                predictions = db_service.get_student_predictions(student.id)
                assessment = db_service.get_student_assessments(student.id)
                
                col_a, col_b, col_c, col_d = st.columns(4)
                with col_a:
                    st.metric("Tuổi", student.age)
                with col_b:
                    st.metric("Bản ghi điểm", len(grades))
                with col_c:
                    st.metric("Dự đoán", len(predictions))
                with col_d:
                    st.metric("Đánh giá", "Hoàn thành" if assessment else "Đang chờ")
                
                st.info(f"**Trường:** {student.school}")
                if student.notes:
                    with st.expander("Ghi chú học sinh"):
                        st.write(student.notes)
        else:
            st.info("Không tìm thấy học sinh. Vui lòng thêm học sinh mới hoặc nhập từ CSV.")
            st.session_state['current_student'] = None
    
    with col2:
        if st.button("+ Học sinh mới", use_container_width=True):
            st.session_state['show_new_student_form'] = True
    
    # New student form
    if st.session_state.get('show_new_student_form', False):
        st.divider()
        st.subheader("Tạo học sinh mới")
        
        with st.form("new_student_form"):
            new_id = st.text_input("Mã học sinh*", placeholder="VD: ST001")
            new_name = st.text_input("Họ và tên*", placeholder="VD: Nguyễn Văn A")
            new_age = st.number_input("Tuổi", min_value=10, max_value=25, value=17)
            new_school = st.text_input("Trường", placeholder="VD: Trường THPT ABC")
            new_notes = st.text_area("Ghi chú (hoạt động ngoại khóa, sở thích, ...)")
            
            col_submit, col_cancel = st.columns(2)
            with col_submit:
                submitted = st.form_submit_button("Tạo học sinh", use_container_width=True, type="primary")
            with col_cancel:
                cancelled = st.form_submit_button("Hủy", use_container_width=True)
            
            if submitted:
                if not new_id or not new_name:
                    st.error("Vui lòng nhập mã học sinh và tên")
                else:
                    try:
                        student = db_service.create_student(
                            student_id=new_id,
                            name=new_name,
                            age=new_age,
                            school=new_school,
                            notes=new_notes
                        )
                        st.success(f"Đã tạo học sinh: {student.name}")
                        st.session_state['show_new_student_form'] = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"Lỗi khi tạo học sinh: {e}")
            
            if cancelled:
                st.session_state['show_new_student_form'] = False
                st.rerun()
    
    # Navigation guide
    st.divider()
    st.markdown('<h2><i class="fas fa-compass icon"></i>Hướng dẫn điều hướng</h2>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="nav-card">
            <i class="fas fa-users fa-2x"></i>
            <h3>Quản lý học sinh</h3>
            <p style="font-size: 0.9rem;">Thêm, chỉnh sửa, hoặc nhập dữ liệu học sinh và điểm số</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="nav-card">
            <i class="fas fa-chart-bar fa-2x"></i>
            <h3>Bảng điều khiển</h3>
            <p style="font-size: 0.9rem;">Xem xu hướng điểm số và dự đoán lớp 12</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class="nav-card">
            <i class="fas fa-clipboard-check fa-2x"></i>
            <h3>Đánh giá nghề nghiệp</h3>
            <p style="font-size: 0.9rem;">Hoàn thành đánh giá tính cách RIASEC và nhận gợi ý</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col4:
        st.markdown("""
        <div class="nav-card">
            <i class="fas fa-robot fa-2x"></i>
            <h3>AI Cố vấn</h3>
            <p style="font-size: 0.9rem;">Trò chuyện với AI để được tư vấn nghề nghiệp cá nhân hóa</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: gray; padding: 20px;'>
        <p>Hỗ trợ bởi OpenAI GPT-4 • Học máy hồi quy tuyến tính • Khung RIASEC Holland</p>
    </div>
    """, unsafe_allow_html=True)

else:
    st.error("Khởi tạo ứng dụng thất bại. Vui lòng kiểm tra kết nối cơ sở dữ liệu.")

