# Hệ Thống AI Phân Tích Kết Quả Học Tập và Định Hướng Nghề Nghiệp cho Học Sinh THPT

An AI-powered platform for predicting student academic performance and providing personalized career guidance using the Holland RIASEC framework.

## Features

### 📊 Academic Performance Analysis

- Track student grades from Grade 1-11
- Predict Grade 12 performance using Linear Regression
- Interactive visualizations showing grade trends
- Subject-by-subject analysis with confidence intervals

### 🎯 RIASEC Career Assessment

- Comprehensive personality assessment using Holland Code framework
- 6 personality dimensions: Realistic, Investigative, Artistic, Social, Enterprising, Conventional
- AI-powered evaluation using OpenAI GPT-4
- Personalized career path recommendations

### 💾 Student Data Management

- Full CRUD operations for student profiles and grades
- CSV import/export functionality
- PostgreSQL database for reliable data storage
- Dynamic subject handling (no hardcoded subjects)

### 🔐 Role-Based Access Control

- **Admin Role**: Can view and manage all student information
- **Student Role**: Can only view and manage their own information
- Students are linked to user accounts via `user_id` foreign key
- Access control enforced across all pages (Student Management, Dashboard, Career Assessment, AI Chatbot)

### 🤖 AI-Powered Insights

- Two-phase assessment process:
  - Phase 1: Independent question evaluation
  - Phase 2: Comprehensive career recommendation
- Evidence-based reasoning with explanations
- Confidence scoring for recommendations

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd huongNghiep
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up configuration

Create a `.streamlit/secrets.toml` file:

```toml
OPENAI_API_KEY = "your-openai-api-key-here"
```

### 4. Initialize database

The system uses PostgreSQL. Database connection is configured in `app/config/database.py`.

Current database:

```
postgresql://postgres:etJtdOhpsVUCwGoOsDlyXzTsXGNFvAdS@shinkansen.proxy.rlwy.net:51402/railway
```

The database tables will be created automatically on first run.

### 5. Run database migration (for role-based access control)

If you're upgrading from an older version, run the migration to add the `user_id` column to the students table:

```bash
python3 migrate_add_user_id_to_students.py
```

This migration:
- Adds `user_id` column to link students to user accounts
- Creates foreign key constraint
- Leaves existing students with `user_id = NULL` (admins can see all students)

### 6. Load RIASEC Framework

The RIASEC framework is automatically loaded from `asset/RIASEC_Career_Framework.csv` on first run.

## Running the App

```bash
streamlit run app/main.py
```

The application will be available at `http://localhost:8501`

## Project Structure

```
huongNghiep/
├── app/
│   ├── main.py                      # Main entry point
│   ├── config/
│   │   ├── settings.py              # Configuration constants
│   │   └── database.py              # Database connection setup
│   ├── database/
│   │   ├── __init__.py
│   │   └── models.py                # SQLAlchemy models
│   ├── services/
│   │   ├── database_service.py      # CRUD operations
│   │   ├── prediction_service.py    # ML predictions
│   │   ├── career_service.py        # Career assessment
│   │   ├── cache.py                 # Caching utilities
│   │   └── logger.py                # Logging setup
│   ├── pages/
│   │   ├── 1_Student_Management.py  # Student & grade CRUD
│   │   ├── 2_Dashboard.py           # Performance visualization
│   │   └── 3_Career_Assessment.py   # RIASEC assessment
│   └── utils/
│       └── data_utils.py            # Data processing utilities
├── asset/
│   ├── RIASEC_Career_Framework.csv  # Career framework questions
│   └── sample_student_data.csv      # Sample data for testing
├── requirements.txt                 # Python dependencies
├── PRD.md                          # Product Requirements Document
└── README.md                       # This file
```

## Database Schema

### Students Table

- Profile information (ID, name, age, school, notes)
- Timestamps for record tracking

### Grades Table

- Subject, grade level (1-11), score (0-10)
- Foreign key to student
- Dynamic subject handling

### Predictions Table

- Predicted Grade 12 scores per subject
- Confidence intervals
- Model version tracking

### Framework Table

- RIASEC career framework questions
- Category, question text, evaluation criteria
- Weights for scoring

### Assessment Responses Table

- Individual question answers (Yes/No/Partial)
- AI reasoning for each answer
- Links to student and question

### Career Recommendations Table

- Final RIASEC profile (e.g., "RIA")
- Recommended career paths
- Detailed summary and confidence score

## Usage Guide

### 1. Add a Student

- Go to home page
- Click "➕ New Student"
- Fill in student information
- Or import from CSV

### 2. Manage Grades

- Navigate to "Student Management" page
- Add grades manually or import from CSV
- Edit or delete existing grades
- View all grade records in a table

### 3. View Academic Performance

- Go to "Dashboard" page
- View interactive charts for each subject
- See Grade 12 predictions with trend lines
- Analyze overall performance statistics

### 4. Run Career Assessment

- Go to "Career Assessment" page
- Enter OpenAI API key (if not in secrets)
- Click "Start RIASEC Assessment"
- Wait for evaluation (typically 1-2 minutes)
- View results including:
  - RIASEC profile radar chart
  - Recommended career paths
  - Detailed analysis
  - Question-by-question breakdown

### 5. Export Data

- Download predictions as CSV
- Download assessment results
- Download detailed responses

## RIASEC Framework

The system uses the Holland Code (RIASEC) framework for career assessment:

- **R - Realistic**: Practical, hands-on, technical work
- **I - Investigative**: Analytical, scientific, research-oriented
- **A - Artistic**: Creative, expressive, artistic work
- **S - Social**: Helping, teaching, service-oriented
- **E - Enterprising**: Leadership, persuasion, business
- **C - Conventional**: Organized, detail-oriented, systematic

Each student receives a 3-letter Holland Code (e.g., "RIA") representing their top 3 personality types.

## Sample Data

Sample data is provided in `asset/sample_student_data.csv`:

- 2 students with complete grade histories
- Grades 1-11 for multiple subjects
- Example student profiles

## Technical Details

### Machine Learning

- **Algorithm**: Linear Regression (scikit-learn)
- **Training**: Per-subject models using grade level as feature
- **Prediction**: Extrapolate to Grade 12
- **Validation**: R² score and MAE metrics

### AI Assessment

- **LLM**: OpenAI GPT-4 / GPT-4o-mini
- **Structured Output**: Pydantic models for consistent responses
- **Parallel Processing**: Concurrent evaluation of questions
- **Two-Phase Process**:
  1. Independent question evaluation
  2. Comprehensive synthesis and recommendation

### Database

- **System**: PostgreSQL (production), SQLite (development)
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Automatic schema creation

### Frontend

- **Framework**: Streamlit
- **Visualization**: Plotly for interactive charts
- **Caching**: Streamlit cache for database connections

## API Costs

Typical API costs per assessment:

- ~40 questions × $0.001 (GPT-4o-mini) = ~$0.04
- Final recommendation (GPT-4o) = ~$0.02
- **Total**: ~$0.06 per complete assessment

## Troubleshooting

### Database Connection Issues

- Verify PostgreSQL connection string in `app/config/database.py`
- Check network connectivity
- Ensure database exists and is accessible

### Missing RIASEC Framework

- Verify `asset/RIASEC_Career_Framework.csv` exists
- Check file format (CSV with proper headers)
- Restart application to reload framework

### API Key Errors

- Verify OpenAI API key is valid
- Check API quota and billing
- Ensure key has GPT-4 access

### Grade Prediction Issues

- Need minimum 2 grades per subject for prediction
- Check for data quality issues (null values, invalid scores)
- Review grade level values (must be 1-11)

## Contributing

This is an academic project for COS40005 Computing Technology Project A.

## License

[MIT](LICENSE)

## Contact

Tuan (Henry) Hung Nguyen

---

**Built with:** Python • Streamlit • OpenAI GPT-4 • PostgreSQL • Scikit-learn • Plotly
