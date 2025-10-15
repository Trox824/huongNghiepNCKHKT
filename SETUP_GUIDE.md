# Setup Guide - Student Career Guidance System

## ✅ System Ready!

Your Student Career Guidance System has been successfully set up. All files are in place and ready to run.

## 📁 What's Been Created

### Core System Files

- ✅ `app/main.py` - Main application entry point
- ✅ `app/config/database.py` - PostgreSQL connection (configured)
- ✅ `app/database/models.py` - SQLAlchemy data models
- ✅ `app/services/database_service.py` - CRUD operations
- ✅ `app/services/prediction_service.py` - ML predictions (Linear Regression)
- ✅ `app/services/career_service.py` - RIASEC career assessment (LLM)

### Frontend Pages (No Emojis in Filenames)

- ✅ `app/pages/1_Student_Management.py` - Student & grade CRUD
- ✅ `app/pages/2_Dashboard.py` - Performance visualization
- ✅ `app/pages/3_Career_Assessment.py` - RIASEC assessment

### Data Files

- ✅ `asset/RIASEC_Career_Framework.csv` - 37 career assessment questions
- ✅ `asset/sample_student_data.csv` - Sample data for 2 students
- ✅ `requirements.txt` - Python dependencies (cleaned up)

### Documentation

- ✅ `README.md` - Complete system documentation
- ✅ `PRD.md` - Product Requirements Document
- ✅ `IMPLEMENTATION_PLAN.md` - Development guide
- ✅ `init_db.py` - Database initialization script

### 🗑️ Cleaned Up (Old EU AI Act System Files Removed)

- ❌ `app/services/playstore.py`
- ❌ `app/services/selenium_scraper.py`
- ❌ `app/utils/review_filter.py`
- ❌ `app/models/app_data.py`
- ❌ `app/models/ar_miner_model.pkl`
- ❌ `app/ui/*.py` (all old UI files)
- ❌ `asset/EU_AI_Act_Assessment_Questions.csv`

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set OpenAI API Key

Create `.streamlit/secrets.toml`:

```toml
OPENAI_API_KEY = "your-key-here"
```

### 3. Initialize Database

```bash
python init_db.py
```

This will:

- Create all database tables
- Load the RIASEC framework (37 questions)
- Optionally load sample student data

### 4. Run the Application

```bash
streamlit run app/main.py
```

Open browser at: `http://localhost:8501`

## 📊 Database Configuration

**PostgreSQL Connection (Already Configured):**

```
postgresql://postgres:etJtdOhpsVUCwGoOsDlyXzTsXGNFvAdS@shinkansen.proxy.rlwy.net:51402/railway
```

Connection is set in `app/config/database.py`

## 🎯 Key Features

### 1. Student Management

- Full CRUD operations for students and grades
- CSV import/export
- Dynamic subject handling (no hardcoded subjects)

### 2. Academic Dashboard

- Interactive Plotly visualizations
- Grade 1-11 historical data
- Grade 12 predictions with confidence intervals
- Subject-by-subject analysis

### 3. RIASEC Career Assessment

- 37 questions across 6 personality types (R-I-A-S-E-C)
- AI-powered evaluation using GPT-4
- Two-phase process:
  - Phase 1: Independent question evaluation
  - Phase 2: Comprehensive career recommendation
- Radar chart visualization
- Downloadable results

## 📋 Holland RIASEC Framework

The system uses 6 personality dimensions:

| Code  | Type          | Description                      | Example Careers                    |
| ----- | ------------- | -------------------------------- | ---------------------------------- |
| **R** | Realistic     | Practical, hands-on, technical   | Engineer, Mechanic, Builder        |
| **I** | Investigative | Analytical, scientific, research | Scientist, Analyst, Researcher     |
| **A** | Artistic      | Creative, expressive, artistic   | Artist, Writer, Designer           |
| **S** | Social        | Helping, teaching, service       | Teacher, Counselor, Nurse          |
| **E** | Enterprising  | Leadership, persuasion, business | Manager, Entrepreneur, Sales       |
| **C** | Conventional  | Organized, detail-oriented       | Accountant, Administrator, Analyst |

Each student gets a 3-letter Holland Code (e.g., "RIA") representing their top 3 types.

## 📝 Typical Workflow

1. **Create Student**

   - Go to home page → Add new student
   - Or import from CSV

2. **Add Grades**

   - Navigate to "Student Management"
   - Add grades for Grades 1-11
   - Or import CSV with all grade data

3. **View Dashboard**

   - Go to "Dashboard" page
   - See interactive charts for each subject
   - View Grade 12 predictions

4. **Run Assessment**

   - Go to "Career Assessment" page
   - Click "Start RIASEC Assessment"
   - Wait ~1-2 minutes for AI evaluation
   - View results and recommendations

5. **Export Data**
   - Download predictions CSV
   - Download assessment results
   - Download detailed responses

## 💰 API Costs

Typical costs per complete assessment:

- **Question Evaluation**: ~37 questions × $0.001 = ~$0.04 (GPT-4o-mini)
- **Final Recommendation**: ~$0.02 (GPT-4o)
- **Total**: ~$0.06 per student assessment

## 🔧 Troubleshooting

### Database Connection Error

- Check PostgreSQL connection in `app/config/database.py`
- Verify network connectivity
- Run `python init_db.py` to create tables

### Missing RIASEC Framework

- Check `asset/RIASEC_Career_Framework.csv` exists
- Run `python init_db.py` to reload

### OpenAI API Error

- Verify API key in `.streamlit/secrets.toml`
- Check API quota and billing
- Ensure GPT-4 access is enabled

### No Predictions Generated

- Need minimum 2 grade records per subject
- Check data quality (no null values, scores 0-10)
- Grade levels must be 1-11

## 📦 File Structure Summary

```
huongNghiep/
├── app/
│   ├── main.py                          # ✅ NEW - Main entry
│   ├── config/
│   │   ├── settings.py
│   │   └── database.py                  # ✅ NEW - PostgreSQL config
│   ├── database/
│   │   ├── __init__.py                  # ✅ NEW
│   │   └── models.py                    # ✅ NEW - SQLAlchemy models
│   ├── services/
│   │   ├── database_service.py          # ✅ NEW - CRUD
│   │   ├── prediction_service.py        # ✅ NEW - ML
│   │   ├── career_service.py            # ✅ NEW - LLM assessment
│   │   ├── analysis.py                  # ⚠️ OLD - can be removed
│   │   ├── cache.py                     # ✅ Kept
│   │   └── logger.py                    # ✅ Kept
│   ├── pages/
│   │   ├── 1_Student_Management.py      # ✅ NEW - CRUD UI
│   │   ├── 2_Dashboard.py               # ✅ NEW - Visualizations
│   │   └── 3_Career_Assessment.py       # ✅ NEW - RIASEC UI
│   └── utils/
│       └── data_utils.py                # ✅ Kept
├── asset/
│   ├── RIASEC_Career_Framework.csv      # ✅ NEW - 37 questions
│   └── sample_student_data.csv          # ✅ NEW - Test data
├── requirements.txt                     # ✅ UPDATED
├── README.md                            # ✅ UPDATED
├── PRD.md                              # ✅ UPDATED
├── init_db.py                           # ✅ NEW
└── SETUP_GUIDE.md                       # ✅ This file
```

## ✅ All Tasks Completed

- ✅ Phase 1: Data models & database schema (PostgreSQL)
- ✅ Phase 2: ML prediction service (Linear Regression)
- ✅ Phase 3: Career assessment service (RIASEC + LLM)
- ✅ Phase 4: Frontend pages (Management, Dashboard, Assessment)
- ✅ Phase 5: Sample CSV files
- ✅ Phase 6: Updated requirements.txt
- ✅ Phase 7: Removed old files
- ✅ Phase 8: New main.py
- ✅ Phase 9: Testing & validation
- ✅ Phase 10: Documentation
- ✅ RIASEC framework CSV created
- ✅ PostgreSQL database configured

## 🎉 Ready to Use!

Your system is ready for:

- Academic performance tracking
- Grade 12 predictions
- Career assessments
- Student guidance

Run `python3 -m streamlit run app/main.py` to start!

---

**Need Help?** Check README.md or PRD.md for detailed information.
