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
import pandas as pd
import tempfile
import os
from app.config.database import init_database, get_db_connection
from app.services.auth_service import AuthService
from app.services.database_service import DatabaseService
from app.services.logger import logger

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
        
        # Auto-migrate: rename hashed_password to password if needed
        try:
            from sqlalchemy import text
            from app.config.database import engine
            with engine.connect() as connection:
                # Check if hashed_password column exists
                check_query = text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'users' 
                    AND column_name = 'hashed_password'
                """)
                result = connection.execute(check_query)
                if result.fetchone():
                    # Rename the column
                    rename_query = text("""
                        ALTER TABLE users 
                        RENAME COLUMN hashed_password TO password;
                    """)
                    connection.execute(rename_query)
                    connection.commit()
                    logger.info("Auto-migrated: renamed hashed_password to password")
        except Exception as mig_error:
            logger.warning(f"Migration check failed (may be OK): {mig_error}")
        
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

# =====================
# AUTH UTILITIES
# =====================

def ensure_auth_session_state():
    """Ensure required authentication state variables exist."""
    if 'user' not in st.session_state:
        st.session_state['user'] = None
    if 'auth_mode' not in st.session_state:
        st.session_state['auth_mode'] = "login"


def render_auth_forms(auth_service: AuthService):
    """Render login and registration forms."""
    st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            display: none !important;
        }
        [data-testid="stSidebarNav"] {
            display: none !important;
        }
        [data-testid="stAppViewContainer"] {
            margin-left: 0 !important;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <h2 style="text-align: center;"><i class="fas fa-lock icon"></i>Đăng nhập để sử dụng hệ thống</h2>
    """, unsafe_allow_html=True)
    st.info("Vui lòng đăng nhập hoặc tạo tài khoản mới để tiếp tục.")

    auth_mode = st.radio(
        "Chọn chức năng",
        options=["Đăng nhập", "Đăng ký"],
        index=0 if st.session_state.get("auth_mode", "login") == "login" else 1,
        horizontal=True,
        key="auth_mode_selector",
    )
    st.session_state["auth_mode"] = "login" if auth_mode == "Đăng nhập" else "register"

    if auth_mode == "Đăng nhập":
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Tên đăng nhập", key="login_username")
            password = st.text_input("Mật khẩu", type="password", key="login_password")
            submit = st.form_submit_button("Đăng nhập", type="primary", use_container_width=True)

            if submit:
                # Strip whitespace from inputs
                username = username.strip() if username else ""
                password = password.strip() if password else ""
                
                if not username or not password:
                    st.error("Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu.")
                else:
                    user = auth_service.authenticate_user(username, password)
                    if user:
                        st.session_state['user'] = {
                            "id": user.id,
                            "username": user.username,
                            "email": user.email,
                            "is_admin": user.is_admin,
                        }
                        # Reset student selection and forms on new login
                        st.session_state['student_id'] = None
                        st.session_state['current_student'] = None
                        st.session_state['show_new_student_form'] = False
                        st.success("Đăng nhập thành công! Đang chuyển tiếp...")
                        st.rerun()
                    else:
                        st.error("Tên đăng nhập hoặc mật khẩu không chính xác.")
    else:
        with st.form("register_form", clear_on_submit=False):
            username = st.text_input("Tên đăng nhập*", key="register_username")
            email = st.text_input("Email", key="register_email")
            password = st.text_input("Mật khẩu*", type="password", key="register_password")
            confirm_password = st.text_input("Xác nhận mật khẩu*", type="password", key="register_confirm_password")
            submit = st.form_submit_button("Đăng ký", type="primary", use_container_width=True)

            if submit:
                # Strip whitespace from inputs
                username = username.strip() if username else ""
                email = email.strip() if email else None
                password = password.strip() if password else ""
                confirm_password = confirm_password.strip() if confirm_password else ""
                
                if not username or not password or not confirm_password:
                    st.error("Vui lòng nhập đầy đủ thông tin bắt buộc.")
                elif len(password) < 6:
                    st.error("Mật khẩu phải có ít nhất 6 ký tự.")
                elif password != confirm_password:
                    st.error("Mật khẩu xác nhận không khớp.")
                else:
                    # Check password length and warn if too long (bcrypt limit is 72 bytes)
                    password_bytes = len(password.encode('utf-8'))
                    if password_bytes > 72:
                        st.warning("⚠️ Mật khẩu quá dài (hơn 72 ký tự). Mật khẩu sẽ được cắt ngắn tự động.")
                    
                    try:
                        user = auth_service.create_user(username=username, password=password, email=email)
                        st.success("Đăng ký thành công! Vui lòng đăng nhập.")
                        st.session_state['auth_mode'] = "login"
                        # Clear form keys to reset the form
                        if 'register_username' in st.session_state:
                            del st.session_state['register_username']
                        if 'register_email' in st.session_state:
                            del st.session_state['register_email']
                        if 'register_password' in st.session_state:
                            del st.session_state['register_password']
                        if 'register_confirm_password' in st.session_state:
                            del st.session_state['register_confirm_password']
                        st.rerun()
                    except ValueError as exc:
                        st.error(str(exc))
                    except Exception as exc:
                        st.error(f"Lỗi khi đăng ký: {str(exc)}")
                        logger.exception("Registration error")


# Initialize
if initialize_app():
    # Ensure auth state and create services
    ensure_auth_session_state()
    db = get_db_connection()
    db_service = DatabaseService(db)
    auth_service = AuthService(db)

    if st.session_state['user']:
        with st.sidebar:
            user = st.session_state['user']
            st.markdown(f"### 👋 Xin chào, **{user['username']}**")
            if user.get('is_admin', False):
                st.markdown("**🔑 Vai trò: Quản trị viên**")
                st.caption("Bạn có quyền xem tất cả học sinh.")
            else:
                st.markdown("**👤 Vai trò: Học sinh**")
                st.caption("Bạn chỉ có thể xem thông tin của mình.")
            if st.button("Đăng xuất", use_container_width=True):
                st.session_state['user'] = None
                st.session_state['student_id'] = None
                st.session_state['current_student'] = None
                st.session_state['show_new_student_form'] = False
                st.success("Đã đăng xuất.")
                st.rerun()

    if not st.session_state['user']:
        render_auth_forms(auth_service)
        st.stop()

    # Title and description
    st.markdown("""
    <h2><i class="fas fa-graduation-cap icon"></i>Hệ Thống AI Phân Tích Kết Quả Học Tập và Định Hướng Nghề Nghiệp cho Học Sinh THPT</h2>
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
    
    # Student selector
    st.subheader("Chọn hoặc tạo học sinh")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Get students based on user role
        user = st.session_state['user']
        try:
            # Verify method exists (defensive check for deployment issues)
            if not hasattr(db_service, 'get_students_for_user'):
                raise AttributeError(
                    f"DatabaseService missing 'get_students_for_user' method. "
                    f"Available methods: {[m for m in dir(db_service) if not m.startswith('_')]}"
                )
            students = db_service.get_students_for_user(
                user_id=user['id'],
                is_admin=user.get('is_admin', False)
            )
        except AttributeError as e:
            st.error(f"Lỗi hệ thống: {str(e)}")
            logger.exception("DatabaseService method missing")
            # Fallback: use get_all_students for admin, empty list for regular users
            if user.get('is_admin', False) and hasattr(db_service, 'get_all_students'):
                students = db_service.get_all_students()
            else:
                students = []
        except Exception as e:
            st.error(f"Lỗi khi tải danh sách học sinh: {str(e)}")
            logger.exception("Error loading students")
            students = []
        
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
                # Load selected student with access control
                user = st.session_state['user']
                student = db_service.get_student_for_user(
                    student_id=selected_id,
                    user_id=user['id'],
                    is_admin=user.get('is_admin', False)
                )
                
                if not student:
                    st.error("Bạn không có quyền truy cập học sinh này.")
                    st.session_state['current_student'] = None
                    st.session_state['student_id'] = None
                else:
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
    
    # CSV Import Section
    st.divider()
    st.subheader("Nhập học sinh từ CSV")
    
    with st.expander("📥 Nhập dữ liệu học sinh từ file CSV", expanded=False):
        st.markdown("""
        ### Định dạng CSV
        File CSV của bạn cần có các cột sau:
        - `student_id`: Mã học sinh (bắt buộc)
        - `student_name`: Tên học sinh (bắt buộc)
        - `age`: Tuổi
        - `school`: Tên trường
        - `notes`: Ghi chú bổ sung
        - `subject`: Tên môn học (bắt buộc)
        - `grade_level`: Lớp (1-11) (bắt buộc)
        - `score`: Điểm (0-10) (bắt buộc)
        - `semester`: (Tùy chọn) Học kỳ (1 hoặc 2)
        """)
        
        uploaded_file = st.file_uploader("Chọn file CSV", type=['csv'])
        
        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file)
                st.success(f"Đã tải {len(df)} bản ghi")
                st.dataframe(df.head(10), use_container_width=True)
                
                if st.button("Nhập dữ liệu", type="primary", use_container_width=True):
                    try:
                        # Save temporarily and import
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='wb') as tmp:
                            tmp.write(uploaded_file.getvalue())
                            tmp_path = tmp.name
                        
                        count = db_service.import_students_from_csv(tmp_path)
                        
                        # Clean up temp file
                        os.unlink(tmp_path)
                        
                        st.success(f"✅ Đã nhập dữ liệu cho {count} học sinh")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Lỗi khi nhập dữ liệu: {e}")
            except Exception as e:
                st.error(f"Lỗi khi đọc CSV: {e}")
        
        # Download sample CSV
        st.markdown("### Tải xuống file CSV mẫu")
        
        # Create sample data
        sample_records = []
        subjects = ['TOÁN', 'VẬT LÝ', 'HÓA HỌC', 'ANH VĂN', 'VĂN HỌC']
        
        # Generate sample data for grades 9-11 across multiple subjects
        for subject in subjects:
            for grade in [9, 10, 11]:
                base_score = 7.0 + (subjects.index(subject) * 0.3)
                grade_bonus = (grade - 9) * 0.2
                score = min(10.0, base_score + grade_bonus + (0.1 * (grade - 9)))
                
                sample_records.append({
                    'student_id': 'ST001',
                    'student_name': 'Nguyễn Văn A',
                    'age': 17,
                    'school': 'Trường THPT ABC',
                    'notes': 'Ghi chú về học sinh tại đây',
                    'subject': subject,
                    'grade_level': grade,
                    'score': round(score, 1),
                    'semester': 1
                })
        
        sample_data = pd.DataFrame(sample_records)
        csv = sample_data.to_csv(index=False)
        st.download_button(
            label="📥 Tải xuống file CSV mẫu",
            data=csv,
            file_name="mau_du_lieu_hoc_sinh.csv",
            mime="text/csv",
            use_container_width=True
        )
    
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
                        # Link new student to current user (unless admin creating for others)
                        user = st.session_state['user']
                        user_id = None if user.get('is_admin', False) else user['id']
                        
                        student = db_service.create_student(
                            student_id=new_id,
                            name=new_name,
                            age=new_age,
                            school=new_school,
                            notes=new_notes,
                            user_id=user_id
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

