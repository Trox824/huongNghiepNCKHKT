"""
Career Assessment Page - RIASEC evaluation using LLM
"""
import streamlit as st
import pandas as pd
from app.config.database import get_db_connection
from app.services.database_service import DatabaseService
from app.services.career_service import CareerAssessmentService
import plotly.graph_objects as go

st.set_page_config(page_title="Career Assessment", page_icon="🎯", layout="wide")

# Add Font Awesome
st.markdown("""
<style>
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
    .icon { margin-right: 8px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1><i class="fas fa-clipboard-check icon"></i>RIASEC Career Assessment</h1>', unsafe_allow_html=True)
st.markdown("Evaluate career paths using the Holland Code framework")

# Get database connection
db = get_db_connection()
db_service = DatabaseService(db)

# Check if student is selected
if 'student_id' not in st.session_state or not st.session_state.get('student_id'):
    st.warning("⚠️ Please select a student from the home page first")
    st.stop()

student_id = st.session_state['student_id']
student = db_service.get_student(student_id)

if not student:
    st.error(f"Student {student_id} not found")
    st.stop()

# Get student data
grades_df = db_service.get_student_grades_df(student_id)
predictions_df = db_service.get_student_predictions_df(student_id)

if grades_df.empty:
    st.warning("⚠️ No grade records found. Please add grades first.")
    st.stop()

if predictions_df.empty:
    st.warning("⚠️ No predictions found. Please visit Dashboard to generate predictions.")
    st.stop()

# Get framework
framework_df = db_service.get_framework_df()

if framework_df.empty:
    st.error("⚠️ RIASEC framework not loaded. Please check database.")
    st.stop()

# Student header
st.subheader(f"Assessment for: {student.name}")

# API Key
api_key = st.text_input("OpenAI API Key", type="password", 
                       value=st.secrets.get("OPENAI_API_KEY", ""))

if not api_key:
    st.warning("⚠️ Please provide OpenAI API key")
    st.stop()

# RIASEC explanation
with st.expander("📖 About RIASEC (Holland Code)"):
    st.markdown("""
    The **Holland Code** (RIASEC) is a career interest assessment that categorizes people into six personality types:
    
    - **R - Realistic**: Practical, hands-on, technical work (Engineers, Mechanics, Builders)
    - **I - Investigative**: Analytical, scientific, research-oriented (Scientists, Analysts, Researchers)
    - **A - Artistic**: Creative, expressive, artistic work (Artists, Writers, Designers)
    - **S - Social**: Helping, teaching, service-oriented (Teachers, Counselors, Healthcare)
    - **E - Enterprising**: Leadership, persuasion, business (Managers, Entrepreneurs, Sales)
    - **C - Conventional**: Organized, detail-oriented, systematic (Accountants, Administrators, Analysts)
    
    Your results will show your top 3 codes, which together define your career personality profile.
    """)

st.divider()

# Run assessment button
if st.button("🚀 Start RIASEC Assessment", type="primary", use_container_width=True):
    
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
    st.subheader("Phase 1: Question Evaluation")
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_questions = len(framework_df)
    status_text.text(f"Evaluating {total_questions} questions...")
    
    with st.spinner("Evaluating questions in parallel..."):
        responses = career_service.evaluate_all_questions(
            student.name,
            student_profile,
            framework_df,
            max_workers=5
        )
    
    progress_bar.progress(100)
    status_text.text(f"✅ Completed {len(responses)} question evaluations")
    
    # Save responses to database
    db_service.save_assessment_responses(student_id, responses)
    
    # Calculate RIASEC scores
    riasec_scores = career_service.calculate_riasec_scores(responses, framework_df)
    
    # Phase 2: Generate final recommendation
    st.subheader("Phase 2: Final Career Recommendation")
    
    with st.spinner("Generating personalized career recommendations..."):
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
    
    st.success("✅ Assessment complete!")
    st.rerun()

# Display results if assessment is complete
if st.session_state.get('assessment_complete', False):
    
    st.divider()
    st.header("📊 Assessment Results")
    
    riasec_scores = st.session_state.get('riasec_scores', {})
    recommendation = st.session_state.get('recommendation', {})
    responses = st.session_state.get('assessment_responses', [])
    
    # RIASEC Profile Visualization
    st.subheader("Your RIASEC Profile")
    
    # Create radar chart
    categories = ['Realistic', 'Investigative', 'Artistic', 'Social', 'Enterprising', 'Conventional']
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
        title="RIASEC Personality Profile",
        height=500
    )
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Scores")
        sorted_scores = sorted(riasec_scores.items(), key=lambda x: x[1], reverse=True)
        for code, score in sorted_scores:
            name = {'R': 'Realistic', 'I': 'Investigative', 'A': 'Artistic',
                   'S': 'Social', 'E': 'Enterprising', 'C': 'Conventional'}[code]
            st.metric(f"{code} - {name}", f"{score:.1f}/100")
    
    # Career Recommendations
    st.divider()
    st.subheader("💼 Recommended Career Paths")
    
    riasec_profile = recommendation.get('riasec_profile', '')
    st.info(f"**Your Holland Code:** {riasec_profile}")
    
    recommended_paths = recommendation.get('recommended_paths', [])
    
    if recommended_paths:
        cols = st.columns(len(recommended_paths))
        for i, path in enumerate(recommended_paths):
            with cols[i]:
                st.success(f"**{i+1}. {path}**")
    
    # Confidence score
    confidence = recommendation.get('confidence_score', 0.0)
    st.progress(confidence)
    st.caption(f"Confidence: {confidence:.0%}")
    
    # Detailed summary
    st.divider()
    st.subheader("📝 Detailed Analysis")
    summary = recommendation.get('summary', '')
    st.markdown(summary)
    
    # Question breakdown
    st.divider()
    st.subheader("📋 Question-by-Question Breakdown")
    
    # Group responses by RIASEC code
    riasec_groups = {'R': [], 'I': [], 'A': [], 'S': [], 'E': [], 'C': []}
    
    for resp in responses:
        question_row = framework_df[framework_df['id'] == resp['question_id']]
        if not question_row.empty:
            code = question_row.iloc[0]['riasec_code']
            riasec_groups[code].append((question_row.iloc[0]['question'], resp))
    
    # Display by category
    riasec_names = {
        'R': 'Realistic (Practical/Technical)',
        'I': 'Investigative (Analytical/Scientific)',
        'A': 'Artistic (Creative/Expressive)',
        'S': 'Social (Helpful/Service)',
        'E': 'Enterprising (Leadership/Business)',
        'C': 'Conventional (Organized/Systematic)'
    }
    
    for code in ['R', 'I', 'A', 'S', 'E', 'C']:
        if riasec_groups[code]:
            with st.expander(f"{code} - {riasec_names[code]} ({len(riasec_groups[code])} questions)", expanded=False):
                for question_text, resp in riasec_groups[code]:
                    answer_color = {
                        'Yes': '🟢',
                        'Partial': '🟡',
                        'No': '🔴',
                        'Error': '⚠️'
                    }.get(resp['answer'], '⚪')
                    
                    st.markdown(f"**Q:** {question_text}")
                    st.markdown(f"**A:** {answer_color} {resp['answer']}")
                    st.markdown(f"*Reasoning:* {resp['reasoning']}")
                    st.divider()
    
    # Download options
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        # Download assessment results
        results_data = {
            'student_name': student.name,
            'student_id': student_id,
            'riasec_profile': riasec_profile,
            'recommended_paths': ', '.join(recommended_paths),
            'confidence': confidence,
            **{f'{code}_score': score for code, score in riasec_scores.items()}
        }
        results_df = pd.DataFrame([results_data])
        csv = results_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Assessment Summary",
            data=csv,
            file_name=f"riasec_assessment_{student_id}.csv",
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
                    'riasec_code': q['riasec_code'],
                    'category': q['career_category'],
                    'question': q['question'],
                    'answer': resp['answer'],
                    'reasoning': resp['reasoning']
                })
        
        responses_df = pd.DataFrame(responses_data)
        csv = responses_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Detailed Responses",
            data=csv,
            file_name=f"riasec_responses_{student_id}.csv",
            mime="text/csv"
        )

else:
    st.info("👆 Click the button above to start the assessment")

