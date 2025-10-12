"""
Career Assessment Service using RIASEC framework and LLM
"""
import openai
from pydantic import BaseModel
from typing import List, Literal, Optional, Dict
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.services.logger import logger
import streamlit as st


class QuestionResponse(BaseModel):
    """Structured response for a single question"""
    answer: Literal["Yes", "No", "Partial"]
    reasoning: str


class RIASECScore(BaseModel):
    """RIASEC profile scores"""
    R_score: float  # Realistic
    I_score: float  # Investigative
    A_score: float  # Artistic
    S_score: float  # Social
    E_score: float  # Enterprising
    C_score: float  # Conventional


class FinalRecommendation(BaseModel):
    """Structured final career recommendation"""
    riasec_profile: str  # e.g., "RIA" (top 3 codes)
    recommended_paths: List[str]  # 1-3 career paths
    summary: str  # Detailed explanation
    confidence_score: float  # 0-1


class CareerAssessmentService:
    """Service for evaluating students against RIASEC career framework"""
    
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
    
    def evaluate_single_question(
        self,
        student_name: str,
        student_profile: str,
        question: str,
        question_id: int,
        riasec_code: str
    ) -> Dict:
        """
        Evaluate a single question independently
        
        IMPORTANT: No context from other questions
        
        Args:
            student_name: Student's name
            student_profile: Complete student academic profile
            question: The evaluation question
            question_id: Question ID from database
            riasec_code: RIASEC category (R, I, A, S, E, C)
        
        Returns:
            Dictionary with question_id, answer, reasoning
        """
        # Create prompt
        prompt = f"""You are evaluating a student for career guidance using the Holland RIASEC framework.

RIASEC Code: {riasec_code} ({self._get_riasec_name(riasec_code)})

Question: {question}

Student: {student_name}
{student_profile}

Evaluate this question INDEPENDENTLY (do not consider other questions).

Provide:
1. Answer: Yes, No, or Partial
   - Yes: Strong evidence supporting this trait
   - No: Little or no evidence for this trait
   - Partial: Some evidence but not conclusive

2. Reasoning: Explain your answer based on the student's grades, performance trends, and notes.
   Be specific and reference actual subjects, grades, or trends.

Answer format should be clear and concise."""
        
        try:
            # Call OpenAI API with structured output
            response = self.client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format=QuestionResponse,
                temperature=0.3
            )
            
            parsed = response.choices[0].message.parsed
            
            logger.info(f"Q{question_id} ({riasec_code}): {parsed.answer}")
            
            return {
                'question_id': question_id,
                'answer': parsed.answer,
                'reasoning': parsed.reasoning
            }
            
        except Exception as e:
            logger.error(f"Error evaluating question {question_id}: {e}")
            return {
                'question_id': question_id,
                'answer': 'Error',
                'reasoning': f"Evaluation failed: {str(e)}"
            }
    
    def evaluate_all_questions(
        self,
        student_name: str,
        student_profile: str,
        framework_df: pd.DataFrame,
        max_workers: int = 5
    ) -> List[Dict]:
        """
        Evaluate all questions in parallel
        
        Each question is evaluated independently
        
        Args:
            student_name: Student's name
            student_profile: Complete student academic profile
            framework_df: DataFrame with RIASEC questions
            max_workers: Number of parallel workers
        
        Returns:
            List of assessment response dictionaries
        """
        responses = []
        
        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}
            
            for idx, row in framework_df.iterrows():
                future = executor.submit(
                    self.evaluate_single_question,
                    student_name,
                    student_profile,
                    row['question'],
                    int(row['id']),
                    row['riasec_code']
                )
                futures[future] = idx
            
            # Collect results as they complete
            for future in as_completed(futures):
                response = future.result()
                responses.append(response)
        
        logger.info(f"Completed evaluation of {len(responses)} questions")
        return responses
    
    def calculate_riasec_scores(self, assessment_responses: List[Dict], framework_df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate RIASEC profile scores based on assessment responses
        
        Args:
            assessment_responses: List of assessment response dicts
            framework_df: DataFrame with questions and weights
        
        Returns:
            Dictionary with scores for each RIASEC code
        """
        # Initialize scores
        riasec_scores = {
            'R': 0.0,  # Realistic
            'I': 0.0,  # Investigative
            'A': 0.0,  # Artistic
            'S': 0.0,  # Social
            'E': 0.0,  # Enterprising
            'C': 0.0   # Conventional
        }
        
        riasec_weights = {code: 0.0 for code in riasec_scores.keys()}
        
        # Calculate weighted scores
        for response in assessment_responses:
            # Find corresponding question
            question = framework_df[framework_df['id'] == response['question_id']].iloc[0]
            riasec_code = question['riasec_code']
            weight = float(question['weight'])
            
            # Calculate score contribution
            if response['answer'] == 'Yes':
                score = 1.0
            elif response['answer'] == 'Partial':
                score = 0.5
            else:  # No or Error
                score = 0.0
            
            riasec_scores[riasec_code] += score * weight
            riasec_weights[riasec_code] += weight
        
        # Normalize scores
        for code in riasec_scores.keys():
            if riasec_weights[code] > 0:
                riasec_scores[code] = (riasec_scores[code] / riasec_weights[code]) * 100
        
        return riasec_scores
    
    def generate_final_recommendation(
        self,
        student_name: str,
        student_profile: str,
        assessment_responses: List[Dict],
        framework_df: pd.DataFrame,
        riasec_scores: Dict[str, float]
    ) -> Dict:
        """
        Generate final career recommendation based on all answers
        
        This is Phase 2: Analyzing all answers together
        
        Args:
            student_name: Student's name
            student_profile: Complete student academic profile
            assessment_responses: List of all assessment responses
            framework_df: DataFrame with questions
            riasec_scores: Calculated RIASEC scores
        
        Returns:
            Career recommendation dictionary
        """
        # Prepare summary of all Q&A
        qa_summary = self._format_qa_summary(assessment_responses, framework_df)
        
        # Format RIASEC scores
        riasec_summary = "\n".join([
            f"{code} ({self._get_riasec_name(code)}): {score:.1f}/100"
            for code, score in sorted(riasec_scores.items(), key=lambda x: x[1], reverse=True)
        ])
        
        # Get top 3 RIASEC codes
        top_codes = sorted(riasec_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        riasec_profile = "".join([code for code, _ in top_codes])
        
        # Create final recommendation prompt
        prompt = f"""You are a career counselor analyzing a student's complete RIASEC assessment.

Student: {student_name}
{student_profile}

RIASEC Profile Scores:
{riasec_summary}

Top RIASEC Profile: {riasec_profile}

Assessment Results Summary:
{qa_summary}

Based on ALL the assessment results above, provide:

1. RIASEC Profile: The top 3 RIASEC codes (already calculated as: {riasec_profile})

2. Recommended Career Paths: Provide 2-3 specific career paths that align with this RIASEC profile.
   Examples based on profiles:
   - RIE: Engineering, Architecture, Computer Science
   - IAS: Research Scientist, Data Analyst, Academic
   - ASE: Graphic Designer, Marketing, Creative Director
   - SEI: Business Management, Entrepreneurship, Sales
   - etc.

3. Detailed Summary: Write a comprehensive explanation (3-4 paragraphs) covering:
   - Student's key strengths based on the assessment
   - Why these career paths fit the student's RIASEC profile
   - How their academic performance supports these recommendations
   - Specific subjects or skills that align with these careers
   - Areas for development or improvement

4. Confidence Score: Provide a confidence score (0-1) based on:
   - Consistency of answers within RIASEC categories
   - Strength of academic performance
   - Clarity of the RIASEC profile

Be specific, supportive, and actionable in your recommendations."""
        
        try:
            response = self.client.beta.chat.completions.parse(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format=FinalRecommendation,
                temperature=0.5
            )
            
            parsed = response.choices[0].message.parsed
            
            return {
                'riasec_profile': parsed.riasec_profile,
                'recommended_paths': parsed.recommended_paths,
                'summary': parsed.summary,
                'confidence_score': parsed.confidence_score,
                'riasec_scores': riasec_scores
            }
            
        except Exception as e:
            logger.error(f"Error generating final recommendation: {e}")
            return {
                'riasec_profile': riasec_profile,
                'recommended_paths': ["Error generating recommendations"],
                'summary': f"Failed to generate recommendation: {str(e)}",
                'confidence_score': 0.0,
                'riasec_scores': riasec_scores
            }
    
    def _format_student_profile(
        self,
        student: Dict,
        grades_df: pd.DataFrame,
        predictions_df: pd.DataFrame
    ) -> str:
        """Format student data for LLM context"""
        
        # Student info
        profile = f"""
Name: {student['name']}
Age: {student['age']}
School: {student['school']}
Notes: {student.get('notes', 'N/A')}

Grade History (Grades 1-11):
"""
        
        # Group grades by subject
        for subject in sorted(grades_df['subject'].unique()):
            subject_grades = grades_df[grades_df['subject'] == subject].sort_values('grade_level')
            grades_str = ", ".join([
                f"G{row['grade_level']}: {row['score']:.1f}"
                for _, row in subject_grades.iterrows()
            ])
            
            # Calculate average
            avg_score = subject_grades['score'].mean()
            
            profile += f"\n  {subject}: {grades_str} (Avg: {avg_score:.1f})"
        
        # Predicted Grade 12
        if not predictions_df.empty:
            profile += "\n\nPredicted Grade 12 Scores:\n"
            for _, pred in predictions_df.iterrows():
                profile += f"  {pred['subject']}: {pred['predicted_score']:.1f}"
                if 'confidence_lower' in pred and pred['confidence_lower'] is not None:
                    profile += f" (CI: {pred['confidence_lower']:.1f}-{pred['confidence_upper']:.1f})"
                profile += "\n"
        
        return profile
    
    def _format_qa_summary(self, responses: List[Dict], framework_df: pd.DataFrame) -> str:
        """Format all Q&A for final recommendation"""
        summary = ""
        
        # Group by RIASEC code
        riasec_groups = {'R': [], 'I': [], 'A': [], 'S': [], 'E': [], 'C': []}
        
        for resp in responses:
            question = framework_df[framework_df['id'] == resp['question_id']].iloc[0]
            riasec_code = question['riasec_code']
            riasec_groups[riasec_code].append((question['question'], resp))
        
        # Format by RIASEC category
        for code in ['R', 'I', 'A', 'S', 'E', 'C']:
            if riasec_groups[code]:
                summary += f"\n{code} - {self._get_riasec_name(code)}:\n"
                for question_text, resp in riasec_groups[code]:
                    summary += f"  Q: {question_text}\n"
                    summary += f"  A: {resp['answer']} - {resp['reasoning']}\n"
        
        return summary
    
    def _get_riasec_name(self, code: str) -> str:
        """Get full name for RIASEC code"""
        names = {
            'R': 'Realistic',
            'I': 'Investigative',
            'A': 'Artistic',
            'S': 'Social',
            'E': 'Enterprising',
            'C': 'Conventional'
        }
        return names.get(code, code)


@st.cache_resource
def get_career_service(_api_key: str):
    """Get cached career assessment service instance"""
    return CareerAssessmentService(_api_key)

