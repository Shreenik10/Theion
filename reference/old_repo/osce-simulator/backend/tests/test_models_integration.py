import pytest
import uuid
from datetime import datetime
from app.models import (
    Student, Consultation, StudentConsultation, 
    EvaluationCategory, User
)
from app.models.seed_data import seed_sample_data


class TestModelsIntegration:
    """Integration tests for all models working together."""
    
    def test_complete_workflow_with_evaluation(self, clean_db):
        """Test the complete workflow from student creation to evaluation."""
        db_session = clean_db
        
        # 1. Create a student
        student = Student(
            id=str(uuid.uuid4()),
            name="Integration Test Student",
            username=f"integrationtest_{uuid.uuid4().hex[:8]}",
            email=f"integration.test_{uuid.uuid4().hex[:8]}@university.edu",
            password="hashed_password"
        )
        db_session.add(student)
        
        # 2. Create a consultation
        consultation = Consultation(
            id=str(uuid.uuid4()),
            name="Integration Test Consultation",
            duration=45,
            difficulty="intermediate",
            flag1=True,
            flag2=False,
            conversational_flow_file="/flows/integration_test.json",
            evaluation_template="/templates/integration_test.json"
        )
        db_session.add(consultation)
        db_session.commit()
        
        # 3. Start consultation
        student_consultation = student.start_consultation(consultation.id, db_session)
        assert student_consultation.in_progress is True
        assert student_consultation.attempt_number == 1
        
        # 4. Create evaluation categories
        categories = [
            EvaluationCategory(
                id=str(uuid.uuid4()),
                student_consultation_id=student_consultation.id,
                category_name="Communication Skills",
                max_score=30,
                student_score=25,
                feedback="Good rapport building, clear communication",
                points_deducted=5
            ),
            EvaluationCategory(
                id=str(uuid.uuid4()),
                student_consultation_id=student_consultation.id,
                category_name="Clinical Reasoning",
                max_score=40,
                student_score=32,
                feedback="Solid differential diagnosis, good problem-solving",
                points_deducted=8
            ),
            EvaluationCategory(
                id=str(uuid.uuid4()),
                student_consultation_id=student_consultation.id,
                category_name="Patient Care",
                max_score=30,
                student_score=28,
                feedback="Comprehensive assessment, appropriate care plan",
                points_deducted=2
            )
        ]
        
        for category in categories:
            db_session.add(category)
        
        # 5. Update student consultation with final score
        total_score = sum(cat.student_score for cat in categories)
        student_consultation.final_score = total_score
        student_consultation.duration_taken = 42
        student_consultation.strengths = "Excellent communication and patient care"
        student_consultation.next_steps = "Continue practicing clinical reasoning"
        
        db_session.commit()
        
        # 6. Submit consultation
        result = student.submit_consultation(student_consultation.id, db_session)
        assert result is True
        
        # 7. Verify all relationships work
        # Student -> StudentConsultation
        assert len(student.consultations) == 1
        assert student.consultations[0].id == student_consultation.id
        
        # StudentConsultation -> EvaluationCategory
        assert len(student_consultation.evaluation_categories) == 3
        
        # StudentConsultation -> Consultation
        assert student_consultation.consultation.id == consultation.id
        
        # 8. Test metrics
        metrics = student.view_metrics(db_session)
        assert metrics["total_attempts"] == 1
        assert metrics["average_score"] == 85  # (25+32+28) = 85
        assert metrics["total_duration"] == 42
        assert metrics["consultations_taken"] == 1
        
        # 9. Test evaluation view
        evaluation = student.view_evaluation(student_consultation.id, db_session)
        assert evaluation["final_score"] == 85
        assert evaluation["duration_taken"] == 42
        assert evaluation["total_possible_score"] == 100
        assert evaluation["total_actual_score"] == 85
        assert evaluation["percentage_score"] == 85.0
        assert len(evaluation["evaluation_categories"]) == 3
        
        # 10. Test consultation history
        history = student.get_consultation_history(db_session)
        assert len(history) == 1
        assert history[0]["consultation_id"] == consultation.id
        assert history[0]["final_score"] == 85
    
    def test_multiple_consultations_same_student(self, clean_db):
        """Test a student taking multiple different consultations."""
        db_session = clean_db
        
        # Create student
        student = Student(
            id=str(uuid.uuid4()),
            name="Multi-Consultation Student",
            username=f"multiconsult_{uuid.uuid4().hex[:8]}",
            email=f"multi.consult_{uuid.uuid4().hex[:8]}@university.edu",
            password="hashed_password"
        )
        db_session.add(student)
        
        # Create multiple consultations
        consultations = []
        for i in range(3):
            consultation = Consultation(
                id=str(uuid.uuid4()),
                name=f"Consultation {i+1}",
                duration=30 + (i * 10),
                difficulty=["beginner", "intermediate", "advanced"][i],
                conversational_flow_file=f"/flows/consultation_{i+1}.json",
                evaluation_template=f"/templates/consultation_{i+1}.json"
            )
            consultations.append(consultation)
            db_session.add(consultation)
        
        db_session.commit()
        
        # Start and complete each consultation
        for i, consultation in enumerate(consultations):
            # Start consultation
            student_consultation = student.start_consultation(consultation.id, db_session)
            
            # Add evaluation categories
            category = EvaluationCategory(
                id=str(uuid.uuid4()),
                student_consultation_id=student_consultation.id,
                category_name="Overall Performance",
                max_score=100,
                student_score=80 + (i * 5),  # Different scores for each
                feedback=f"Good performance on consultation {i+1}",
                points_deducted=20 - (i * 5)
            )
            db_session.add(category)
            
            # Update consultation
            student_consultation.final_score = 80 + (i * 5)
            student_consultation.duration_taken = 25 + (i * 5)
            student_consultation.strengths = f"Strengths for consultation {i+1}"
            student_consultation.next_steps = f"Next steps for consultation {i+1}"
            
            # Submit
            student.submit_consultation(student_consultation.id, db_session)
        
        # Test metrics
        metrics = student.view_metrics(db_session)
        assert metrics["total_attempts"] == 3
        assert metrics["consultations_taken"] == 3
        assert metrics["average_score"] == 85  # (80 + 85 + 90) / 3
        assert metrics["total_duration"] == 90  # (25 + 30 + 35)
        
        # Test history
        history = student.get_consultation_history(db_session)
        assert len(history) == 3
        
        # Verify attempt numbers are correct
        attempt_numbers = [h["attempt_number"] for h in history]
        assert attempt_numbers == [1, 1, 1]  # Each consultation attempted once
    
    def test_multiple_attempts_same_consultation(self, clean_db):
        """Test a student taking the same consultation multiple times."""
        db_session = clean_db
        
        # Create student and consultation
        student = Student(
            id=str(uuid.uuid4()),
            name="Multiple Attempts Student",
            username=f"multattempts_{uuid.uuid4().hex[:8]}",
            email=f"multi.attempts_{uuid.uuid4().hex[:8]}@university.edu",
            password="hashed_password"
        )
        db_session.add(student)
        
        consultation = Consultation(
            id=str(uuid.uuid4()),
            name="Practice Consultation",
            duration=30,
            difficulty="intermediate",
            conversational_flow_file="/flows/practice.json",
            evaluation_template="/templates/practice.json"
        )
        db_session.add(consultation)
        db_session.commit()
        
        # Take the consultation 3 times
        attempts = []
        for attempt_num in range(1, 4):
            # Start consultation
            student_consultation = student.start_consultation(consultation.id, db_session)
            assert student_consultation.attempt_number == attempt_num
            
            # Add evaluation
            category = EvaluationCategory(
                id=str(uuid.uuid4()),
                student_consultation_id=student_consultation.id,
                category_name="Performance",
                max_score=100,
                student_score=70 + (attempt_num * 10),  # Improving scores
                feedback=f"Attempt {attempt_num} - showing improvement",
                points_deducted=30 - (attempt_num * 5)
            )
            db_session.add(category)
            
            # Update and submit
            student_consultation.final_score = 70 + (attempt_num * 10)
            student_consultation.duration_taken = 35 - (attempt_num * 2)
            student_consultation.strengths = f"Improving with each attempt"
            student_consultation.next_steps = f"Continue practicing"
            
            student.submit_consultation(student_consultation.id, db_session)
            attempts.append(student_consultation)
        
        # Test metrics
        metrics = student.view_metrics(db_session)
        assert metrics["total_attempts"] == 3
        assert metrics["consultations_taken"] == 1  # Only one unique consultation
        assert metrics["average_score"] == 90  # (80 + 90 + 100) / 3
        
        # Test history
        history = student.get_consultation_history(db_session)
        assert len(history) == 3
        
        # Verify attempt numbers
        attempt_numbers = [h["attempt_number"] for h in history]
        assert attempt_numbers == [3, 2, 1]  # Most recent first
    
    def test_user_inheritance_relationships(self, clean_db):
        """Test that User inheritance and relationships work correctly."""
        db_session = clean_db
        
        # Create a user (base class)
        user = User(
            id=str(uuid.uuid4()),
            name="Base User",
            username=f"baseuser_{uuid.uuid4().hex[:8]}",
            email=f"base.user_{uuid.uuid4().hex[:8]}@university.edu",
            password="hashed_password"
        )
        db_session.add(user)
        
        # Create a student (inherits from User)
        student = Student(
            id=str(uuid.uuid4()),
            name="Inheritance Test Student",
            username=f"inheritancetest_{uuid.uuid4().hex[:8]}",
            email=f"inheritance.test_{uuid.uuid4().hex[:8]}@university.edu",
            password="hashed_password"
        )
        db_session.add(student)
        db_session.commit()
        
        # Verify both are in the database
        users = db_session.query(User).all()
        students = db_session.query(Student).all()
        
        assert len(users) == 2  # Both user and student
        assert len(students) == 1  # Only the student
        
        # Verify student has all user attributes
        assert hasattr(student, 'name')
        assert hasattr(student, 'username')
        assert hasattr(student, 'email')
        assert hasattr(student, 'password')
        assert hasattr(student, 'created_at')
        assert hasattr(student, 'updated_at')
        
        # Verify student has student-specific attributes
        assert hasattr(student, 'consultations')
    
    def test_database_constraints_and_validation(self, clean_db):
        """Test database constraints and validation."""
        db_session = clean_db
        
        # Test unique username constraint
        duplicate_username = f"duplicate_username_{uuid.uuid4().hex[:8]}"
        student1 = Student(
            id=str(uuid.uuid4()),
            name="Student 1",
            username=duplicate_username,
            email=f"student1_{uuid.uuid4().hex[:8]}@university.edu",
            password="hashed_password"
        )
        db_session.add(student1)
        db_session.commit()
        
        # Try to create another student with same username
        student2 = Student(
            id=str(uuid.uuid4()),
            name="Student 2",
            username=duplicate_username,  # Same username
            email=f"student2_{uuid.uuid4().hex[:8]}@university.edu",
            password="hashed_password"
        )
        db_session.add(student2)
        
        # This should raise an integrity error
        with pytest.raises(Exception):  # SQLAlchemy will raise an integrity error
            db_session.commit()
        
        db_session.rollback()
        
        # Test unique email constraint
        duplicate_email = f"student1_{uuid.uuid4().hex[:8]}@university.edu"
        student2.email = duplicate_email  # Same email as student1
        db_session.add(student2)
        
        with pytest.raises(Exception):
            db_session.commit()
    
    def test_seed_data_integration(self, clean_db):
        """Test that seed data works correctly with all models."""
        db_session = clean_db
        
        # Seed the database
        sample_data = seed_sample_data(db_session)
        
        # Verify all models were created
        students = db_session.query(Student).all()
        consultations = db_session.query(Consultation).all()
        student_consultations = db_session.query(StudentConsultation).all()
        evaluation_categories = db_session.query(EvaluationCategory).all()
        
        assert len(students) == 1
        assert len(consultations) == 2
        assert len(student_consultations) == 1
        assert len(evaluation_categories) == 4
        
        # Test relationships work
        student = students[0]
        assert len(student.consultations) == 1
        
        student_consultation = student_consultations[0]
        assert len(student_consultation.evaluation_categories) == 4
        
        # Test that the student can use all methods
        metrics = student.view_metrics(db_session)
        assert metrics["total_attempts"] == 1
        assert metrics["average_score"] == 85
        
        evaluation = student.view_evaluation(student_consultation.id, db_session)
        assert evaluation["final_score"] == 85
        assert len(evaluation["evaluation_categories"]) == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
