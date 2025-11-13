"""
SQLAlchemy database models
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.config.database import Base


class User(Base):
    """Application user model"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True)
    password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f"<User(username={self.username}, is_admin={self.is_admin})>"

class Student(Base):
    """Student profile model"""
    __tablename__ = 'students'
    
    id = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # Link to user account
    name = Column(String(200), nullable=False)
    age = Column(Integer)
    school = Column(String(200))
    notes = Column(Text)  # Extracurricular activities, interests
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    user = relationship("User", backref="students")  # Link back to user
    grades = relationship("Grade", back_populates="student", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="student", cascade="all, delete-orphan")
    assessments = relationship("AssessmentResponse", back_populates="student", cascade="all, delete-orphan")
    recommendations = relationship("CareerRecommendation", back_populates="student", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Student(id={self.id}, name={self.name}, user_id={self.user_id})>"


class Grade(Base):
    """Student grade record model"""
    __tablename__ = 'grades'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String, ForeignKey('students.id'), nullable=False)
    subject = Column(String(100), nullable=False)
    grade_level = Column(Integer, nullable=False)  # 1-11
    score = Column(Float, nullable=False)  # 0-10 scale
    semester = Column(Integer)  # Optional: 1 or 2
    created_at = Column(DateTime, default=datetime.now)
    
    student = relationship("Student", back_populates="grades")
    
    def __repr__(self):
        return f"<Grade(student={self.student_id}, subject={self.subject}, level={self.grade_level}, score={self.score})>"


class Prediction(Base):
    """Grade 12 prediction model"""
    __tablename__ = 'predictions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String, ForeignKey('students.id'), nullable=False)
    subject = Column(String(100), nullable=False)
    predicted_score = Column(Float, nullable=False)
    confidence_lower = Column(Float)  # Lower bound of confidence interval
    confidence_upper = Column(Float)  # Upper bound of confidence interval
    model_version = Column(String(50), default="linear_regression_v1")
    timestamp = Column(DateTime, default=datetime.now)
    
    student = relationship("Student", back_populates="predictions")
    
    def __repr__(self):
        return f"<Prediction(student={self.student_id}, subject={self.subject}, score={self.predicted_score})>"


class Framework(Base):
    """Career framework questions model (loaded from CSV)"""
    __tablename__ = 'framework'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    riasec_code = Column(String(1), nullable=False)  # R, I, A, S, E, C
    career_category = Column(String(100), nullable=False)  # Realistic, Investigative, etc.
    question = Column(Text, nullable=False)
    key_subjects = Column(String(200))  # Comma/semicolon separated
    required_grades = Column(String(50))  # e.g., ">= 7.5"
    weight = Column(Float, default=1.0)
    description = Column(Text)
    
    # Relationships
    assessments = relationship("AssessmentResponse", back_populates="question")
    
    def __repr__(self):
        return f"<Framework({self.riasec_code}: {self.question[:50]}...)>"


class AssessmentResponse(Base):
    """Individual question assessment response"""
    __tablename__ = 'assessment_responses'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String, ForeignKey('students.id'), nullable=False)
    question_id = Column(Integer, ForeignKey('framework.id'), nullable=False)
    answer = Column(String(20), nullable=False)  # "Yes", "No", "Partial"
    reasoning = Column(Text)
    timestamp = Column(DateTime, default=datetime.now)
    
    student = relationship("Student", back_populates="assessments")
    question = relationship("Framework", back_populates="assessments")
    
    def __repr__(self):
        return f"<Assessment(student={self.student_id}, question={self.question_id}, answer={self.answer})>"


class CareerRecommendation(Base):
    """Final career recommendation model"""
    __tablename__ = 'career_recommendations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String, ForeignKey('students.id'), nullable=False)
    recommended_paths = Column(Text, nullable=False)  # JSON array of career paths
    riasec_profile = Column(String(6))  # e.g., "RIA" (top 3 Holland codes)
    summary = Column(Text)  # Detailed explanation
    confidence_score = Column(Float)  # 0-1
    timestamp = Column(DateTime, default=datetime.now)
    
    student = relationship("Student", back_populates="recommendations")
    
    def __repr__(self):
        return f"<CareerRecommendation(student={self.student_id}, riasec={self.riasec_profile})>"

