import uuid
from sqlalchemy.orm import Session
from .student import Student
from .consultation import Consultation
from .student_consultation import StudentConsultation
from .evaluation_category import EvaluationCategory

def seed_sample_data(db: Session):
    """
    Seed the database with sample data for testing and development.
    """
    
    # Create sample consultations
    consultation1 = Consultation(
        id=str(uuid.uuid4()),
        name="Cardiovascular Assessment",
        duration=30,
        difficulty="intermediate",
        flag1=False,
        flag2=True,
        conversational_flow_file="/flows/cardiovascular_assessment.json",
        evaluation_template="/templates/cardiovascular_evaluation.json"
    )
    
    consultation2 = Consultation(
        id=str(uuid.uuid4()),
        name="Respiratory Examination",
        duration=25,
        difficulty="beginner",
        flag1=True,
        flag2=False,
        conversational_flow_file="/flows/respiratory_examination.json",
        evaluation_template="/templates/respiratory_evaluation.json"
    )
    
    # Create sample student
    student = Student(
        id=str(uuid.uuid4()),
        name="John Doe",
        username="johndoe",
        email="john.doe@university.edu",
        password="hashed_password_here"  # In real app, this would be properly hashed
    )
    
    # Add to database
    db.add(consultation1)
    db.add(consultation2)
    db.add(student)
    db.commit()
    
    # Create sample student consultation
    student_consultation = StudentConsultation(
        id=str(uuid.uuid4()),
        student_id=student.id,
        consultation_id=consultation1.id,
        attempt_number=1,
        in_progress=False,
        completed=True,
        final_score=85,
        duration_taken=28,
        strengths="Good communication skills, thorough history taking",
        next_steps="Practice auscultation techniques, improve differential diagnosis"
    )
    
    db.add(student_consultation)
    db.commit()
    
    # Create sample evaluation categories
    categories = [
        EvaluationCategory(
            id=str(uuid.uuid4()),
            student_consultation_id=student_consultation.id,
            category_name="Communication",
            max_score=25,
            student_score=22,
            feedback="Excellent rapport building and clear communication with patient",
            points_deducted=3
        ),
        EvaluationCategory(
            id=str(uuid.uuid4()),
            student_consultation_id=student_consultation.id,
            category_name="Clinical Reasoning",
            max_score=30,
            student_score=25,
            feedback="Good differential diagnosis but missed some key findings",
            points_deducted=5
        ),
        EvaluationCategory(
            id=str(uuid.uuid4()),
            student_consultation_id=student_consultation.id,
            category_name="Patient Care",
            max_score=25,
            student_score=23,
            feedback="Comprehensive assessment and appropriate care plan",
            points_deducted=2
        ),
        EvaluationCategory(
            id=str(uuid.uuid4()),
            student_consultation_id=student_consultation.id,
            category_name="Technical Skills",
            max_score=20,
            student_score=15,
            feedback="Basic examination skills demonstrated, needs practice with auscultation",
            points_deducted=5
        )
    ]
    
    for category in categories:
        db.add(category)
    
    db.commit()
    
    print("Sample data seeded successfully!")
    return {
        "student_id": student.id,
        "consultation_ids": [consultation1.id, consultation2.id],
        "student_consultation_id": student_consultation.id
    }
