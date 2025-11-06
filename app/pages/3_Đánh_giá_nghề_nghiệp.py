"""
Career Assessment Page - RIASEC evaluation using LLM
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
from app.services.career_service import CareerAssessmentService
import plotly.graph_objects as go

st.set_page_config(page_title="ĐÁNH GIÁ NGHỀ NGHIỆP", layout="wide")

# Add Font Awesome
st.markdown("""
<style>
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
    .icon { margin-right: 8px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1><i class="fas fa-clipboard-check icon"></i>ĐÁNH GIÁ NGHỀ NGHIỆP RIASEC</h1>', unsafe_allow_html=True)
st.markdown("ĐÁNH GIÁ CON ĐƯỜNG NGHỀ NGHIỆP SỬ DỤNG KHUNG HOLLAND CODE")

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

# Get student data
grades_df = db_service.get_student_grades_df(student_id)
predictions_df = db_service.get_student_predictions_df(student_id)

if grades_df.empty:
    st.warning("KHÔNG TÌM THẤY BẢN GHI ĐIỂM. VUI LÒNG THÊM ĐIỂM TRƯỚC.")
    st.stop()

if predictions_df.empty:
    st.warning("KHÔNG TÌM THẤY DỰ ĐOÁN. VUI LÒNG VÀO BẢNG ĐIỀU KHIỂN ĐỂ TẠO DỰ ĐOÁN.")
    st.stop()

# Get framework
framework_df = db_service.get_framework_df()

if framework_df.empty:
    st.error("CHƯA TẢI KHUNG RIASEC. VUI LÒNG KIỂM TRA CƠ SỞ DỮ LIỆU.")
    st.stop()

# Student header
st.subheader(f"ĐÁNH GIÁ CHO: {student.name}")

# API Key from secrets
api_key = st.secrets.get("OPENAI_API_KEY", "")

if not api_key:
    st.error("OPENAI API KEY chưa được cấu hình. Vui lòng thêm vào .streamlit/secrets.toml")
    st.stop()

# RIASEC explanation
with st.expander("VỀ RIASEC (MÃ HOLLAND)"):
    st.markdown("""
    **MÃ HOLLAND** (RIASEC) LÀ MỘT ĐÁNH GIÁ SỞ THÍCH NGHỀ NGHIỆP PHÂN LOẠI CON NGƯỜI THÀNH SÁU LOẠI TÍNH CÁCH:
    
    - **R - REALISTIC (THỰC TẾ)**: CÔNG VIỆC THỰC HÀNH, KỸ THUẬT (KỸ SƯ, THỢ MÁY, CÔNG NHÂN XÂY DỰNG)
    - **I - INVESTIGATIVE (ĐIỀU TRA)**: CÔNG VIỆC PHÂN TÍCH, KHOA HỌC, NGHIÊN CỨU (NHÀ KHOA HỌC, NHÀ PHÂN TÍCH, NHÀ NGHIÊN CỨU)
    - **A - ARTISTIC (NGHỆ THUẬT)**: CÔNG VIỆC SÁNG TẠO, BIỂU HIỆN (NGHỆ SĨ, NHÀ VĂN, NHÀ THIẾT KẾ)
    - **S - SOCIAL (XÃ HỘI)**: CÔNG VIỆC GIÚP ĐỠ, DẠY HỌC, PHỤC VỤ (GIÁO VIÊN, CỐ VẤN, Y TẾ)
    - **E - ENTERPRISING (DOANH NGHIỆP)**: CÔNG VIỆC LÃNH ĐẠO, THUYẾT PHỤC, KINH DOANH (QUẢN LÝ, DOANH NHÂN, BÁN HÀNG)
    - **C - CONVENTIONAL (TRUYỀN THỐNG)**: CÔNG VIỆC CÓ TỔ CHỨC, CHÚ Ý CHI TIẾT, HỆ THỐNG (KẾ TOÁN, QUẢN TRỊ VIÊN, PHÂN TÍCH VIÊN)
    
    KẾT QUẢ CỦA BẠN SẼ HIỂN THỊ 3 MÃ HÀNG ĐẦU, TẠO THÀNH HỒ SƠ TÍNH CÁCH NGHỀ NGHIỆP CỦA BẠN.
    """)

st.divider()

# Run assessment button
if st.button("BẮT ĐẦU ĐÁNH GIÁ RIASEC", type="primary", use_container_width=True):
    
    career_service = CareerAssessmentService(api_key)
    
    # Prepare student profile
    student_dict = {
        'name': student.name,
        'age': student.age,
        'school': student.school,
        'notes': student.notes or ''
    }
    
    # Format student profile
    student_profile = career_service._format_student_profile(
        student_dict, grades_df, predictions_df
    )
    
    # Phase 1: Evaluate all questions
    st.subheader("GIAI ĐOẠN 1: ĐÁNH GIÁ CÂU HỎI")
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_questions = len(framework_df)
    status_text.text(f"ĐANG ĐÁNH GIÁ {total_questions} CÂU HỎI...")
    
    with st.spinner("ĐANG ĐÁNH GIÁ CÂU HỎI SONG SONG..."):
        responses = career_service.evaluate_all_questions(
            student.name,
            student_profile,
            framework_df,
            max_workers=5
        )
    
    progress_bar.progress(100)
    status_text.text(f"ĐÃ HOÀN THÀNH {len(responses)} ĐÁNH GIÁ CÂU HỎI")
    
    # Save responses to database
    db_service.save_assessment_responses(student_id, responses)
    
    # Calculate RIASEC scores
    riasec_scores = career_service.calculate_riasec_scores(responses, framework_df)
    
    # Phase 2: Generate final recommendation
    st.subheader("GIAI ĐOẠN 2: GỢI Ý NGHỀ NGHIỆP CUỐI CÙNG")
    
    with st.spinner("ĐANG TẠO GỢI Ý NGHỀ NGHIỆP CÁ NHÂN HÓA..."):
        recommendation = career_service.generate_final_recommendation(
            student.name,
            student_profile,
            responses,
            framework_df,
            riasec_scores
        )
    
    # Save recommendation to database
    db_service.save_career_recommendation(student_id, recommendation)
    
    # Store in session state
    st.session_state['assessment_complete'] = True
    st.session_state['riasec_scores'] = riasec_scores
    st.session_state['recommendation'] = recommendation
    st.session_state['assessment_responses'] = responses
    
    st.success("ĐÁNH GIÁ HOÀN THÀNH!")
    st.rerun()

# Display results if assessment is complete
if st.session_state.get('assessment_complete', False):
    
    st.divider()
    st.header("KẾT QUẢ ĐÁNH GIÁ")
    
    riasec_scores = st.session_state.get('riasec_scores', {})
    recommendation = st.session_state.get('recommendation', {})
    responses = st.session_state.get('assessment_responses', [])
    
    # RIASEC Profile Visualization
    st.subheader("HỒ SƠ RIASEC CỦA BẠN")
    
    # Create radar chart
    categories = ['THỰC TẾ', 'ĐIỀU TRA', 'NGHỆ THUẬT', 'XÃ HỘI', 'DOANH NGHIỆP', 'TRUYỀN THỐNG']
    values = [riasec_scores.get(code, 0) for code in ['R', 'I', 'A', 'S', 'E', 'C']]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name=student.name,
        line_color='#1f77b4',
        fillcolor='rgba(31, 119, 180, 0.3)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=False,
        title="HỒ SƠ TÍNH CÁCH RIASEC",
        height=500
    )
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### ĐIỂM SỐ")
        sorted_scores = sorted(riasec_scores.items(), key=lambda x: x[1], reverse=True)
        for code, score in sorted_scores:
            name = {'R': 'THỰC TẾ', 'I': 'ĐIỀU TRA', 'A': 'NGHỆ THUẬT',
                   'S': 'XÃ HỘI', 'E': 'DOANH NGHIỆP', 'C': 'TRUYỀN THỐNG'}[code]
            st.metric(f"{code} - {name}", f"{score:.1f}/100")
    
    # Career Recommendations
    st.divider()
    st.subheader("CON ĐƯỜNG NGHỀ NGHIỆP ĐỀ XUẤT")
    
    riasec_profile = recommendation.get('riasec_profile', '')
    st.info(f"**MÃ HOLLAND CỦA BẠN:** {riasec_profile}")
    
    recommended_paths = recommendation.get('recommended_paths', [])
    
    if recommended_paths:
        cols = st.columns(len(recommended_paths))
        for i, path in enumerate(recommended_paths):
            with cols[i]:
                st.success(f"**{i+1}. {path}**")
    
    # Confidence score
    confidence = recommendation.get('confidence_score', 0.0)
    st.progress(confidence)
    st.caption(f"ĐỘ TIN CẬY: {confidence:.0%}")
    
    # Detailed summary
    st.divider()
    st.subheader("📝 PHÂN TÍCH CHI TIẾT")
    summary = recommendation.get('summary', '')
    st.markdown(summary)
    
    # Question breakdown
    st.divider()
    st.subheader("📋 CHI TIẾT TỪNG CÂU HỎI")
    
    # Group responses by RIASEC code
    riasec_groups = {'R': [], 'I': [], 'A': [], 'S': [], 'E': [], 'C': []}
    
    for resp in responses:
        question_row = framework_df[framework_df['id'] == resp['question_id']]
        if not question_row.empty:
            code = question_row.iloc[0]['riasec_code']
            riasec_groups[code].append((question_row.iloc[0]['question'], resp))
    
    # Display by category
    riasec_names = {
        'R': 'THỰC TẾ (THỰC HÀNH/KỸ THUẬT)',
        'I': 'ĐIỀU TRA (PHÂN TÍCH/KHOA HỌC)',
        'A': 'NGHỆ THUẬT (SÁNG TẠO/BIỂU HIỆN)',
        'S': 'XÃ HỘI (GIÚP ĐỠ/PHỤC VỤ)',
        'E': 'DOANH NGHIỆP (LÃNH ĐẠO/KINH DOANH)',
        'C': 'TRUYỀN THỐNG (TỔ CHỨC/HỆ THỐNG)'
    }
    
    for code in ['R', 'I', 'A', 'S', 'E', 'C']:
        if riasec_groups[code]:
            with st.expander(f"{code} - {riasec_names[code]} ({len(riasec_groups[code])} CÂU HỎI)", expanded=False):
                for question_text, resp in riasec_groups[code]:
                    answer_text = {
                        'Yes': '[CÓ]',
                        'Partial': '[PHẦN NÀO]',
                        'No': '[KHÔNG]',
                        'Error': '[LỖI]'
                    }.get(resp['answer'], '[N/A]')
                    
                    st.markdown(f"**CÂU HỎI:** {question_text}")
                    st.markdown(f"**TRẢ LỜI:** {answer_text} {resp['answer']}")
                    st.markdown(f"*LÝ DO:* {resp['reasoning']}")
                    st.divider()
    
    # Download options
    st.divider()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Download assessment results
        results_data = {
            'ten_hoc_sinh': student.name,
            'ma_hoc_sinh': student_id,
            'ho_so_riasec': riasec_profile,
            'con_duong_de_xuat': ', '.join(recommended_paths),
            'do_tin_cay': confidence,
            **{f'diem_{code}': score for code, score in riasec_scores.items()}
        }
        results_df = pd.DataFrame([results_data])
        csv = results_df.to_csv(index=False)
        st.download_button(
            label="TẢI XUỐNG TÓM TẮT ĐÁNH GIÁ",
            data=csv,
            file_name=f"danh_gia_riasec_{student_id}.csv",
            mime="text/csv"
        )
    
    with col2:
        # Download detailed responses
        responses_data = []
        for resp in responses:
            question_row = framework_df[framework_df['id'] == resp['question_id']]
            if not question_row.empty:
                q = question_row.iloc[0]
                responses_data.append({
                    'ma_riasec': q['riasec_code'],
                    'danh_muc': q['career_category'],
                    'cau_hoi': q['question'],
                    'tra_loi': resp['answer'],
                    'ly_do': resp['reasoning']
                })
        
        responses_df = pd.DataFrame(responses_data)
        csv = responses_df.to_csv(index=False)
        st.download_button(
            label="TẢI XUỐNG CÂU TRẢ LỜI CHI TIẾT",
            data=csv,
            file_name=f"tra_loi_riasec_{student_id}.csv",
            mime="text/csv"
        )
    
    with col3:
        # Link to AI Chatbot
        st.markdown("### TƯ VẤN THÊM")
        st.markdown("**Trò chuyện với AI để được tư vấn chi tiết hơn về nghề nghiệp của bạn!**")
        if st.button("MỞ AI CỐ VẤN", type="primary", use_container_width=True):
            st.success("Chuyển đến trang AI Cố vấn để trò chuyện!")
            st.info("AI sẽ sử dụng kết quả RIASEC của bạn để đưa ra lời khuyên cá nhân hóa.")

else:
    st.info("NHẤP NÚT BÊN TRÊN ĐỂ BẮT ĐẦU ĐÁNH GIÁ")

