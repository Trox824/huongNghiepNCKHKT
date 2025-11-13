"""
AI Career Guidance Chatbot Page
Interactive chatbot for students after RIASEC assessment
"""
import sys
import os
# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import streamlit as st
import pandas as pd
from datetime import datetime
from app.config.database import get_db_connection
from app.services.database_service import DatabaseService
from app.services.chatbot_service import StudentCareerChatbot, ChatMessage
import json

st.set_page_config(page_title="AI CỐ VẤN NGHỀ NGHIỆP", layout="centered")

# Styling
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stTextInput > div > div > input {
        border-radius: 8px;
    }
    .stButton > button {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Authentication guard
if 'user' not in st.session_state or not st.session_state['user']:
    st.warning("Vui lòng đăng nhập để truy cập tính năng này.")
    st.switch_page("main.py")
    st.stop()

# Get database connection
db = get_db_connection()
db_service = DatabaseService(db)

# Check if student is selected
if 'student_id' not in st.session_state or not st.session_state.get('student_id'):
    st.warning("Vui lòng chọn học sinh từ trang chủ trước")
    st.stop()

student_id = st.session_state['student_id']
user = st.session_state['user']

# Check access control: admin can access any student, regular users only their own
student = db_service.get_student_for_user(
    student_id=student_id,
    user_id=user['id'],
    is_admin=user.get('is_admin', False)
)

if not student:
    st.error(f"Bạn không có quyền truy cập học sinh này")
    st.stop()

# Check if student has completed RIASEC assessment
recommendation = db_service.get_student_recommendation(student_id)
if not recommendation:
    st.warning("Bạn chưa hoàn thành đánh giá RIASEC. Vui lòng vào trang 'Đánh giá nghề nghiệp' để thực hiện đánh giá trước.")
    st.stop()

# API Key from secrets
api_key = st.secrets.get("OPENAI_API_KEY", "")

if not api_key:
    st.error("OpenAI API Key chưa được cấu hình. Vui lòng thêm vào .streamlit/secrets.toml")
    st.stop()

# Initialize chatbot
if 'chatbot' not in st.session_state:
    st.session_state.chatbot = StudentCareerChatbot(api_key, db_service)

# Initialize conversation history
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

# Sidebar - Student Info
with st.sidebar:
    st.title("AI Cố Vấn")
    st.divider()

    st.subheader("Tài liệu PDF để tham khảo")
    uploaded_pdf = st.file_uploader("Tải lên tệp PDF (tùy chọn)", type=["pdf"])
    col_up1, col_up2 = st.columns(2)
    with col_up1:
        if uploaded_pdf is not None and st.button("Sử dụng PDF", use_container_width=True):
            try:
                st.session_state.chatbot.ingest_pdf(uploaded_pdf.read(), uploaded_pdf.name)
                st.success(f"Đã thêm: {uploaded_pdf.name}")
            except Exception as e:
                st.error(f"Không thể xử lý PDF: {e}")
    with col_up2:
        if st.button("Xóa PDF", use_container_width=True, type="secondary"):
            st.session_state.chatbot.clear_document()
            st.info("Đã xóa tài liệu đang dùng")
    # Show current document status
    if getattr(st.session_state.chatbot, 'document_name', None):
        st.caption(f"Đang dùng tài liệu: {st.session_state.chatbot.document_name}")

    st.subheader("Thông tin học sinh")
    st.write(f"**{student.name}**")

    st.divider()

    st.subheader("Hồ sơ RIASEC")
    st.metric("Mã Holland", recommendation.riasec_profile)

    recommended_paths = json.loads(recommendation.recommended_paths)
    st.metric("Số nghề đề xuất", len(recommended_paths))
    st.metric("Độ tin cậy", f"{recommendation.confidence_score:.0%}")

    with st.expander("Chi tiết"):
        st.write("**Nghề nghiệp đề xuất:**")
        for path in recommended_paths:
            st.write(f"- {path}")
        st.write(f"**Phân tích:** {recommendation.summary}")

    st.divider()

    st.subheader("Câu hỏi gợi ý")
    suggestions = [
        "Tôi phù hợp với nghề gì nhất?",
        "Làm sao để phát triển kỹ năng?",
        "Tôi nên học thêm gì?",
        "Giải thích mã Holland của tôi"
    ]

    for i, suggestion in enumerate(suggestions):
        if st.button(suggestion, key=f"suggestion_{i}", use_container_width=True):
            st.session_state.user_input = suggestion
            st.rerun()

    st.divider()

    if st.button("Xóa lịch sử trò chuyện", use_container_width=True, type="secondary"):
        st.session_state.conversation_history = []
        st.session_state.chatbot.clear_conversation()
        st.rerun()

    with st.expander("Mẹo sử dụng"):
        st.markdown("""
**Cách sử dụng:**
- Hỏi cụ thể và rõ ràng
- Chatbot nhớ ngữ cảnh
- Dùng gợi ý để bắt đầu

**Chatbot có thể:**
- Giải thích RIASEC
- Tư vấn nghề nghiệp
- Gợi ý phát triển
- Định hướng tương lai
""")

# Main chat area
st.title("Trò chuyện với AI")

# Display conversation history
if st.session_state.conversation_history:
    for message in st.session_state.conversation_history:
        with st.chat_message(message['role']):
            st.write(message['content'])
            st.caption(message['timestamp'])

            # Display suggestions if available
            if message['role'] == 'assistant' and 'suggestions' in message and message['suggestions']:
                st.markdown("**Gợi ý câu hỏi tiếp theo:**")
                for suggestion in message['suggestions']:
                    st.markdown(f"- {suggestion}")
else:
    # Welcome message
    with st.chat_message("assistant"):
        st.write(f"**Xin chào {student.name}!**")
        st.write("""
Tôi là AI Cố vấn nghề nghiệp của bạn. Dựa trên kết quả đánh giá RIASEC, tôi có thể giúp bạn:

- Hiểu rõ hơn về tính cách nghề nghiệp
- Khám phá các nghề nghiệp phù hợp
- Lời khuyên về học tập và phát triển kỹ năng
- Lập kế hoạch nghề nghiệp tương lai

Hãy đặt câu hỏi bất kỳ về nghề nghiệp, học tập, hoặc định hướng tương lai!
""")

# Chat input
user_input = st.chat_input("Nhập câu hỏi của bạn...", key="user_input_field")

# Use suggestion if set
if 'user_input' in st.session_state and st.session_state.user_input:
    user_input = st.session_state.user_input
    del st.session_state.user_input

# Process user input
if user_input and user_input.strip():
    with st.spinner("AI đang suy nghĩ..."):
        try:
            # Generate response
            response = st.session_state.chatbot.generate_response(student_id, user_input)

            # Add to conversation history
            st.session_state.conversation_history.append({
                'role': 'user',
                'content': user_input,
                'timestamp': datetime.now().strftime("%H:%M")
            })

            st.session_state.conversation_history.append({
                'role': 'assistant',
                'content': response.message,
                'suggestions': response.suggestions,
                'timestamp': datetime.now().strftime("%H:%M")
            })

            st.rerun()

        except Exception as e:
            st.error(f"Lỗi: {str(e)}")
