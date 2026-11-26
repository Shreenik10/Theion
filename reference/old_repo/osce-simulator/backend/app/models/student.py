from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from .user import User, Base
from .student_consultation import StudentConsultation
from .evaluation_category import EvaluationCategory
import uuid
from datetime import datetime
from typing import List, Dict, Optional

class Student(User):
    """
    Student model inheriting from User with student-specific functionality.
    """
    __tablename__ = "students"
    
    id = Column(String, ForeignKey("users.id"), primary_key=True, index=True)
    
    # Relationships
    consultations = relationship("StudentConsultation", back_populates="student")
    
    def start_consultation(self, consultation_id: str, db_session) -> StudentConsultation:
        """
        Start a new consultation attempt.
        
        Args:
            consultation_id: ID of the consultation to start
            db_session: Database session for persistence
            
        Returns:
            StudentConsultation: The newly created consultation attempt
        """
        # Get the next attempt number for this student and consultation
        existing_attempts = db_session.query(StudentConsultation).filter_by(
            student_id=self.id,
            consultation_id=consultation_id
        ).count()
        
        attempt_number = existing_attempts + 1
        
        # Create new student consultation record
        student_consultation = StudentConsultation(
            id=str(uuid.uuid4()),
            student_id=self.id,
            consultation_id=consultation_id,
            attempt_number=attempt_number,
            in_progress=True,
            completed=False,
            started_date=datetime.utcnow()
        )
        
        db_session.add(student_consultation)
        db_session.commit()
        
        return student_consultation
    
    def submit_consultation(self, student_consultation_id: str, db_session) -> bool:
        """
        Submit a consultation for evaluation.
        
        Args:
            student_consultation_id: ID of the consultation to submit
            db_session: Database session for persistence
            
        Returns:
            bool: True if submission was successful
        """
        # Find the student consultation
        student_consultation = db_session.query(StudentConsultation).filter_by(
            id=student_consultation_id,
            student_id=self.id
        ).first()
        
        if not student_consultation:
            raise ValueError(f"Student consultation {student_consultation_id} not found")
        
        if not student_consultation.in_progress:
            raise ValueError("Consultation is not in progress")
        
        # Mark as completed and set submission date
        student_consultation.in_progress = False
        student_consultation.completed = True
        student_consultation.submitted_date = datetime.utcnow()
        student_consultation.completed_date = datetime.utcnow()
        
        db_session.commit()
        
        return True
    
    def view_metrics(self, db_session) -> Dict:
        """
        View performance metrics across all consultations.
        
        Args:
            db_session: Database session for queries
            
        Returns:
            Dict: Aggregated performance metrics
        """
        # Get all completed consultations for this student
        completed_consultations = db_session.query(StudentConsultation).filter_by(
            student_id=self.id,
            completed=True
        ).all()
        
        if not completed_consultations:
            return {
                "total_attempts": 0,
                "completed_attempts": 0,
                "average_score": 0,
                "total_duration": 0,
                "consultations_taken": 0
            }
        
        # Calculate metrics
        total_attempts = len(completed_consultations)
        total_score = sum(c.final_score or 0 for c in completed_consultations)
        average_score = total_score / total_attempts if total_attempts > 0 else 0
        total_duration = sum(c.duration_taken or 0 for c in completed_consultations)
        
        # Count unique consultations taken
        unique_consultations = set(c.consultation_id for c in completed_consultations)
        
        return {
            "total_attempts": total_attempts,
            "completed_attempts": total_attempts,
            "average_score": round(average_score, 2),
            "total_duration": total_duration,
            "consultations_taken": len(unique_consultations),
            "consultation_breakdown": [
                {
                    "consultation_id": c.consultation_id,
                    "attempt_number": c.attempt_number,
                    "score": c.final_score,
                    "duration": c.duration_taken,
                    "completed_date": c.completed_date.isoformat() if c.completed_date else None
                }
                for c in completed_consultations
            ]
        }
    
    def view_evaluation(self, student_consultation_id: str, db_session) -> Dict:
        """
        View detailed evaluation for a specific consultation attempt.
        
        Args:
            student_consultation_id: ID of the consultation attempt
            db_session: Database session for queries
            
        Returns:
            Dict: Detailed evaluation information
        """
        # Get the student consultation
        student_consultation = db_session.query(StudentConsultation).filter_by(
            id=student_consultation_id,
            student_id=self.id
        ).first()
        
        if not student_consultation:
            raise ValueError(f"Student consultation {student_consultation_id} not found")
        
        # Get evaluation categories
        evaluation_categories = db_session.query(EvaluationCategory).filter_by(
            student_consultation_id=student_consultation_id
        ).all()
        
        # Calculate total possible score and actual score
        total_possible_score = sum(cat.max_score for cat in evaluation_categories)
        total_actual_score = sum(cat.student_score or 0 for cat in evaluation_categories)
        total_points_deducted = sum(cat.points_deducted for cat in evaluation_categories)
        
        return {
            "consultation_id": student_consultation.consultation_id,
            "attempt_number": student_consultation.attempt_number,
            "final_score": student_consultation.final_score,
            "duration_taken": student_consultation.duration_taken,
            "strengths": student_consultation.strengths,
            "next_steps": student_consultation.next_steps,
            "started_date": student_consultation.started_date.isoformat() if student_consultation.started_date else None,
            "completed_date": student_consultation.completed_date.isoformat() if student_consultation.completed_date else None,
            "submitted_date": student_consultation.submitted_date.isoformat() if student_consultation.submitted_date else None,
            "total_possible_score": total_possible_score,
            "total_actual_score": total_actual_score,
            "total_points_deducted": total_points_deducted,
            "percentage_score": round((total_actual_score / total_possible_score * 100), 2) if total_possible_score > 0 else 0,
            "evaluation_categories": [
                {
                    "category_name": cat.category_name,
                    "max_score": cat.max_score,
                    "student_score": cat.student_score,
                    "points_deducted": cat.points_deducted,
                    "percentage_score": cat.get_percentage_score(),
                    "feedback": cat.feedback
                }
                for cat in evaluation_categories
            ]
        }
    
    def get_consultation_history(self, db_session) -> List[Dict]:
        """
        Get complete consultation history for this student.
        
        Args:
            db_session: Database session for queries
            
        Returns:
            List[Dict]: List of all consultation attempts
        """
        consultations = db_session.query(StudentConsultation).filter_by(
            student_id=self.id
        ).order_by(StudentConsultation.started_date.desc()).all()
        
        return [
            {
                "id": c.id,
                "consultation_id": c.consultation_id,
                "attempt_number": c.attempt_number,
                "in_progress": c.in_progress,
                "completed": c.completed,
                "final_score": c.final_score,
                "duration_taken": c.duration_taken,
                "started_date": c.started_date.isoformat() if c.started_date else None,
                "completed_date": c.completed_date.isoformat() if c.completed_date else None
            }
            for c in consultations
        ]
    
    def __repr__(self):
        return f"<Student(id={self.id}, name={self.name}, username={self.username})>"
