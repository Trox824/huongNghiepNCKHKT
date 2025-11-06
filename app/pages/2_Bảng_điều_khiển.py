"""
Dashboard Page - Visualize grades and Grade 12 predictions
"""
import sys
import os
# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from app.config.database import get_db_connection
from app.services.database_service import DatabaseService
from app.services.prediction_service import PredictionService

st.set_page_config(page_title="BẢNG ĐIỀU KHIỂN HỌC TẬP", layout="wide")

# Add Font Awesome
st.markdown("""
<style>
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
    .icon { margin-right: 8px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1><i class="fas fa-chart-line icon"></i>BẢNG ĐIỀU KHIỂN THÀNH TÍCH HỌC TẬP</h1>', unsafe_allow_html=True)
st.markdown("TRỰC QUAN HÓA XU HƯỚNG ĐIỂM VÀ DỰ ĐOÁN THÀNH TÍCH LỚP 12")

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

# Get student grades
grades_df = db_service.get_student_grades_df(student_id)

if grades_df.empty:
    st.warning("KHÔNG TÌM THẤY BẢN GHI ĐIỂM. VUI LÒNG THÊM ĐIỂM Ở TRANG QUẢN LÝ HỌC SINH.")
    st.stop()

# Student header
st.subheader(f"HỌC SINH: {student.name}")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("TUỔI", student.age)
with col2:
    st.metric("TRƯỜNG", student.school)
with col3:
    st.metric("TỔNG SỐ ĐIỂM", len(grades_df))

st.divider()

# Predict Grade 12 scores
prediction_service = PredictionService()

with st.spinner("ĐANG DỰ ĐOÁN ĐIỂM LỚP 12..."):
    predictions = prediction_service.predict_grade_12(student_id, grades_df)

# Save predictions to database
if predictions:
    db_service.save_predictions(student_id, predictions)
    predictions_df = pd.DataFrame(predictions)
    
    # Store in session state for other pages
    st.session_state['predictions_df'] = predictions_df

# Get trend data for all subjects
trends = prediction_service.get_all_trends(grades_df)

# Subject selection
subjects = sorted(grades_df['subject'].unique())
selected_subject = st.selectbox("CHỌN MÔN HỌC ĐỂ XEM:", subjects)

# Get trend for selected subject
selected_trend = next((t for t in trends if t['subject'] == selected_subject), None)

if selected_trend:
    # Create visualization
    fig = go.Figure()
    
    # Historical grades (actual data points)
    fig.add_trace(go.Scatter(
        x=selected_trend['historical_grades'],
        y=selected_trend['historical_scores'],
        mode='markers',
        name='ĐIỂM THỰC TẾ',
        marker=dict(size=12, color='#1f77b4', symbol='circle'),
        hovertemplate='<b>LỚP %{x}</b><br>ĐIỂM: %{y:.2f}<extra></extra>'
    ))
    
    # Trend line (regression line)
    if selected_trend['trend_line_scores']:
        fig.add_trace(go.Scatter(
            x=selected_trend['trend_line_grades'][:11],  # Only up to Grade 11
            y=selected_trend['trend_line_scores'][:11],
            mode='lines',
            name='ĐƯỜNG XU HƯỚNG',
            line=dict(color='#1f77b4', width=2, dash='dash'),
            hovertemplate='<b>LỚP %{x}</b><br>XU HƯỚNG: %{y:.2f}<extra></extra>'
        ))
    
    # Predicted Grade 12
    if selected_trend['predicted_grade_12'] is not None:
        fig.add_trace(go.Scatter(
            x=[12],
            y=[selected_trend['predicted_grade_12']],
            mode='markers',
            name='DỰ ĐOÁN LỚP 12',
            marker=dict(size=16, color='#ff7f0e', symbol='star'),
            hovertemplate='<b>LỚP 12 (DỰ ĐOÁN)</b><br>ĐIỂM: %{y:.2f}<extra></extra>'
        ))
        
        # Extension line to prediction
        if selected_trend['trend_line_scores']:
            fig.add_trace(go.Scatter(
                x=[11, 12],
                y=[selected_trend['trend_line_scores'][10], selected_trend['predicted_grade_12']],
                mode='lines',
                name='MỞ RỘNG DỰ ĐOÁN',
                line=dict(color='#ff7f0e', width=2, dash='dot'),
                showlegend=False,
                hoverinfo='skip'
            ))
    
    # Update layout
    fig.update_layout(
        title=f"{selected_subject} - XU HƯỚNG THÀNH TÍCH & DỰ ĐOÁN LỚP 12",
        xaxis_title="LỚP",
        yaxis_title="ĐIỂM (0-10)",
        yaxis_range=[0, 10.5],
        xaxis=dict(
            tickmode='linear',
            tick0=1,
            dtick=1,
            range=[0.5, 12.5]
        ),
        hovermode='closest',
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Add reference lines
    fig.add_hline(y=8.0, line_dash="dot", line_color="green", opacity=0.5,
                  annotation_text="TỐT (8.0)", annotation_position="right")
    fig.add_hline(y=6.5, line_dash="dot", line_color="orange", opacity=0.5,
                  annotation_text="ĐẠT YÊU CẦU (6.5)", annotation_position="right")
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display metrics
    metrics = selected_trend.get('metrics', {})
    if metrics:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("ĐIỂM R²", f"{metrics.get('r2_score', 0):.3f}",
                     help="CHẤT LƯỢNG MÔ HÌNH (GẦN 1.0 LÀ TỐT HƠN)")
        with col2:
            st.metric("SAI SỐ TUYỆT ĐỐI TRUNG BÌNH", f"{metrics.get('mae', 0):.2f}",
                     help="SAI SỐ DỰ ĐOÁN TRUNG BÌNH")
        with col3:
            st.metric("SỐ ĐIỂM DỮ LIỆU", metrics.get('data_points', 0))

st.divider()

# Summary Section
st.subheader("TÓM TẮT THÀNH TÍCH TỔNG QUÁT")

# Create summary table
summary_data = []
for trend in trends:
    pred_score = trend.get('predicted_grade_12')
    if pred_score:
        historical_avg = sum(trend['historical_scores']) / len(trend['historical_scores'])
        change = pred_score - historical_avg
        summary_data.append({
            'MÔN HỌC': trend['subject'],
            'TRUNG BÌNH HIỆN TẠI (L1-11)': f"{historical_avg:.2f}",
            'DỰ ĐOÁN L12': f"{pred_score:.2f}",
            'THAY ĐỔI': f"{change:+.2f}",
            'TRẠNG THÁI': 'TĂNG' if change > 0 else 'GIẢM' if change < 0 else 'ỔN ĐỊNH'
        })

if summary_data:
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, use_container_width=True, hide_index=True)
    
    # Overall statistics
    st.divider()
    st.subheader("📈 THỐNG KÊ")
    
    col1, col2, col3, col4 = st.columns(4)
    
    predictions_df = pd.DataFrame(predictions)
    avg_predicted = predictions_df['predicted_score'].mean()
    avg_current = grades_df['score'].mean()
    
    with col1:
        st.metric("TRUNG BÌNH HIỆN TẠI", f"{avg_current:.2f}")
    with col2:
        st.metric("TRUNG BÌNH DỰ ĐOÁN L12", f"{avg_predicted:.2f}")
    with col3:
        overall_change = avg_predicted - avg_current
        st.metric("XU HƯỚNG TỔNG QUÁT", f"{overall_change:+.2f}",
                 delta=f"{overall_change:+.2f}")
    with col4:
        strong_subjects = len([p for p in predictions if p['predicted_score'] >= 8.0])
        st.metric("MÔN HỌC TỐT (≥8.0)", strong_subjects)
    
    # Strengths analysis
    analysis = prediction_service.analyze_student_strengths(predictions)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.success("**ĐIỂM MẠNH:**")
        if analysis['strong_subjects']:
            for subj in analysis['strong_subjects']:
                st.markdown(f"- {subj}")
        else:
            st.markdown("*TIẾP TỤC XÂY DỰNG ĐIỂM MẠNH*")
    
    with col2:
        st.info("**CẦN CẢI THIỆN:**")
        if analysis['improvement_areas']:
            for subj in analysis['improvement_areas']:
                st.markdown(f"📝 {subj}")
        else:
            st.markdown("*TẤT CẢ MÔN HỌC ĐANG THỂ HIỆN TỐT*")

# Download predictions
st.divider()
if predictions:
    predictions_df = pd.DataFrame(predictions)
    csv = predictions_df.to_csv(index=False)
    st.download_button(
        label="TẢI XUỐNG DỰ ĐOÁN DƯỚI DẠNG CSV",
        data=csv,
        file_name=f"du_doan_{student.name}_{student_id}.csv",
        mime="text/csv"
    )

