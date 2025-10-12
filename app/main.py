"""
Student Career Guidance System - Main Entry Point
"""
import streamlit as st
from app.config.database import init_database, get_db_connection
from app.services.database_service import DatabaseService
import os

# Page configuration
st.set_page_config(
    page_title="Student Career Guidance System",
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
                st.success(f"✅ Loaded {count} RIASEC framework questions")
            else:
                st.warning("⚠️ RIASEC framework file not found")
        
        return True
    except Exception as e:
        st.error(f"Failed to initialize database: {e}")
        return False

# Initialize
if initialize_app():
    # Title and description
    st.markdown("""
    <h1><i class="fas fa-graduation-cap icon"></i>Student Career Guidance System</h1>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <h3><i class="fas fa-sparkles icon"></i>Welcome to the AI-Powered Career Guidance Platform</h3>
    
    <div class="feature-card">
        <p><i class="fas fa-chart-line icon"></i><strong>Academic Performance Analysis</strong><br/>
        Track and predict grades across all subjects with machine learning</p>
    </div>
    
    <div class="feature-card">
        <p><i class="fas fa-user-check icon"></i><strong>RIASEC Career Assessment</strong><br/>
        Evaluate personality and interests using the Holland Code framework</p>
    </div>
    
    <div class="feature-card">
        <p><i class="fas fa-brain icon"></i><strong>Personalized Recommendations</strong><br/>
        Get AI-powered career path suggestions tailored to your profile</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Get database connection
    db = get_db_connection()
    db_service = DatabaseService(db)
    
    # Student selector
    st.subheader("Select or Create a Student")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        students = db_service.get_all_students()
        
        if students:
            student_options = {f"{s.name} (ID: {s.id})": s.id for s in students}
            student_options["+ Add New Student"] = "NEW"
            
            selected = st.selectbox(
                "Choose a student:",
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
                st.success(f"Loaded: **{student.name}**")
                
                # Quick stats
                grades = db_service.get_student_grades(student.id)
                predictions = db_service.get_student_predictions(student.id)
                assessment = db_service.get_student_assessments(student.id)
                
                col_a, col_b, col_c, col_d = st.columns(4)
                with col_a:
                    st.metric("Age", student.age)
                with col_b:
                    st.metric("Grade Records", len(grades))
                with col_c:
                    st.metric("Predictions", len(predictions))
                with col_d:
                    st.metric("Assessment", "Complete" if assessment else "Pending")
                
                st.info(f"**School:** {student.school}")
                if student.notes:
                    with st.expander("Student Notes"):
                        st.write(student.notes)
        else:
            st.info("No students found. Please add a new student or import from CSV.")
            st.session_state['current_student'] = None
    
    with col2:
        if st.button("+ New Student", use_container_width=True):
            st.session_state['show_new_student_form'] = True
    
    # New student form
    if st.session_state.get('show_new_student_form', False):
        st.divider()
        st.subheader("Create New Student")
        
        with st.form("new_student_form"):
            new_id = st.text_input("Student ID*", placeholder="e.g., ST001")
            new_name = st.text_input("Full Name*", placeholder="e.g., John Doe")
            new_age = st.number_input("Age", min_value=10, max_value=25, value=17)
            new_school = st.text_input("School", placeholder="e.g., ABC High School")
            new_notes = st.text_area("Notes (extracurricular activities, interests, etc.)")
            
            col_submit, col_cancel = st.columns(2)
            with col_submit:
                submitted = st.form_submit_button("Create Student", use_container_width=True, type="primary")
            with col_cancel:
                cancelled = st.form_submit_button("Cancel", use_container_width=True)
            
            if submitted:
                if not new_id or not new_name:
                    st.error("Please provide Student ID and Name")
                else:
                    try:
                        student = db_service.create_student(
                            student_id=new_id,
                            name=new_name,
                            age=new_age,
                            school=new_school,
                            notes=new_notes
                        )
                        st.success(f"Created student: {student.name}")
                        st.session_state['show_new_student_form'] = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error creating student: {e}")
            
            if cancelled:
                st.session_state['show_new_student_form'] = False
                st.rerun()
    
    # Navigation guide
    st.divider()
    st.markdown('<h2><i class="fas fa-compass icon"></i>Navigation Guide</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="nav-card">
            <i class="fas fa-users fa-2x"></i>
            <h3>Manage Students</h3>
            <p style="font-size: 0.9rem;">Add, edit, or import student data and grade records</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="nav-card">
            <i class="fas fa-chart-bar fa-2x"></i>
            <h3>Dashboard</h3>
            <p style="font-size: 0.9rem;">View grade trends and Grade 12 predictions</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class="nav-card">
            <i class="fas fa-clipboard-check fa-2x"></i>
            <h3>Career Assessment</h3>
            <p style="font-size: 0.9rem;">Complete RIASEC personality evaluation and get recommendations</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: gray; padding: 20px;'>
        <p>Powered by OpenAI GPT-4 • Linear Regression ML • Holland RIASEC Framework</p>
    </div>
    """, unsafe_allow_html=True)

else:
    st.error("Failed to initialize the application. Please check database connection.")

