# Product Requirements Document (PRD)

## 1. Product Overview

**Product Name:** AI-Powered Student Performance Prediction and Career Guidance System

**Prepared By:** Tuan (Henry) Hung Nguyen – COS40005 Computing Technology Project A

**Last Updated:** October 11th, 2025

---

## 2. Product Summary

This system is an AI-based platform designed to analyze student performance data from Grades 1–11, predict Grade 12 results, and recommend suitable career paths.

The platform combines:

- **A Linear Regression model** for academic prediction
- **A Large Language Model (LLM)** that reasons using a predefined career framework (CSV-driven) to provide personalized career advice

The solution aims to assist students, teachers, and parents in understanding academic progress, future performance trends, and career orientation based on academic results and qualitative information.

---

## 3. Goals & Objectives

| Goal                            | Description                                                                                 |
| ------------------------------- | ------------------------------------------------------------------------------------------- |
| 🎯 **Performance Prediction**   | Predict Grade 12 performance per subject using data from Grades 1–11                        |
| 🧠 **Career Recommendation**    | Use a rule-based framework with LLM reasoning to suggest suitable career paths              |
| 💬 **Interactive AI Assistant** | Provide a conversational AI for explaining predictions and career matches                   |
| 📊 **Visualization & Reports**  | Offer clear dashboards and charts for student performance trends                            |
| 🧩 **Dynamic Data Management**  | Support dynamic subjects — handle cases where subjects appear/disappear across grade levels |

---

## 4. Key Features

### 4.1. Student Data Management

**Description:**

- Import student data from CSV or form input
- Store academic records dynamically for Grades 1–11
- Handle subject variability (some subjects only appear in later grades)
- Allow teacher/admin CRUD operations

**Functional Requirements:**

- **FR1:** Data model supports dynamic subject list per student
- **FR2:** Upload and parse student CSV files
- **FR3:** Store student metadata (name, class, year, notes, etc.)

---

### 4.2. Academic Prediction Module

**Description:**

- Predict Grade 12 subject results using Linear Regression based on all historical grades (Grades 1–11)
- Handle missing subject data dynamically
- Generate performance trend visualizations

**Functional Requirements:**

- **FR4:** Train and serve a Linear Regression model using Scikit-learn
- **FR5:** Predict grade per subject with fallback interpolation for missing years
- **FR6:** Display interactive graphs (performance over time)

**Rationale:**

Linear Regression is chosen because:

- The task is continuous prediction, not classification
- The dataset is small and structured
- It supports explainable coefficient-based insights

---

### 4.3. Career Guidance Framework

**Description:**

- Based on a predefined career framework (e.g., RIASEC categories or custom CSV)
- Each category includes requirements, key subjects, weightings, and evaluation questions
- The LLM evaluates whether a student meets the conditions for each career group

**Functional Requirements:**

- **FR7:** Load CSV framework dynamically on system startup
- **FR8:** Generate question sets from the framework for each category
- **FR9:** Evaluate student data (grades, notes) through LLM reasoning
- **FR10:** Classify the student into 1–3 suitable career categories

**CSV Framework Example:**

| Category    | Key_Subjects     | Required_Grades | Questions                                               | Notes                                    |
| ----------- | ---------------- | --------------- | ------------------------------------------------------- | ---------------------------------------- |
| Engineering | Math, Physics    | ≥ 7.5           | "Does the student show strong problem-solving in STEM?" | Based on performance in technical tasks  |
| Arts        | Literature, Art  | ≥ 7.0           | "Does the student demonstrate creativity?"              | Include writing/project-based evaluation |
| Social      | English, History | ≥ 6.5           | "Is the student collaborative or communicative?"        | Use extracurricular notes                |

---

### 4.4. AI Reasoning Engine (Question-Based Evaluation)

**Description:**

The system evaluates students through a two-phase process:

**Phase 1: Individual Question Evaluation**

- Load questions from career framework CSV
- For each question, evaluate the student independently using:
  - Student's grade history (Grades 1-11)
  - Predicted Grade 12 scores
  - Student metadata (notes, extracurricular activities)
  - Subject-specific performance patterns
- Each question is answered in isolation (no context from other questions)
- Store all individual answers with reasoning

**Phase 2: Final Career Recommendation**

- Aggregate all question answers
- LLM analyzes the complete set of answers
- Generate comprehensive career path recommendation
- Provide reasoning based on answer patterns and grade performance

**Functional Requirements:**

- **FR11:** Load career framework questions from CSV on startup
- **FR12:** Evaluate each question independently using OpenAI API
- **FR13:** Store individual question responses (answer + reasoning)
- **FR14:** Generate final summary analyzing all answers together
- **FR15:** Return 1-3 recommended career paths with detailed explanations
- **FR16:** Cache individual question responses and final recommendations

---

### 4.5. Frontend Interface (Streamlit)

**Description:**

- Dashboard for visualizing grades and predictions
- Career assessment page showing question-by-question evaluation
- Results page with final career recommendations
- Admin panel for uploading framework CSV and student data

**Functional Requirements:**

- **FR17:** Multi-page Streamlit app (Dashboard / Assessment / Career Results / Data Upload)
- **FR18:** Plot grade trends by subject and predicted scores using Plotly
- **FR19:** Display individual question answers with reasoning
- **FR20:** Show final career recommendation summary with supporting evidence
- **FR21:** Upload interface for student CSV and career framework CSV
- **FR22:** Student selection dropdown for multi-student analysis

---

### 4.6. Backend (Python Services)

**Description:**

Service layer for:

- Student data management (CRUD operations)
- Model training and prediction (Linear Regression)
- Career question evaluation (LLM-based)
- Final recommendation generation
- Dynamic subject handling

**Functional Requirements:**

- **FR23:** Service classes with consistent interfaces
- **FR24:** Async/parallel processing for multiple question evaluations
- **FR25:** Caching layer for predictions and LLM responses
- **FR26:** CSV parsing utilities for student and framework data
- **FR27:** Database abstraction for SQLite/PostgreSQL

---

## 5. System Architecture

```
┌─────────────────────────────────────────┐
│  Student Data Input                     │
│  - CSV Upload (Grades 1-11)             │
│  - Student Metadata & Notes             │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  Database Layer                         │
│  - Students Table                       │
│  - Grades Table (Dynamic Subjects)      │
│  - Framework Table                      │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  ML Prediction Service                  │
│  - Linear Regression Model              │
│  - Train on Grades 1-11                 │
│  - Predict Grade 12 per Subject         │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  Career Framework CSV                   │
│  - Category                             │
│  - Questions                            │
│  - Key Subjects                         │
│  - Required Grades                      │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  Question Evaluation Loop               │
│  For each question:                     │
│    - Load student data + predictions    │
│    - Send to LLM (isolated context)     │
│    - Get answer + reasoning             │
│    - Store result                       │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  Final Career Recommendation            │
│  - Aggregate all answers                │
│  - LLM analyzes patterns                │
│  - Generate 1-3 career paths            │
│  - Provide detailed reasoning           │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  Streamlit Frontend                     │
│  - Dashboard (Grades & Predictions)     │
│  - Assessment Results (Q&A)             │
│  - Career Recommendations               │
└─────────────────────────────────────────┘
```

---

## 6. Data Flow

### 6.1. Data Import & Preparation

1. **Upload student CSV** containing grades for Grades 1-11, student metadata, notes
2. **Parse and validate** data structure, identify available subjects per student
3. **Store in database** with dynamic subject handling
4. **Upload career framework CSV** with questions, categories, requirements

### 6.2. Grade Prediction

1. **Extract grade history** for each student and subject
2. **Train Linear Regression model** per subject (using grade level as X, score as Y)
3. **Predict Grade 12 score** for each subject
4. **Store predictions** in predictions table with timestamp
5. **Visualize trends** showing historical grades + predicted Grade 12

### 6.3. Career Assessment (Phase 1: Individual Questions)

1. **Load career framework questions** from CSV
2. **For each question independently:**
   - Create evaluation context with:
     - Student profile (name, age, school, notes)
     - Grade history (Grades 1-11 with scores per subject)
     - Predicted Grade 12 scores
     - No context from other questions
   - **Send to OpenAI API** with specific question
   - **Parse response:** Answer (Yes/No/Partial) + Reasoning
   - **Store result** in assessment_responses table
3. **Cache results** to avoid re-evaluation

### 6.4. Career Recommendation (Phase 2: Final Summary)

1. **Collect all question-answer pairs** for the student
2. **Aggregate results** by career category
3. **Send complete assessment to LLM:**
   - All questions with their answers and reasoning
   - Student's grade patterns and strengths
   - Predicted Grade 12 performance
4. **LLM generates final recommendation:**
   - 1-3 suitable career paths ranked by fit
   - Detailed reasoning referencing specific answers
   - Strengths and areas for development
   - Actionable advice
5. **Display results** in frontend with:
   - Grade visualizations
   - Question-by-question breakdown
   - Final career recommendations
   - Supporting evidence from answers

---

## 7. Data Model

### Database Tables

#### `students`

- `id` (Primary Key)
- `name`
- `age`
- `school`
- `notes` (extracurricular activities, interests, etc.)
- `created_at`
- `updated_at`

#### `grades`

- `id` (Primary Key)
- `student_id` (Foreign Key → students)
- `subject` (string, dynamic)
- `grade_level` (1-11)
- `score` (float, 0-10 scale)
- `semester` (optional)

#### `predictions`

- `id` (Primary Key)
- `student_id` (Foreign Key → students)
- `subject`
- `predicted_score` (float, predicted Grade 12 score)
- `confidence_interval` (optional)
- `model_version`
- `timestamp`

#### `framework`

- `id` (Primary Key)
- `category` (e.g., "Engineering", "Arts", "Social Sciences")
- `question` (evaluation question text)
- `key_subjects` (comma-separated, e.g., "Math,Physics")
- `required_grades` (minimum grade threshold, e.g., "≥ 7.5")
- `weight` (importance weight for this question)

#### `assessment_responses`

- `id` (Primary Key)
- `student_id` (Foreign Key → students)
- `question_id` (Foreign Key → framework)
- `answer` (e.g., "Yes", "No", "Partial")
- `reasoning` (LLM explanation for the answer)
- `timestamp`

#### `career_recommendations`

- `id` (Primary Key)
- `student_id` (Foreign Key → students)
- `recommended_paths` (JSON array, e.g., ["Engineering", "Computer Science"])
- `summary` (detailed career guidance text)
- `confidence_score` (float, 0-1)
- `timestamp`

### Dynamic Subject Handling

- Subjects are **not hard-coded**; each record defines subject as a string
- Prediction logic filters by available subjects per student
- System adapts to varying subject offerings across grade levels
- Missing grades handled gracefully with interpolation or exclusion

### Data Relationships

```
students (1) ──→ (N) grades
students (1) ──→ (N) predictions
students (1) ──→ (N) assessment_responses
students (1) ──→ (N) career_recommendations
framework (1) ──→ (N) assessment_responses
```

---

## 8. Technical Stack

| Component             | Technology                       |
| --------------------- | -------------------------------- |
| **Frontend**          | Streamlit                        |
| **Backend Services**  | Python 3.10+                     |
| **Database**          | SQLite (dev) → PostgreSQL (prod) |
| **ORM**               | SQLAlchemy (optional)            |
| **ML Model**          | Scikit-learn (Linear Regression) |
| **LLM Engine**        | OpenAI API (GPT-4o, GPT-4o-mini) |
| **Structured Output** | Pydantic 2.0+                    |
| **Data Processing**   | Pandas, NumPy                    |
| **Visualization**     | Plotly (interactive charts)      |
| **Caching**           | Streamlit cache / Custom cache   |
| **CSV Handling**      | Python csv / Pandas              |
| **Async Processing**  | asyncio / concurrent.futures     |
| **Hosting**           | Railway / Streamlit Cloud        |

---

## 9. Success Metrics

| Metric                            | Target            |
| --------------------------------- | ----------------- |
| **Prediction accuracy**           | ≥ 80% per subject |
| **LLM career reasoning accuracy** | ≥ 85% relevance   |
| **Response latency**              | ≤ 5s per query    |
| **User satisfaction**             | ≥ 4/5 rating      |
| **System uptime**                 | ≥ 95%             |

---

## 10. Timeline

| Phase                                         | Duration | Deliverable            |
| --------------------------------------------- | -------- | ---------------------- |
| **Phase 1:** Data collection + schema design  | 2 weeks  | Database + sample data |
| **Phase 2:** Linear Regression implementation | 2 weeks  | ML model pipeline      |
| **Phase 3:** LLM reasoning + framework setup  | 3 weeks  | CSV framework + RAG    |
| **Phase 4:** Frontend dashboard & chatbot     | 3 weeks  | Streamlit UI           |
| **Phase 5:** Integration & testing            | 2 weeks  | Full functional system |
| **Phase 6:** Final report + presentation      | 1 week   | Submission-ready build |

**Total Duration:** 13 weeks

---

## 11. Risks & Mitigation

| Risk                    | Impact | Mitigation                                     |
| ----------------------- | ------ | ---------------------------------------------- |
| Incomplete grade data   | Medium | Impute missing grades using regression average |
| High LLM API cost       | Medium | Use GPT-3.5 and caching                        |
| CSV inconsistency       | Low    | Validate CSV format before loading             |
| Slow reasoning response | Medium | Use async and vector cache                     |
| Limited dataset         | Medium | Simulate synthetic students for testing        |

---

## 12. Future Enhancements

- 🌏 Add Vietnamese language support for chatbot reasoning
- 📚 Introduce adaptive learning path recommendations
- 🎓 Expand framework with real-world university majors
- 👥 Support multi-student batch prediction
- 📱 Deploy mobile version (React Native)
- 🔐 Implement role-based authentication system
- 📈 Advanced analytics dashboard with comparative insights
- 🤝 Integration with school management systems

---

## 13. Summary

This system integrates both **predictive analytics (ML)** and **contextual reasoning (LLM)** to deliver a hybrid AI solution for student development.

**Key Deliverables:**

- ✅ A regression-based prediction of academic trends
- ✅ A reasoning-driven career classification aligned with predefined frameworks
- ✅ A user-friendly interface for educational insights

The design ensures:

- Compliance with AI/ML academic requirements
- Scalability for future enhancements
- Practical real-world impact for educational institutions

---

## Appendix

### A. Glossary

- **LLM:** Large Language Model - AI system for natural language understanding and generation
- **Linear Regression:** Statistical method for predicting continuous values based on historical data
- **CRUD:** Create, Read, Update, Delete - basic database operations
- **RIASEC:** Realistic, Investigative, Artistic, Social, Enterprising, Conventional (career interest model)
- **Pydantic:** Python library for data validation using type hints
- **Structured Output:** JSON schema enforced by Pydantic for consistent API responses
- **Dynamic Subjects:** System capability to handle varying subject lists per student without hardcoding
- **Assessment Response:** Individual answer to a career framework question with reasoning
- **Career Framework:** CSV-based collection of questions organized by career category

### B. References

- **Scikit-learn Documentation:** https://scikit-learn.org/stable/modules/linear_model.html
- **OpenAI API Documentation:** https://platform.openai.com/docs
- **Pydantic Documentation:** https://docs.pydantic.dev/
- **Streamlit Documentation:** https://docs.streamlit.io
- **Pandas User Guide:** https://pandas.pydata.org/docs/user_guide/index.html
- **Plotly Python Documentation:** https://plotly.com/python/
- **SQLAlchemy Documentation:** https://docs.sqlalchemy.org/

---

_End of Document_
