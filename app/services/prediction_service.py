"""
ML Prediction Service for Grade 12 predictions using Linear Regression
"""
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from typing import Dict, List, Tuple, Optional
from app.services.logger import logger
import streamlit as st


class PredictionService:
    """Service for predicting Grade 12 scores using Linear Regression"""
    
    def __init__(self):
        self.models: Dict[str, LinearRegression] = {}
        self.model_metrics: Dict[str, Dict] = {}
    
    def train_model_for_subject(self, grades_df: pd.DataFrame, subject: str) -> Optional[LinearRegression]:
        """
        Train a Linear Regression model for a specific subject
        
        Args:
            grades_df: DataFrame with columns [grade_level, score]
            subject: Subject name
        
        Returns:
            Trained LinearRegression model or None if insufficient data
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
        
        # Calculate metrics
        r2 = model.score(X, y)
        predictions = model.predict(X)
        mae = np.mean(np.abs(y - predictions))
        
        # Store model and metrics
        self.models[subject] = model
        self.model_metrics[subject] = {
            'r2_score': r2,
            'mae': mae,
            'data_points': len(subject_df),
            'coefficient': float(model.coef_[0]),
            'intercept': float(model.intercept_)
        }
        
        logger.info(f"Trained model for {subject}: R² = {r2:.3f}, MAE = {mae:.3f}")
        return model
    
    def predict_grade_12(self, student_id: str, grades_df: pd.DataFrame) -> List[Dict]:
        """
        Predict Grade 12 scores for all subjects
        
        Args:
            student_id: Student ID
            grades_df: DataFrame with student's grades
        
        Returns:
            List of prediction dictionaries
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
            
            # Calculate simple confidence interval (based on historical variance)
            subject_df = grades_df[grades_df['subject'] == subject]
            std_dev = subject_df['score'].std()
            confidence_lower = max(0, predicted_score - std_dev)
            confidence_upper = min(10, predicted_score + std_dev)
            
            # Create prediction dictionary
            prediction = {
                'student_id': student_id,
                'subject': subject,
                'predicted_score': float(predicted_score),
                'confidence_lower': float(confidence_lower),
                'confidence_upper': float(confidence_upper),
                'model_version': 'linear_regression_v1',
                'r2_score': self.model_metrics[subject]['r2_score'],
                'mae': self.model_metrics[subject]['mae']
            }
            predictions.append(prediction)
        
        logger.info(f"Generated {len(predictions)} predictions for student: {student_id}")
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
            
            # Calculate trend line for visualization
            all_grades = list(range(1, 13))
            trend_scores = [float(np.clip(model.predict([[g]])[0], 0, 10)) for g in all_grades]
        else:
            predicted_score = None
            trend_scores = None
        
        return {
            'subject': subject,
            'historical_grades': historical_grades,
            'historical_scores': historical_scores,
            'predicted_grade_12': predicted_score,
            'trend_line_grades': all_grades if trend_scores else None,
            'trend_line_scores': trend_scores,
            'metrics': self.model_metrics.get(subject, {})
        }
    
    def get_all_trends(self, grades_df: pd.DataFrame) -> List[Dict]:
        """Get trend data for all subjects"""
        subjects = grades_df['subject'].unique()
        return [self.get_trend_data(grades_df, subject) for subject in subjects]
    
    def analyze_student_strengths(self, predictions: List[Dict], threshold: float = 8.0) -> Dict:
        """
        Analyze student's strengths based on predictions
        
        Args:
            predictions: List of prediction dictionaries
            threshold: Score threshold for "strong" subjects
        
        Returns:
            Analysis dictionary
        """
        if not predictions:
            return {
                'strong_subjects': [],
                'weak_subjects': [],
                'average_predicted_score': 0,
                'top_subject': None,
                'improvement_areas': []
            }
        
        # Sort predictions by score
        sorted_preds = sorted(predictions, key=lambda x: x['predicted_score'], reverse=True)
        
        strong_subjects = [p['subject'] for p in sorted_preds if p['predicted_score'] >= threshold]
        weak_subjects = [p['subject'] for p in sorted_preds if p['predicted_score'] < 7.0]
        
        avg_score = np.mean([p['predicted_score'] for p in predictions])
        
        top_subject = sorted_preds[0]['subject'] if sorted_preds else None
        
        # Identify subjects needing improvement (low R² or declining trend)
        improvement_areas = [
            p['subject'] for p in predictions 
            if p.get('r2_score', 1.0) < 0.7 or p['predicted_score'] < 7.0
        ]
        
        return {
            'strong_subjects': strong_subjects,
            'weak_subjects': weak_subjects,
            'average_predicted_score': float(avg_score),
            'top_subject': top_subject,
            'improvement_areas': improvement_areas,
            'all_predictions': sorted_preds
        }


@st.cache_resource
def get_prediction_service():
    """Get cached prediction service instance"""
    return PredictionService()

