from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class StudentConsultation(Base):
    """
    StudentConsultation model tracking individual student attempts at consultations.
    """
    __tablename__ = "student_consultations"
    
    id = Column(String, primary_key=True, index=True)
    student_id = Column(String, ForeignKey("students.id"), nullable=False)
    consultation_id = Column(String, ForeignKey("consultations.id"), nullable=False)
    attempt_number = Column(Integer, nullable=False, default=1)
    in_progress = Column(Boolean, default=True)
    completed = Column(Boolean, default=False)
    final_score = Column(Integer, nullable=True)  # Score out of 100
    duration_taken = Column(Integer, nullable=True)  # Duration taken in minutes
    strengths = Column(String, nullable=True)  # JSON string or text
    next_steps = Column(String, nullable=True)  # JSON string or text
    started_date = Column(DateTime(timezone=True), server_default=func.now())
    completed_date = Column(DateTime(timezone=True), nullable=True)
    submitted_date = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    student = relationship("Student", back_populates="consultations")
    consultation = relationship("Consultation", back_populates="student_consultations")
    evaluation_categories = relationship("EvaluationCategory", back_populates="student_consultation")
    
    def __repr__(self):
        return f"<StudentConsultation(id={self.id}, student_id={self.student_id}, consultation_id={self.consultation_id}, attempt_number={self.attempt_number})>"
