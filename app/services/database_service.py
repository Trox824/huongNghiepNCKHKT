"""
Database service for CRUD operations
"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from app.database.models import Student, Grade, Prediction, Framework, AssessmentResponse, CareerRecommendation
from app.services.logger import logger
import pandas as pd
from datetime import datetime


class DatabaseService:
    """Service for database CRUD operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # =====================
    # STUDENT OPERATIONS
    # =====================
    
    def create_student(self, student_id: str, name: str, age: int, school: str, notes: str = "") -> Student:
        """Create a new student"""
        student = Student(
            id=student_id,
            name=name,
            age=age,
            school=school,
            notes=notes
        )
        self.db.add(student)
        self.db.commit()
        self.db.refresh(student)
        logger.info(f"Created student: {student_id} - {name}")
        return student
    
    def get_student(self, student_id: str) -> Optional[Student]:
        """Get student by ID"""
        return self.db.query(Student).filter(Student.id == student_id).first()
    
    def get_all_students(self) -> List[Student]:
        """Get all students"""
        return self.db.query(Student).order_by(Student.name).all()
    
    def update_student(self, student_id: str, **kwargs) -> Optional[Student]:
        """Update student information"""
        student = self.get_student(student_id)
        if student:
            for key, value in kwargs.items():
                if hasattr(student, key):
                    setattr(student, key, value)
            student.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(student)
            logger.info(f"Updated student: {student_id}")
        return student
    
    def delete_student(self, student_id: str) -> bool:
        """Delete student and all related records"""
        student = self.get_student(student_id)
        if student:
            self.db.delete(student)
            self.db.commit()
            logger.info(f"Deleted student: {student_id}")
            return True
        return False
    
    # =====================
    # GRADE OPERATIONS
    # =====================
    
    def add_grade(self, student_id: str, subject: str, grade_level: int, score: float, semester: Optional[int] = None) -> Grade:
        """Add a grade record"""
        grade = Grade(
            student_id=student_id,
            subject=subject,
            grade_level=grade_level,
            score=score,
            semester=semester
        )
        self.db.add(grade)
        self.db.commit()
        self.db.refresh(grade)
        logger.info(f"Added grade for {student_id}: {subject} Grade {grade_level} = {score}")
        return grade
    
    def get_student_grades(self, student_id: str) -> List[Grade]:
        """Get all grades for a student"""
        return self.db.query(Grade).filter(Grade.student_id == student_id).order_by(Grade.grade_level, Grade.subject).all()
    
    def get_student_grades_df(self, student_id: str) -> pd.DataFrame:
        """Get student grades as DataFrame"""
        grades = self.get_student_grades(student_id)
        if not grades:
            return pd.DataFrame()
        
        data = [{
            'id': g.id,
            'student_id': g.student_id,
            'subject': g.subject,
            'grade_level': g.grade_level,
            'score': g.score,
            'semester': g.semester
        } for g in grades]
        
        return pd.DataFrame(data)
    
    def update_grade(self, grade_id: int, **kwargs) -> Optional[Grade]:
        """Update a grade record"""
        grade = self.db.query(Grade).filter(Grade.id == grade_id).first()
        if grade:
            for key, value in kwargs.items():
                if hasattr(grade, key):
                    setattr(grade, key, value)
            self.db.commit()
            self.db.refresh(grade)
            logger.info(f"Updated grade: {grade_id}")
        return grade
    
    def delete_grade(self, grade_id: int) -> bool:
        """Delete a grade record"""
        grade = self.db.query(Grade).filter(Grade.id == grade_id).first()
        if grade:
            self.db.delete(grade)
            self.db.commit()
            logger.info(f"Deleted grade: {grade_id}")
            return True
        return False
    
    def delete_student_grades(self, student_id: str) -> int:
        """Delete all grades for a student"""
        count = self.db.query(Grade).filter(Grade.student_id == student_id).delete()
        self.db.commit()
        logger.info(f"Deleted {count} grades for student: {student_id}")
        return count
    
    # =====================
    # PREDICTION OPERATIONS
    # =====================
    
    def save_predictions(self, student_id: str, predictions: List[Dict]) -> List[Prediction]:
        """Save Grade 12 predictions for a student"""
        # Delete old predictions
        self.db.query(Prediction).filter(Prediction.student_id == student_id).delete()
        
        # Save new predictions
        prediction_objects = []
        for pred in predictions:
            prediction = Prediction(
                student_id=student_id,
                subject=pred['subject'],
                predicted_score=pred['predicted_score'],
                confidence_lower=pred.get('confidence_lower'),
                confidence_upper=pred.get('confidence_upper'),
                model_version=pred.get('model_version', 'linear_regression_v1')
            )
            self.db.add(prediction)
            prediction_objects.append(prediction)
        
        self.db.commit()
        logger.info(f"Saved {len(predictions)} predictions for student: {student_id}")
        return prediction_objects
    
    def get_student_predictions(self, student_id: str) -> List[Prediction]:
        """Get all predictions for a student"""
        return self.db.query(Prediction).filter(Prediction.student_id == student_id).all()
    
    def get_student_predictions_df(self, student_id: str) -> pd.DataFrame:
        """Get student predictions as DataFrame"""
        predictions = self.get_student_predictions(student_id)
        if not predictions:
            return pd.DataFrame()
        
        data = [{
            'subject': p.subject,
            'predicted_score': p.predicted_score,
            'confidence_lower': p.confidence_lower,
            'confidence_upper': p.confidence_upper,
            'timestamp': p.timestamp
        } for p in predictions]
        
        return pd.DataFrame(data)
    
    # =====================
    # FRAMEWORK OPERATIONS
    # =====================
    
    def load_framework_from_csv(self, csv_path: str) -> int:
        """Load career framework questions from CSV"""
        import pandas as pd
        
        # Read CSV
        df = pd.read_csv(csv_path)
        
        # Clear existing framework
        self.db.query(Framework).delete()
        
        # Load new framework
        count = 0
        for _, row in df.iterrows():
            framework = Framework(
                riasec_code=row['riasec_code'],
                career_category=row['career_category'],
                question=row['question'],
                key_subjects=row.get('key_subjects', ''),
                required_grades=row.get('required_grades', ''),
                weight=float(row.get('weight', 1.0)),
                description=row.get('description', '')
            )
            self.db.add(framework)
            count += 1
        
        self.db.commit()
        logger.info(f"Loaded {count} framework questions from {csv_path}")
        return count
    
    def get_framework_questions(self, riasec_code: Optional[str] = None) -> List[Framework]:
        """Get framework questions, optionally filtered by RIASEC code"""
        query = self.db.query(Framework)
        if riasec_code:
            query = query.filter(Framework.riasec_code == riasec_code)
        return query.all()
    
    def get_framework_df(self) -> pd.DataFrame:
        """Get framework as DataFrame"""
        questions = self.get_framework_questions()
        if not questions:
            return pd.DataFrame()
        
        data = [{
            'id': q.id,
            'riasec_code': q.riasec_code,
            'career_category': q.career_category,
            'question': q.question,
            'key_subjects': q.key_subjects,
            'required_grades': q.required_grades,
            'weight': q.weight,
            'description': q.description
        } for q in questions]
        
        return pd.DataFrame(data)
    
    # =====================
    # ASSESSMENT OPERATIONS
    # =====================
    
    def save_assessment_responses(self, student_id: str, responses: List[Dict]) -> List[AssessmentResponse]:
        """Save assessment responses for a student"""
        # Delete old assessments
        self.db.query(AssessmentResponse).filter(AssessmentResponse.student_id == student_id).delete()
        
        # Save new assessments
        assessment_objects = []
        for resp in responses:
            assessment = AssessmentResponse(
                student_id=student_id,
                question_id=resp['question_id'],
                answer=resp['answer'],
                reasoning=resp.get('reasoning', '')
            )
            self.db.add(assessment)
            assessment_objects.append(assessment)
        
        self.db.commit()
        logger.info(f"Saved {len(responses)} assessment responses for student: {student_id}")
        return assessment_objects
    
    def get_student_assessments(self, student_id: str) -> List[AssessmentResponse]:
        """Get all assessment responses for a student"""
        return self.db.query(AssessmentResponse).filter(AssessmentResponse.student_id == student_id).all()
    
    # =====================
    # CAREER RECOMMENDATION OPERATIONS
    # =====================
    
    def save_career_recommendation(self, student_id: str, recommendation: Dict) -> CareerRecommendation:
        """Save career recommendation for a student"""
        # Delete old recommendation
        self.db.query(CareerRecommendation).filter(CareerRecommendation.student_id == student_id).delete()
        
        # Save new recommendation
        import json
        career_rec = CareerRecommendation(
            student_id=student_id,
            recommended_paths=json.dumps(recommendation['recommended_paths']),
            riasec_profile=recommendation.get('riasec_profile', ''),
            summary=recommendation.get('summary', ''),
            confidence_score=recommendation.get('confidence_score', 0.0)
        )
        self.db.add(career_rec)
        self.db.commit()
        self.db.refresh(career_rec)
        logger.info(f"Saved career recommendation for student: {student_id}")
        return career_rec
    
    def get_student_recommendation(self, student_id: str) -> Optional[CareerRecommendation]:
        """Get career recommendation for a student"""
        return self.db.query(CareerRecommendation).filter(CareerRecommendation.student_id == student_id).first()
    
    # =====================
    # BULK OPERATIONS
    # =====================
    
    def import_students_from_csv(self, csv_path: str) -> int:
        """Import students and grades from CSV"""
        df = pd.read_csv(csv_path)
        
        students_created = set()
        grades_created = 0
        
        for _, row in df.iterrows():
            student_id = row['student_id']
            
            # Create student if not exists
            if student_id not in students_created:
                existing = self.get_student(student_id)
                if not existing:
                    self.create_student(
                        student_id=student_id,
                        name=row['student_name'],
                        age=int(row.get('age', 17)),
                        school=row.get('school', 'Unknown'),
                        notes=row.get('notes', '')
                    )
                students_created.add(student_id)
            
            # Add grade
            self.add_grade(
                student_id=student_id,
                subject=row['subject'],
                grade_level=int(row['grade_level']),
                score=float(row['score']),
                semester=int(row['semester']) if 'semester' in row and pd.notna(row['semester']) else None
            )
            grades_created += 1
        
        logger.info(f"Imported {len(students_created)} students and {grades_created} grades from {csv_path}")
        return len(students_created)

