from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.orm import relationship
from .database import Base

class Consultation(Base):
    """
    Consultation model representing standardized test/simulation scenarios.
    """
    __tablename__ = "consultations"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    duration = Column(Integer, nullable=False)  # Duration in minutes
    difficulty = Column(String, nullable=False)  # e.g., "beginner", "intermediate", "advanced"
    flag1 = Column(Boolean, default=False)
    flag2 = Column(Boolean, default=False)
    conversational_flow_file = Column(String, nullable=False)  # Path to flow file
    evaluation_template = Column(String, nullable=False)  # Path to evaluation template
    
    # Relationships
    student_consultations = relationship("StudentConsultation", back_populates="consultation")
    
    def __repr__(self):
        return f"<Consultation(id={self.id}, name={self.name}, difficulty={self.difficulty})>"
