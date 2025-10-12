# Implementation Plan: Converting EU AI Act Tool to Student Career Guidance System

## Overview

This document outlines how to transform the current **EU AI Act Assessment Tool** into the **Student Performance Prediction and Career Guidance System** as described in the PRD.

---

## Current State vs. Target State

### Current System (EU AI Act Tool)

- Analyzes mobile apps from Google Play Store
- Uses web scraping (Selenium + google-play-scraper)
- Analyzes user reviews with NLP
- Classifies apps by EU AI Act risk categories
- Uses RAG (FAISS vector database) for evidence retrieval

### Target System (Student Career Guidance)

- Analyzes student academic performance (Grades 1-11)
- Uses CSV imports for student data
- Predicts Grade 12 scores with Linear Regression
- Evaluates students against career framework questions
- **No RAG** - simple question-by-question evaluation

---

## Reusable Components

These components from the current system can be adapted:

### ✅ Keep and Modify

1. **Services Architecture** (`app/services/`)

   - `analysis.py` → Keep LLM integration logic, remove RAG
   - `cache.py` → Keep caching system
   - `logger.py` → Keep logging utilities
   - **Remove:** `playstore.py`, `selenium_scraper.py`

2. **UI Framework** (`app/ui/`)

   - Keep Streamlit multi-page structure
   - Modify for student data instead of app data
   - Reuse status display patterns

3. **Data Models** (`app/models/`)

   - Replace `AppDetails` with `StudentProfile`
   - Replace `Review` with `Grade`
   - Keep structured data patterns

4. **Configuration** (`app/config/`)

   - Keep settings structure
   - Update constants for student system

5. **CSV Assessment Pattern**
   - Keep the CSV-based question framework pattern
   - Replace EU AI Act questions with career guidance questions

---

## Implementation Steps

### Phase 1: Data Models (Week 1)

#### 1.1 Create New Data Models

**File: `app/models/student_data.py`** (replaces `app_data.py`)

```python
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import pandas as pd
from datetime import datetime

@dataclass
class StudentProfile:
    """Student basic information"""
    id: str
    name: str
    age: int
    school: str
    notes: str = ""  # Extracurricular activities, interests
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class Grade:
    """Individual grade record"""
    student_id: str
    subject: str
    grade_level: int  # 1-11
    score: float  # 0-10 scale
    semester: Optional[int] = None

@dataclass
class Prediction:
    """Grade 12 prediction for a subject"""
    student_id: str
    subject: str
    predicted_score: float
    confidence_interval: Optional[tuple] = None
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class AssessmentResponse:
    """Response to a single career framework question"""
    student_id: str
    question_id: int
    question_text: str
    answer: str  # "Yes", "No", "Partial"
    reasoning: str
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class CareerRecommendation:
    """Final career recommendation"""
    student_id: str
    recommended_paths: List[str]  # e.g., ["Engineering", "Computer Science"]
    summary: str  # Detailed explanation
    confidence_score: float
    timestamp: datetime = field(default_factory=datetime.now)
```

#### 1.2 Create Database Schema

**File: `app/database/schema.py`** (new file)

```python
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime

Base = declarative_base()

class Student(Base):
    __tablename__ = 'students'

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    age = Column(Integer)
    school = Column(String)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    grades = relationship("Grade", back_populates="student")
    predictions = relationship("Prediction", back_populates="student")
    assessments = relationship("AssessmentResponse", back_populates="student")
    recommendations = relationship("CareerRecommendation", back_populates="student")

class Grade(Base):
    __tablename__ = 'grades'

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String, ForeignKey('students.id'))
    subject = Column(String, nullable=False)
    grade_level = Column(Integer, nullable=False)  # 1-11
    score = Column(Float, nullable=False)
    semester = Column(Integer)

    student = relationship("Student", back_populates="grades")

class Prediction(Base):
    __tablename__ = 'predictions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String, ForeignKey('students.id'))
    subject = Column(String, nullable=False)
    predicted_score = Column(Float, nullable=False)
    confidence_interval = Column(String)  # JSON string
    model_version = Column(String)
    timestamp = Column(DateTime, default=datetime.now)

    student = relationship("Student", back_populates="predictions")

class Framework(Base):
    __tablename__ = 'framework'

    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String, nullable=False)
    question = Column(Text, nullable=False)
    key_subjects = Column(String)  # Comma-separated
    required_grades = Column(String)
    weight = Column(Float, default=1.0)

class AssessmentResponse(Base):
    __tablename__ = 'assessment_responses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String, ForeignKey('students.id'))
    question_id = Column(Integer, ForeignKey('framework.id'))
    answer = Column(String, nullable=False)
    reasoning = Column(Text)
    timestamp = Column(DateTime, default=datetime.now)

    student = relationship("Student", back_populates="assessments")
    question = relationship("Framework")

class CareerRecommendation(Base):
    __tablename__ = 'career_recommendations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String, ForeignKey('students.id'))
    recommended_paths = Column(Text)  # JSON array
    summary = Column(Text)
    confidence_score = Column(Float)
    timestamp = Column(DateTime, default=datetime.now)

    student = relationship("Student", back_populates="recommendations")

# Database initialization
def init_db(db_path='student_career.db'):
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return engine, Session()
```

---

### Phase 2: ML Prediction Service (Week 2)

#### 2.1 Create Prediction Service

**File: `app/services/prediction.py`** (new file)

```python
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from typing import Dict, List, Tuple
from models.student_data import Prediction
from services.logger import logger

class GradePredictionService:
    """Service for predicting Grade 12 scores using Linear Regression"""

    def __init__(self):
        self.models: Dict[str, LinearRegression] = {}

    def train_model_for_subject(self, grades_df: pd.DataFrame, subject: str) -> LinearRegression:
        """
        Train a Linear Regression model for a specific subject

        Args:
            grades_df: DataFrame with columns [grade_level, score]
            subject: Subject name

        Returns:
            Trained LinearRegression model
        """
        # Filter for this subject
        subject_df = grades_df[grades_df['subject'] == subject].copy()

        if len(subject_df) < 2:
            logger.warning(f"Insufficient data for {subject}: only {len(subject_df)} grades")
            return None

        # Prepare X (grade levels) and y (scores)
        X = subject_df['grade_level'].values.reshape(-1, 1)
        y = subject_df['score'].values

        # Train model
        model = LinearRegression()
        model.fit(X, y)

        # Store model
        self.models[subject] = model

        logger.info(f"Trained model for {subject}: R² = {model.score(X, y):.3f}")
        return model

    def predict_grade_12(self, student_id: str, grades_df: pd.DataFrame) -> List[Prediction]:
        """
        Predict Grade 12 scores for all subjects

        Args:
            student_id: Student ID
            grades_df: DataFrame with student's grades

        Returns:
            List of Prediction objects
        """
        predictions = []

        # Get unique subjects for this student
        subjects = grades_df['subject'].unique()

        for subject in subjects:
            # Train model for this subject
            model = self.train_model_for_subject(grades_df, subject)

            if model is None:
                continue

            # Predict Grade 12 (grade_level = 12)
            predicted_score = model.predict([[12]])[0]

            # Clip to valid range [0, 10]
            predicted_score = np.clip(predicted_score, 0, 10)

            # Create prediction object
            prediction = Prediction(
                student_id=student_id,
                subject=subject,
                predicted_score=float(predicted_score)
            )
            predictions.append(prediction)

        return predictions

    def get_trend_data(self, grades_df: pd.DataFrame, subject: str) -> Dict:
        """
        Get historical trend + prediction for visualization

        Returns:
            Dict with historical grades and predicted Grade 12
        """
        subject_df = grades_df[grades_df['subject'] == subject].sort_values('grade_level')

        historical_grades = subject_df['grade_level'].tolist()
        historical_scores = subject_df['score'].tolist()

        # Get prediction
        model = self.models.get(subject)
        if model:
            predicted_score = float(np.clip(model.predict([[12]])[0], 0, 10))
        else:
            predicted_score = None

        return {
            'subject': subject,
            'historical_grades': historical_grades,
            'historical_scores': historical_scores,
            'predicted_grade_12': predicted_score
        }
```

---

### Phase 3: Career Assessment Service (Week 3-4)

#### 3.1 Modify Analysis Service

**File: `app/services/career_assessment.py`** (replaces parts of `analysis.py`)

```python
import openai
from pydantic import BaseModel
from typing import List, Literal, Optional
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from models.student_data import StudentProfile, AssessmentResponse, CareerRecommendation
from services.logger import logger
from services.cache import CacheService

class QuestionResponse(BaseModel):
    """Structured response for a single question"""
    answer: Literal["Yes", "No", "Partial"]
    reasoning: str

class FinalRecommendation(BaseModel):
    """Structured final career recommendation"""
    recommended_paths: List[str]  # 1-3 career paths
    summary: str  # Detailed explanation
    confidence_score: float  # 0-1

class CareerAssessmentService:
    """Service for evaluating students against career framework"""

    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
        self.cache_service = CacheService()

    def evaluate_single_question(
        self,
        student: StudentProfile,
        grades_df: pd.DataFrame,
        predictions_df: pd.DataFrame,
        question: str,
        category: str
    ) -> AssessmentResponse:
        """
        Evaluate a single question independently

        IMPORTANT: No context from other questions
        """
        # Prepare student context
        context = self._prepare_student_context(student, grades_df, predictions_df)

        # Create prompt
        prompt = f"""You are evaluating a student for career guidance.

Question: {question}
Category: {category}

Student Profile:
{context}

Evaluate this question independently (do not consider other questions).
Provide:
1. Answer: Yes, No, or Partial
2. Reasoning: Explain your answer based on the student's grades and profile

Be specific and reference actual grades/subjects in your reasoning.
"""

        try:
            # Call OpenAI API with structured output
            response = self.client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format=QuestionResponse,
                temperature=0.3
            )

            parsed = response.choices[0].message.parsed

            logger.info(f"Evaluated: '{question[:50]}...' → {parsed.answer}")

            return AssessmentResponse(
                student_id=student.id,
                question_id=0,  # Will be set by caller
                question_text=question,
                answer=parsed.answer,
                reasoning=parsed.reasoning
            )

        except Exception as e:
            logger.error(f"Error evaluating question: {e}")
            return AssessmentResponse(
                student_id=student.id,
                question_id=0,
                question_text=question,
                answer="Error",
                reasoning=f"Evaluation failed: {str(e)}"
            )

    def evaluate_all_questions(
        self,
        student: StudentProfile,
        grades_df: pd.DataFrame,
        predictions_df: pd.DataFrame,
        framework_df: pd.DataFrame,
        max_workers: int = 5
    ) -> List[AssessmentResponse]:
        """
        Evaluate all questions in parallel

        Each question is evaluated independently
        """
        responses = []

        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}

            for idx, row in framework_df.iterrows():
                future = executor.submit(
                    self.evaluate_single_question,
                    student,
                    grades_df,
                    predictions_df,
                    row['question'],
                    row['category']
                )
                futures[future] = idx

            # Collect results as they complete
            for future in as_completed(futures):
                idx = futures[future]
                response = future.result()
                response.question_id = int(idx)
                responses.append(response)

        logger.info(f"Completed evaluation of {len(responses)} questions")
        return responses

    def generate_final_recommendation(
        self,
        student: StudentProfile,
        grades_df: pd.DataFrame,
        predictions_df: pd.DataFrame,
        assessment_responses: List[AssessmentResponse]
    ) -> CareerRecommendation:
        """
        Generate final career recommendation based on all answers

        This is Phase 2: Analyzing all answers together
        """
        # Prepare summary of all Q&A
        qa_summary = self._format_qa_summary(assessment_responses)

        # Prepare student context
        context = self._prepare_student_context(student, grades_df, predictions_df)

        # Create final recommendation prompt
        prompt = f"""You are a career counselor analyzing a student's complete assessment.

Student Profile:
{context}

Assessment Results:
{qa_summary}

Based on ALL the answers above, provide:
1. 1-3 recommended career paths (ranked by suitability)
2. Detailed summary explaining why these paths fit the student
3. Confidence score (0-1) for your recommendations

Consider:
- Patterns in the answers
- Student's grade performance and predictions
- Strengths and weaknesses across subjects
- Overall profile alignment with career categories
"""

        try:
            response = self.client.beta.chat.completions.parse(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format=FinalRecommendation,
                temperature=0.5
            )

            parsed = response.choices[0].message.parsed

            return CareerRecommendation(
                student_id=student.id,
                recommended_paths=parsed.recommended_paths,
                summary=parsed.summary,
                confidence_score=parsed.confidence_score
            )

        except Exception as e:
            logger.error(f"Error generating final recommendation: {e}")
            return CareerRecommendation(
                student_id=student.id,
                recommended_paths=["Error"],
                summary=f"Failed to generate recommendation: {str(e)}",
                confidence_score=0.0
            )

    def _prepare_student_context(
        self,
        student: StudentProfile,
        grades_df: pd.DataFrame,
        predictions_df: pd.DataFrame
    ) -> str:
        """Format student data for LLM context"""

        # Student info
        context = f"""
Name: {student.name}
Age: {student.age}
School: {student.school}
Notes: {student.notes}

Grade History (Grades 1-11):
"""

        # Group grades by subject
        for subject in grades_df['subject'].unique():
            subject_grades = grades_df[grades_df['subject'] == subject].sort_values('grade_level')
            grades_str = ", ".join([
                f"Grade {row['grade_level']}: {row['score']:.1f}"
                for _, row in subject_grades.iterrows()
            ])
            context += f"\n  {subject}: {grades_str}"

        # Predicted Grade 12
        context += "\n\nPredicted Grade 12 Scores:\n"
        for _, pred in predictions_df.iterrows():
            context += f"  {pred['subject']}: {pred['predicted_score']:.1f}\n"

        return context

    def _format_qa_summary(self, responses: List[AssessmentResponse]) -> str:
        """Format all Q&A for final recommendation"""
        summary = ""
        for i, resp in enumerate(responses, 1):
            summary += f"\nQ{i}: {resp.question_text}\n"
            summary += f"A: {resp.answer} - {resp.reasoning}\n"
        return summary
```

---

### Phase 4: Frontend Modifications (Week 5-6)

#### 4.1 Create Main Page

**File: `app/pages/1_📊_Student_Dashboard.py`** (new)

```python
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from services.prediction import GradePredictionService

st.set_page_config(page_title="Student Dashboard", page_icon="📊", layout="wide")

st.title("📊 Student Performance Dashboard")

# Load student data
# TODO: Add database integration
if 'student_data' not in st.session_state:
    st.warning("Please upload student data first")
    st.stop()

student = st.session_state['student_data']
grades_df = st.session_state['grades_df']

# Display student info
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Student", student.name)
with col2:
    st.metric("Age", student.age)
with col3:
    st.metric("School", student.school)

# Predict grades
prediction_service = GradePredictionService()
predictions = prediction_service.predict_grade_12(student.id, grades_df)

# Visualize each subject
subjects = grades_df['subject'].unique()

for subject in subjects:
    trend_data = prediction_service.get_trend_data(grades_df, subject)

    # Create plot
    fig = go.Figure()

    # Historical grades
    fig.add_trace(go.Scatter(
        x=trend_data['historical_grades'],
        y=trend_data['historical_scores'],
        mode='lines+markers',
        name='Historical Grades',
        line=dict(color='blue', width=2),
        marker=dict(size=8)
    ))

    # Predicted Grade 12
    if trend_data['predicted_grade_12']:
        fig.add_trace(go.Scatter(
            x=[12],
            y=[trend_data['predicted_grade_12']],
            mode='markers',
            name='Predicted Grade 12',
            marker=dict(size=12, color='red', symbol='star')
        ))

    fig.update_layout(
        title=f"{subject} - Performance Trend",
        xaxis_title="Grade Level",
        yaxis_title="Score (0-10)",
        yaxis_range=[0, 10],
        hovermode='x unified'
    )

    st.plotly_chart(fig, use_container_width=True)

# Display predictions table
predictions_df = pd.DataFrame([
    {'Subject': p.subject, 'Predicted Grade 12': f"{p.predicted_score:.2f}"}
    for p in predictions
])

st.subheader("Grade 12 Predictions Summary")
st.dataframe(predictions_df, use_container_width=True)
```

#### 4.2 Create Career Assessment Page

**File: `app/pages/2_🎯_Career_Assessment.py`** (new)

```python
import streamlit as st
from services.career_assessment import CareerAssessmentService

st.set_page_config(page_title="Career Assessment", page_icon="🎯", layout="wide")

st.title("🎯 Career Path Assessment")

# Check prerequisites
if 'student_data' not in st.session_state:
    st.warning("Please go to Dashboard first")
    st.stop()

student = st.session_state['student_data']
grades_df = st.session_state['grades_df']
predictions_df = st.session_state['predictions_df']
framework_df = st.session_state['framework_df']

st.write(f"Assessing career paths for **{student.name}**")

# Get API key
api_key = st.secrets.get("OPENAI_API_KEY") or st.text_input("OpenAI API Key", type="password")

if not api_key:
    st.warning("Please provide OpenAI API key")
    st.stop()

# Run assessment
if st.button("Start Assessment", type="primary"):
    service = CareerAssessmentService(api_key)

    with st.spinner("Evaluating questions..."):
        # Phase 1: Individual questions
        responses = service.evaluate_all_questions(
            student, grades_df, predictions_df, framework_df
        )

        # Store responses
        st.session_state['assessment_responses'] = responses

        st.success(f"Completed {len(responses)} question evaluations!")

    with st.spinner("Generating final recommendation..."):
        # Phase 2: Final recommendation
        recommendation = service.generate_final_recommendation(
            student, grades_df, predictions_df, responses
        )

        st.session_state['career_recommendation'] = recommendation

        st.success("Career recommendation generated!")

    st.rerun()

# Display results if available
if 'assessment_responses' in st.session_state:
    st.subheader("Assessment Results")

    responses = st.session_state['assessment_responses']

    # Group by category
    categories = {}
    for resp in responses:
        # Get category from framework
        category = "General"  # TODO: map from framework
        if category not in categories:
            categories[category] = []
        categories[category].append(resp)

    # Display by category
    for category, cat_responses in categories.items():
        with st.expander(f"📁 {category} ({len(cat_responses)} questions)", expanded=False):
            for resp in cat_responses:
                st.markdown(f"**Q:** {resp.question_text}")
                st.markdown(f"**A:** {resp.answer}")
                st.markdown(f"*Reasoning:* {resp.reasoning}")
                st.divider()

# Display final recommendation
if 'career_recommendation' in st.session_state:
    st.divider()
    st.subheader("🎓 Recommended Career Paths")

    rec = st.session_state['career_recommendation']

    # Display recommended paths
    cols = st.columns(len(rec.recommended_paths))
    for i, path in enumerate(rec.recommended_paths):
        with cols[i]:
            st.success(f"**{i+1}. {path}**")

    # Confidence score
    st.progress(rec.confidence_score)
    st.caption(f"Confidence: {rec.confidence_score:.0%}")

    # Detailed summary
    st.markdown("### Detailed Analysis")
    st.markdown(rec.summary)
```

---

### Phase 5: Data Upload & Management (Week 7)

#### 5.1 Create Upload Page

**File: `app/pages/0_📤_Upload_Data.py`** (new)

```python
import streamlit as st
import pandas as pd
from models.student_data import StudentProfile, Grade
from database.schema import init_db

st.set_page_config(page_title="Upload Data", page_icon="📤", layout="wide")

st.title("📤 Upload Student Data")

# Initialize database
engine, session = init_db()

# Upload student grades CSV
st.subheader("1. Upload Student Grades")

st.markdown("""
Expected CSV format:
- Columns: `student_id`, `student_name`, `age`, `school`, `notes`, `subject`, `grade_level`, `score`
- Example:
```

student_id,student_name,age,school,notes,subject,grade_level,score
ST001,John Doe,17,ABC High School,Interested in robotics,Math,9,8.5
ST001,John Doe,17,ABC High School,Interested in robotics,Math,10,8.7
...

```
""")

uploaded_file = st.file_uploader("Choose CSV file", type=['csv'])

if uploaded_file:
  try:
      # Read CSV
      df = pd.read_csv(uploaded_file)

      st.success(f"Loaded {len(df)} records")
      st.dataframe(df.head())

      # Validate columns
      required_cols = ['student_id', 'student_name', 'subject', 'grade_level', 'score']
      missing_cols = [col for col in required_cols if col not in df.columns]

      if missing_cols:
          st.error(f"Missing required columns: {missing_cols}")
      else:
          if st.button("Process and Store", type="primary"):
              # Process data
              # Group by student
              students = {}
              for _, row in df.iterrows():
                  student_id = row['student_id']

                  if student_id not in students:
                      students[student_id] = {
                          'profile': StudentProfile(
                              id=student_id,
                              name=row['student_name'],
                              age=row.get('age', 17),
                              school=row.get('school', 'Unknown'),
                              notes=row.get('notes', '')
                          ),
                          'grades': []
                      }

                  students[student_id]['grades'].append(Grade(
                      student_id=student_id,
                      subject=row['subject'],
                      grade_level=int(row['grade_level']),
                      score=float(row['score'])
                  ))

              st.success(f"Processed {len(students)} students")

              # Store in session state for demo
              st.session_state['students'] = students

              # For demo, use first student
              first_student_id = list(students.keys())[0]
              st.session_state['student_data'] = students[first_student_id]['profile']

              grades_list = students[first_student_id]['grades']
              st.session_state['grades_df'] = pd.DataFrame([
                  {
                      'student_id': g.student_id,
                      'subject': g.subject,
                      'grade_level': g.grade_level,
                      'score': g.score
                  }
                  for g in grades_list
              ])

              st.rerun()

  except Exception as e:
      st.error(f"Error processing file: {e}")

# Upload career framework CSV
st.divider()
st.subheader("2. Upload Career Framework")

st.markdown("""
Expected CSV format:
- Columns: `category`, `question`, `key_subjects`, `required_grades`, `weight`
- Example: See PRD Section 4.3
""")

framework_file = st.file_uploader("Choose framework CSV", type=['csv'], key='framework')

if framework_file:
  try:
      framework_df = pd.read_csv(framework_file)
      st.success(f"Loaded {len(framework_df)} questions")
      st.dataframe(framework_df)

      if st.button("Load Framework", type="primary"):
          st.session_state['framework_df'] = framework_df
          st.success("Framework loaded!")

  except Exception as e:
      st.error(f"Error loading framework: {e}")
```

---

## Summary of Changes

### Files to Remove

- `app/services/playstore.py`
- `app/services/selenium_scraper.py`
- `app/utils/review_filter.py`
- `app/models/ar_miner_model.pkl`
- `asset/EU_AI_Act_Assessment_Questions.csv` (replace with career framework)

### Files to Create

- `app/models/student_data.py`
- `app/database/schema.py`
- `app/services/prediction.py`
- `app/services/career_assessment.py`
- `app/pages/0_📤_Upload_Data.py`
- `app/pages/1_📊_Student_Dashboard.py`
- `app/pages/2_🎯_Career_Assessment.py`
- `asset/Career_Framework_Questions.csv`

### Files to Modify

- `app/main.py` - Update for student system entry point
- `app/services/analysis.py` - Remove RAG, simplify for question evaluation
- `app/services/cache.py` - Adapt for student data caching
- `app/config/settings.py` - Update constants
- `requirements.txt` - Remove unnecessary dependencies, add SQLAlchemy

### Updated requirements.txt

```txt
streamlit>=1.28.0
pandas>=2.0.0
openai>=1.0.0
pydantic>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
plotly>=5.18.0
sqlalchemy>=2.0.0
python-dotenv>=1.0.0
```

---

## Testing Strategy

1. **Unit Tests**

   - Test Linear Regression predictions with sample data
   - Test question evaluation with mock OpenAI responses
   - Test data validation and CSV parsing

2. **Integration Tests**

   - Full pipeline: CSV upload → Prediction → Assessment → Recommendation
   - Database operations
   - Caching functionality

3. **User Acceptance Testing**
   - Upload real student data
   - Verify grade predictions are reasonable
   - Verify career recommendations make sense

---

## Next Steps

1. Review this implementation plan
2. Create sample CSV files for testing
3. Start with Phase 1 (Data Models)
4. Test each phase before moving to the next
5. Deploy to Streamlit Cloud when complete

---

_End of Implementation Plan_
