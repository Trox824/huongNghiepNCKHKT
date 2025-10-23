# AI Career Guidance Chatbot

## Overview

The AI Career Guidance Chatbot is an intelligent conversational interface that provides personalized career counseling to students based on their RIASEC (Holland Code) assessment results. The chatbot leverages OpenAI's GPT-4o-mini model to deliver contextual, helpful advice about career paths, skill development, and educational planning.

## Features

### 🤖 **Intelligent Context Awareness**

- Accesses complete student profile including academic history, grades, and predictions
- Integrates RIASEC assessment results and career recommendations
- Maintains conversation context throughout the session
- Provides personalized responses based on individual student data

### 💬 **Natural Conversation Interface**

- Clean, modern chat interface with message bubbles
- Real-time conversation history display
- Quick suggestion buttons for common questions
- Conversation management (clear history, view profile)

### 🎯 **Comprehensive Career Guidance**

- Explains RIASEC results in student-friendly language
- Suggests specific career paths based on personality profile
- Provides actionable advice for skill development
- Offers guidance on educational planning and preparation

### 📊 **Rich Student Context**

- Academic performance analysis (Grades 1-11)
- Grade 12 predictions with confidence intervals
- Detailed RIASEC assessment responses
- Career recommendation summaries
- Student notes and extracurricular activities

## Technical Architecture

### Core Components

1. **StudentCareerChatbot Service** (`app/services/chatbot_service.py`)

   - Main chatbot logic and OpenAI API integration
   - Student context retrieval and formatting
   - Conversation management and history
   - Response generation with structured output

2. **Chatbot UI** (`app/pages/4_AI_Chatbot.py`)

   - Streamlit-based chat interface
   - Real-time message display
   - Input handling and suggestion system
   - Integration with existing student management system

3. **Database Integration**
   - Seamless access to student data via DatabaseService
   - RIASEC assessment results and recommendations
   - Academic history and predictions
   - Framework questions and responses

### Data Flow

```
Student Context → Chatbot Service → OpenAI API → Structured Response → UI Display
     ↓
Database Service ← Student Data ← RIASEC Assessment ← Career Framework
```

## Usage Guide

### Prerequisites

1. Student must have completed RIASEC assessment
2. OpenAI API key must be provided
3. Student must be selected in the main application

### Getting Started

1. **Complete RIASEC Assessment**

   - Navigate to "Đánh giá nghề nghiệp" page
   - Run the RIASEC assessment for the selected student
   - Ensure assessment is completed successfully

2. **Access AI Chatbot**

   - Go to "AI Cố vấn" page from the main navigation
   - Or click "Mở AI Cố vấn" button from career assessment results
   - Enter OpenAI API key if not already configured

3. **Start Conversation**
   - Use suggested questions or type your own
   - Ask about career paths, skill development, or educational planning
   - AI will provide personalized responses based on your RIASEC profile

### Sample Questions

**Career Exploration:**

- "Tôi phù hợp với nghề gì nhất?"
- "Giải thích mã Holland của tôi"
- "Nghề lập trình viên có phù hợp với tôi không?"

**Skill Development:**

- "Làm sao để phát triển kỹ năng cho nghề nghiệp?"
- "Tôi nên học thêm gì để chuẩn bị cho tương lai?"
- "Kỹ năng nào quan trọng nhất cho nghề của tôi?"

**Educational Planning:**

- "Tôi nên chọn ngành học gì ở đại học?"
- "Làm thế nào để chuẩn bị cho nghề nghiệp tương lai?"
- "Có trường đại học nào phù hợp với tôi không?"

## API Integration

### OpenAI Configuration

- **Model:** GPT-4o-mini (cost-effective, high-quality responses)
- **Temperature:** 0.7 (balanced creativity and consistency)
- **Structured Output:** Pydantic models for consistent response format
- **Context Management:** System prompts with comprehensive student data

### Response Structure

```python
class ChatbotResponse(BaseModel):
    message: str                    # Main response text
    suggestions: List[str]         # Follow-up question suggestions
    related_topics: List[str]       # Related topics for exploration
    confidence: float              # Response confidence score
```

## Security & Privacy

- **API Key Management:** Secure handling of OpenAI API keys
- **Data Privacy:** Student data remains within the application
- **Session Management:** Conversation history cleared on demand
- **Access Control:** Requires completed RIASEC assessment

## Performance Optimization

- **Caching:** Streamlit resource caching for chatbot service
- **Context Length:** Manages conversation history (last 10 messages)
- **Parallel Processing:** Efficient student context retrieval
- **Error Handling:** Graceful fallbacks for API failures

## Future Enhancements

### Planned Features

- **Multi-language Support:** Vietnamese and English conversation
- **Voice Interface:** Speech-to-text and text-to-speech capabilities
- **Advanced Analytics:** Conversation insights and student engagement metrics
- **Integration:** Connect with external career databases and job markets

### Technical Improvements

- **Response Caching:** Cache common responses to reduce API costs
- **Context Compression:** Optimize context length for better performance
- **Custom Models:** Fine-tuned models for educational counseling
- **Real-time Updates:** Live updates when student data changes

## Troubleshooting

### Common Issues

1. **"Không thể tìm thấy thông tin của bạn"**

   - Ensure student has completed RIASEC assessment
   - Check if student is properly selected in main application

2. **API Key Errors**

   - Verify OpenAI API key is valid and has sufficient credits
   - Check API key format and permissions

3. **Slow Response Times**

   - Check internet connection
   - Verify OpenAI API status
   - Consider reducing context length if needed

4. **Empty Conversation History**
   - Refresh the page to reload conversation state
   - Check if session state is properly maintained

### Debug Mode

Enable debug logging by setting log level to DEBUG in the logger configuration to see detailed API interactions and context processing.

## Contributing

When extending the chatbot functionality:

1. **Maintain Context Integrity:** Ensure all student data is properly formatted
2. **Follow Response Structure:** Use Pydantic models for consistent output
3. **Handle Errors Gracefully:** Provide meaningful error messages to users
4. **Test Thoroughly:** Verify responses with various student profiles
5. **Document Changes:** Update this README when adding new features

## Support

For technical support or feature requests:

- Check the main application logs for detailed error information
- Verify database connectivity and student data integrity
- Test with sample student data to isolate issues
- Review OpenAI API documentation for integration questions
