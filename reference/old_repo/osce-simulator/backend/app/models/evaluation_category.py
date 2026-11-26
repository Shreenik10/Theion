from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class EvaluationCategory(Base):
    """
    EvaluationCategory model for detailed scoring breakdown of student consultations.
    """
    __tablename__ = "evaluation_categories"
    
    id = Column(String, primary_key=True, index=True)
    student_consultation_id = Column(String, ForeignKey("student_consultations.id"), nullable=False)
    category_name = Column(String, nullable=False)  # e.g., "Communication", "Clinical Reasoning", "Patient Care"
    max_score = Column(Integer, nullable=False)  # Maximum possible score for this category
    student_score = Column(Integer, nullable=True)  # Actual score achieved by student
    feedback = Column(String, nullable=True)  # Detailed feedback for this category
    points_deducted = Column(Integer, default=0)  # Points deducted from max_score
    
    # Relationships
    student_consultation = relationship("StudentConsultation", back_populates="evaluation_categories")
    
    def get_percentage_score(self) -> float:
        """
        Calculate the percentage score for this category.
        """
        if self.max_score == 0:
            return 0.0
        return (self.student_score / self.max_score) * 100 if self.student_score is not None else 0.0
    
    def __repr__(self):
        return f"<EvaluationCategory(id={self.id}, category_name={self.category_name}, student_score={self.student_score}/{self.max_score})>"
