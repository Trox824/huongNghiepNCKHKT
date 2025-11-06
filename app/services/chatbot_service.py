"""
AI Chatbot Service for Student Career Guidance
Provides contextual conversations based on RIASEC assessment results
"""
import openai
from pydantic import BaseModel
from typing import List, Dict, Optional, Literal
import pandas as pd
from datetime import datetime
from app.services.logger import logger
from app.services.database_service import DatabaseService
import json
import streamlit as st
from io import BytesIO
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
try:
    from pypdf import PdfReader
except Exception:
    PdfReader = None


class ChatMessage(BaseModel):
    """Chat message structure"""
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime = datetime.now()


class ChatbotResponse(BaseModel):
    """Structured chatbot response"""
    message: str
    suggestions: List[str] = []
    related_topics: List[str] = []
    confidence: float = 0.8


class StudentCareerChatbot:
    """AI-powered chatbot for student career guidance based on RIASEC assessment"""
    
    def __init__(self, api_key: str, db_service: DatabaseService):
        self.client = openai.OpenAI(api_key=api_key)
        self.db_service = db_service
        self.conversation_history: List[ChatMessage] = []
        # Document QA state
        self.document_name: Optional[str] = None
        self.document_chunks: List[str] = []
        self._vectorizer: Optional[TfidfVectorizer] = None
        self._tfidf_matrix = None
        
    def get_student_context(self, student_id: str) -> Dict:
        """Get comprehensive student context for chatbot"""
        try:
            # Get student basic info
            student = self.db_service.get_student(student_id)
            if not student:
                return {}
            
            # Get academic data
            grades_df = self.db_service.get_student_grades_df(student_id)
            predictions_df = self.db_service.get_student_predictions_df(student_id)
            
            # Get RIASEC assessment results
            assessments = self.db_service.get_student_assessments(student_id)
            recommendation = self.db_service.get_student_recommendation(student_id)
            
            # Get framework questions for context
            framework_df = self.db_service.get_framework_df()
            
            # Format assessment responses
            assessment_responses = []
            for assessment in assessments:
                question = framework_df[framework_df['id'] == assessment.question_id]
                if not question.empty:
                    q = question.iloc[0]
                    assessment_responses.append({
                        'riasec_code': q['riasec_code'],
                        'category': q['career_category'],
                        'question': q['question'],
                        'answer': assessment.answer,
                        'reasoning': assessment.reasoning
                    })
            
            # Calculate RIASEC scores
            riasec_scores = self._calculate_riasec_scores(assessment_responses, framework_df)
            
            context = {
                'student': {
                    'id': student.id,
                    'name': student.name,
                    'age': student.age,
                    'school': student.school,
                    'notes': student.notes or ''
                },
                'academic_profile': self._format_academic_profile(grades_df, predictions_df),
                'riasec_profile': {
                    'scores': riasec_scores,
                    'top_codes': sorted(riasec_scores.items(), key=lambda x: x[1], reverse=True)[:3],
                    'assessment_responses': assessment_responses
                },
                'career_recommendation': {
                    'riasec_profile': recommendation.riasec_profile if recommendation else '',
                    'recommended_paths': json.loads(recommendation.recommended_paths) if recommendation else [],
                    'summary': recommendation.summary if recommendation else '',
                    'confidence_score': recommendation.confidence_score if recommendation else 0.0
                } if recommendation else None
            }
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting student context: {e}")
            return {}
    
    def generate_response(self, student_id: str, user_message: str) -> ChatbotResponse:
        """Generate contextual response based on student's RIASEC assessment"""
        try:
            # Get student context
            context = self.get_student_context(student_id)
            if not context:
                return ChatbotResponse(
                    message="Xin lỗi, tôi không thể tìm thấy thông tin của bạn. Vui lòng đảm bảo bạn đã hoàn thành đánh giá RIASEC.",
                    confidence=0.0
                )
            
            # Add user message to conversation history
            self.conversation_history.append(ChatMessage(role="user", content=user_message))
            
            # Create system prompt with student context
            system_prompt = self._create_system_prompt(context)

            # If a document is available, retrieve relevant chunks and add to context
            doc_context = self._retrieve_relevant_context(user_message)
            if doc_context:
                system_prompt += "\n\nTHÔNG TIN TỪ TÀI LIỆU ĐÍNH KÈM (ưu tiên trích dẫn):\n" + doc_context
            
            # Prepare conversation for API
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add recent conversation history (last 10 messages to manage context length)
            recent_history = self.conversation_history[-10:]
            for msg in recent_history:
                messages.append({"role": msg.role, "content": msg.content})
            
            # Call OpenAI API
            response = self.client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=messages,
                response_format=ChatbotResponse,
                temperature=0.7
            )
            
            chatbot_response = response.choices[0].message.parsed
            
            # Add assistant response to conversation history
            self.conversation_history.append(ChatMessage(role="assistant", content=chatbot_response.message))
            
            logger.info(f"Generated chatbot response for student {student_id}")
            return chatbot_response
            
        except Exception as e:
            logger.error(f"Error generating chatbot response: {e}")
            return ChatbotResponse(
                message="Xin lỗi, có lỗi xảy ra khi xử lý câu hỏi của bạn. Vui lòng thử lại sau.",
                confidence=0.0
            )

    def ingest_pdf(self, file_bytes: bytes, filename: str) -> None:
        """Ingest a PDF file, split into chunks, and build a retrieval index."""
        try:
            if PdfReader is None:
                raise RuntimeError("Thiếu thư viện pypdf. Vui lòng cài đặt 'pypdf'.")

            reader = PdfReader(BytesIO(file_bytes))
            raw_text_parts: List[str] = []
            for page in reader.pages:
                text = page.extract_text() or ""
                cleaned = " ".join(text.split())
                if cleaned:
                    raw_text_parts.append(cleaned)

            full_text = "\n".join(raw_text_parts)
            chunks = self._chunk_text(full_text, max_chars=1200, overlap=150)

            self.document_name = filename
            self.document_chunks = chunks
            self._build_index()
            logger.info(f"Ingested PDF '{filename}' with {len(chunks)} chunks")
        except Exception as e:
            logger.error(f"Error ingesting PDF: {e}")
            raise

    def clear_document(self) -> None:
        """Clear current ingested document and index."""
        self.document_name = None
        self.document_chunks = []
        self._vectorizer = None
        self._tfidf_matrix = None
        logger.info("Cleared ingested document context")

    def _chunk_text(self, text: str, max_chars: int = 1200, overlap: int = 150) -> List[str]:
        """Simple recursive chunker by characters with overlap to preserve context."""
        if not text:
            return []
        chunks: List[str] = []
        start = 0
        n = len(text)
        while start < n:
            end = min(start + max_chars, n)
            chunk = text[start:end]
            chunks.append(chunk)
            if end == n:
                break
            start = max(0, end - overlap)
        return chunks

    def _build_index(self) -> None:
        """Build TF-IDF index for current document chunks."""
        if not self.document_chunks:
            self._vectorizer = None
            self._tfidf_matrix = None
            return
        self._vectorizer = TfidfVectorizer(stop_words='english')
        self._tfidf_matrix = self._vectorizer.fit_transform(self.document_chunks)

    def _retrieve_relevant_context(self, query: str, top_k: int = 4) -> str:
        """Retrieve top-k relevant chunks concatenated as context."""
        try:
            if not self.document_chunks or self._vectorizer is None or self._tfidf_matrix is None:
                return ""
            query_vec = self._vectorizer.transform([query])
            sims = cosine_similarity(query_vec, self._tfidf_matrix).flatten()
            if sims.size == 0:
                return ""
            top_indices = sims.argsort()[::-1][:top_k]
            selected = [self.document_chunks[i] for i in top_indices if sims[i] > 0]
            if not selected:
                return ""
            header = f"(Nguồn: {self.document_name})\n"
            joined = "\n---\n".join(selected)
            return header + joined
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return ""
    
    def _create_system_prompt(self, context: Dict) -> str:
        """Create comprehensive system prompt with student context"""
        student = context['student']
        academic_profile = context['academic_profile']
        riasec_profile = context['riasec_profile']
        career_rec = context['career_recommendation']
        
        # Format RIASEC scores
        riasec_scores_text = "\n".join([
            f"- {code} ({self._get_riasec_name(code)}): {score:.1f}/100"
            for code, score in riasec_profile['scores'].items()
        ])
        
        # Format top RIASEC codes
        top_codes_text = ", ".join([f"{code} ({self._get_riasec_name(code)})" for code, _ in riasec_profile['top_codes']])
        
        # Format assessment responses
        assessment_text = ""
        for resp in riasec_profile['assessment_responses']:
            assessment_text += f"\n- {resp['question']}\n  Trả lời: {resp['answer']}\n  Lý do: {resp['reasoning']}\n"
        
        system_prompt = f"""Bạn là một cố vấn nghề nghiệp AI thông minh và thân thiện, chuyên giúp học sinh định hướng nghề nghiệp dựa trên kết quả đánh giá RIASEC.

THÔNG TIN HỌC SINH:
- Tên: {student['name']}
- Tuổi: {student['age']}
- Trường: {student['school']}
- Ghi chú: {student['notes']}

HỒ SƠ HỌC TẬP:
{academic_profile}

KẾT QUẢ ĐÁNH GIÁ RIASEC:
Điểm số từng loại tính cách:
{riasec_scores_text}

Top 3 tính cách nổi bật: {top_codes_text}

Chi tiết đánh giá:
{assessment_text}

GỢI Ý NGHỀ NGHIỆP:
"""
        
        if career_rec:
            recommended_paths = ", ".join(career_rec['recommended_paths'])
            system_prompt += f"""
- Mã Holland: {career_rec['riasec_profile']}
- Con đường nghề nghiệp đề xuất: {recommended_paths}
- Độ tin cậy: {career_rec['confidence_score']:.0%}
- Phân tích chi tiết: {career_rec['summary']}
"""
        else:
            system_prompt += "\n- Chưa có gợi ý nghề nghiệp cụ thể"
        
        system_prompt += """

NHIỆM VỤ CỦA BẠN:
1. Trả lời câu hỏi của học sinh một cách thân thiện, chính xác và hữu ích
2. Sử dụng thông tin RIASEC để giải thích tại sao học sinh phù hợp với các nghề nghiệp cụ thể
3. Đưa ra lời khuyên thực tế về cách phát triển kỹ năng và chuẩn bị cho nghề nghiệp
4. Khuyến khích học sinh khám phá các lĩnh vực phù hợp với tính cách của họ
5. Trả lời bằng tiếng Việt, giọng điệu thân thiện và động viên

CÁCH TRẢ LỜI:
- Luôn tham chiếu đến kết quả RIASEC của học sinh
- Đưa ra ví dụ cụ thể về nghề nghiệp và công việc
- Gợi ý các bước tiếp theo để phát triển nghề nghiệp
- Khuyến khích học sinh đặt câu hỏi thêm

Hãy trả lời câu hỏi của học sinh một cách chi tiết và hữu ích."""

        return system_prompt
    
    def _format_academic_profile(self, grades_df: pd.DataFrame, predictions_df: pd.DataFrame) -> str:
        """Format academic profile for context"""
        profile = "Lịch sử điểm số:\n"
        
        if not grades_df.empty:
            # Group by subject
            for subject in sorted(grades_df['subject'].unique()):
                subject_grades = grades_df[grades_df['subject'] == subject].sort_values('grade_level')
                grades_str = ", ".join([
                    f"Lớp {int(row['grade_level'])}: {row['score']:.1f}"
                    for _, row in subject_grades.iterrows()
                ])
                avg_score = subject_grades['score'].mean()
                profile += f"- {subject}: {grades_str} (Trung bình: {avg_score:.1f})\n"
        
        if not predictions_df.empty:
            profile += "\nDự đoán điểm Lớp 12:\n"
            for _, pred in predictions_df.iterrows():
                profile += f"- {pred['subject']}: {pred['predicted_score']:.1f}\n"
        
        return profile
    
    def _calculate_riasec_scores(self, assessment_responses: List[Dict], framework_df: pd.DataFrame) -> Dict[str, float]:
        """Calculate RIASEC scores from assessment responses"""
        riasec_scores = {'R': 0.0, 'I': 0.0, 'A': 0.0, 'S': 0.0, 'E': 0.0, 'C': 0.0}
        riasec_weights = {code: 0.0 for code in riasec_scores.keys()}
        
        for resp in assessment_responses:
            code = resp['riasec_code']
            # Find weight from framework
            question_row = framework_df[framework_df['riasec_code'] == code]
            if not question_row.empty:
                weight = float(question_row.iloc[0]['weight'])
            else:
                weight = 1.0
            
            # Calculate score contribution
            if resp['answer'] == 'Yes':
                score = 1.0
            elif resp['answer'] == 'Partial':
                score = 0.5
            else:
                score = 0.0
            
            riasec_scores[code] += score * weight
            riasec_weights[code] += weight
        
        # Normalize scores
        for code in riasec_scores.keys():
            if riasec_weights[code] > 0:
                riasec_scores[code] = (riasec_scores[code] / riasec_weights[code]) * 100
        
        return riasec_scores
    
    def _get_riasec_name(self, code: str) -> str:
        """Get full name for RIASEC code"""
        names = {
            'R': 'Thực tế',
            'I': 'Điều tra',
            'A': 'Nghệ thuật',
            'S': 'Xã hội',
            'E': 'Doanh nghiệp',
            'C': 'Truyền thống'
        }
        return names.get(code, code)
    
    def clear_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("Cleared chatbot conversation history")
    
    def get_conversation_summary(self) -> str:
        """Get summary of current conversation"""
        if not self.conversation_history:
            return "Chưa có cuộc trò chuyện nào."
        
        user_messages = [msg.content for msg in self.conversation_history if msg.role == "user"]
        return f"Đã có {len(user_messages)} câu hỏi trong cuộc trò chuyện này."


@st.cache_resource
def get_chatbot_service(_api_key: str, _db_service: DatabaseService):
    """Get cached chatbot service instance"""
    return StudentCareerChatbot(_api_key, _db_service)
