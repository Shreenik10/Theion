import pytest
import uuid
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import (
    Base, Student, Consultation, StudentConsultation, 
    EvaluationCategory, create_tables, get_db
)
from app.models.seed_data import seed_sample_data


class TestStudentModel:
    """Test suite for the Student model and its methods."""
    
    @pytest.fixture(scope="class")
    def engine(self):
        """Create test database engine."""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=engine)
        return engine
    
    @pytest.fixture(scope="class")
    def SessionLocal(self, engine):
        """Create test database session factory."""
        return sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    @pytest.fixture
    def db_session(self, SessionLocal):
        """Create a fresh database session for each test."""
        session = SessionLocal()
        yield session
        session.close()
    
    @pytest.fixture
    def sample_data(self, db_session):
        """Seed database with sample data."""
        return seed_sample_data(db_session)
    
    @pytest.fixture
    def student(self, db_session, sample_data):
        """Get the sample student from seeded data."""
        return db_session.query(Student).filter_by(id=sample_data["student_id"]).first()
    
    @pytest.fixture
    def consultation(self, db_session, sample_data):
        """Get a sample consultation from seeded data."""
        return db_session.query(Consultation).filter_by(id=sample_data["consultation_ids"][0]).first()
    
    @pytest.fixture
    def new_student(self, db_session):
        """Create a new student for testing."""
        student = Student(
            id=str(uuid.uuid4()),
            name="Test Student",
            username=f"teststudent_{uuid.uuid4().hex[:8]}",
            email=f"test.student_{uuid.uuid4().hex[:8]}@university.edu",
            password="hashed_password"
        )
        db_session.add(student)
        db_session.commit()
        return student
    
    def test_student_creation(self, db_session):
        """Test creating a new student."""
        student = Student(
            id=str(uuid.uuid4()),
            name="Jane Doe",
            username="janedoe",
            email="jane.doe@university.edu",
            password="hashed_password"
        )
        
        db_session.add(student)
        db_session.commit()
        
        # Verify student was created
        retrieved_student = db_session.query(Student).filter_by(id=student.id).first()
        assert retrieved_student is not None
        assert retrieved_student.name == "Jane Doe"
        assert retrieved_student.username == "janedoe"
        assert retrieved_student.email == "jane.doe@university.edu"
        assert retrieved_student.password == "hashed_password"
    
    def test_student_inheritance(self, new_student):
        """Test that Student inherits from User properly."""
        assert isinstance(new_student, Student)
        assert hasattr(new_student, 'name')
        assert hasattr(new_student, 'username')
        assert hasattr(new_student, 'email')
        assert hasattr(new_student, 'password')
        assert hasattr(new_student, 'created_at')
        assert hasattr(new_student, 'updated_at')
    
    def test_student_relationships(self, student, db_session):
        """Test student relationships with other models."""
        # Test relationship with StudentConsultation
        assert hasattr(student, 'consultations')
        assert isinstance(student.consultations, list)
        
        # Verify the relationship works
        student_consultations = db_session.query(StudentConsultation).filter_by(student_id=student.id).all()
        assert len(student.consultations) == len(student_consultations)
    
    def test_start_consultation_success(self, new_student, consultation, db_session):
        """Test successfully starting a consultation."""
        # Start consultation
        student_consultation = new_student.start_consultation(consultation.id, db_session)
        
        # Verify consultation was created
        assert student_consultation is not None
        assert student_consultation.student_id == new_student.id
        assert student_consultation.consultation_id == consultation.id
        assert student_consultation.attempt_number == 1
        assert student_consultation.in_progress is True
        assert student_consultation.completed is False
        assert student_consultation.started_date is not None
        
        # Verify it's in the database
        db_consultation = db_session.query(StudentConsultation).filter_by(id=student_consultation.id).first()
        assert db_consultation is not None
        assert db_consultation.in_progress is True
    
    def test_start_consultation_multiple_attempts(self, new_student, consultation, db_session):
        """Test starting multiple attempts of the same consultation."""
        # Start first consultation
        consultation1 = new_student.start_consultation(consultation.id, db_session)
        assert consultation1.attempt_number == 1
        
        # Start second consultation
        consultation2 = new_student.start_consultation(consultation.id, db_session)
        assert consultation2.attempt_number == 2
        
        # Start third consultation
        consultation3 = new_student.start_consultation(consultation.id, db_session)
        assert consultation3.attempt_number == 3
        
        # Verify all are in database
        all_consultations = db_session.query(StudentConsultation).filter_by(
            student_id=new_student.id,
            consultation_id=consultation.id
        ).all()
        assert len(all_consultations) == 3
    
    def test_submit_consultation_success(self, new_student, consultation, db_session):
        """Test successfully submitting a consultation."""
        # Start consultation
        student_consultation = new_student.start_consultation(consultation.id, db_session)
        
        # Submit consultation
        result = new_student.submit_consultation(student_consultation.id, db_session)
        
        # Verify submission was successful
        assert result is True
        
        # Verify consultation was updated
        db_consultation = db_session.query(StudentConsultation).filter_by(id=student_consultation.id).first()
        assert db_consultation.in_progress is False
        assert db_consultation.completed is True
        assert db_consultation.submitted_date is not None
        assert db_consultation.completed_date is not None
    
    def test_submit_consultation_not_found(self, new_student, db_session):
        """Test submitting a consultation that doesn't exist."""
        with pytest.raises(ValueError, match="Student consultation .* not found"):
            new_student.submit_consultation("non-existent-id", db_session)
    
    def test_submit_consultation_not_in_progress(self, new_student, consultation, db_session):
        """Test submitting a consultation that's not in progress."""
        # Start and submit consultation
        student_consultation = new_student.start_consultation(consultation.id, db_session)
        new_student.submit_consultation(student_consultation.id, db_session)
        
        # Try to submit again
        with pytest.raises(ValueError, match="Consultation is not in progress"):
            new_student.submit_consultation(student_consultation.id, db_session)
    
    def test_submit_consultation_wrong_student(self, new_student, consultation, db_session):
        """Test submitting a consultation that belongs to another student."""
        # Create another student
        other_student = Student(
            id=str(uuid.uuid4()),
            name="Other Student",
            username="otherstudent",
            email="other.student@university.edu",
            password="hashed_password"
        )
        db_session.add(other_student)
        db_session.commit()
        
        # Start consultation with first student
        student_consultation = new_student.start_consultation(consultation.id, db_session)
        
        # Try to submit with other student
        with pytest.raises(ValueError, match="Student consultation .* not found"):
            other_student.submit_consultation(student_consultation.id, db_session)
    
    def test_view_metrics_no_consultations(self, new_student, db_session):
        """Test viewing metrics when student has no consultations."""
        metrics = new_student.view_metrics(db_session)
        
        expected = {
            "total_attempts": 0,
            "completed_attempts": 0,
            "average_score": 0,
            "total_duration": 0,
            "consultations_taken": 0
        }
        
        assert metrics == expected
    
    def test_view_metrics_with_consultations(self, student, db_session):
        """Test viewing metrics when student has completed consultations."""
        metrics = student.view_metrics(db_session)
        
        # Verify basic structure
        assert "total_attempts" in metrics
        assert "completed_attempts" in metrics
        assert "average_score" in metrics
        assert "total_duration" in metrics
        assert "consultations_taken" in metrics
        assert "consultation_breakdown" in metrics
        
        # Verify values are reasonable
        assert metrics["total_attempts"] >= 0
        assert metrics["completed_attempts"] >= 0
        assert 0 <= metrics["average_score"] <= 100
        assert metrics["total_duration"] >= 0
        assert metrics["consultations_taken"] >= 0
        
        # Verify breakdown structure
        if metrics["consultation_breakdown"]:
            breakdown = metrics["consultation_breakdown"][0]
            assert "consultation_id" in breakdown
            assert "attempt_number" in breakdown
            assert "score" in breakdown
            assert "duration" in breakdown
            assert "completed_date" in breakdown
    
    def test_view_evaluation_success(self, student, db_session, sample_data):
        """Test viewing evaluation for a specific consultation."""
        evaluation = student.view_evaluation(sample_data["student_consultation_id"], db_session)
        
        # Verify basic structure
        assert "consultation_id" in evaluation
        assert "attempt_number" in evaluation
        assert "final_score" in evaluation
        assert "duration_taken" in evaluation
        assert "strengths" in evaluation
        assert "next_steps" in evaluation
        assert "started_date" in evaluation
        assert "completed_date" in evaluation
        assert "submitted_date" in evaluation
        assert "total_possible_score" in evaluation
        assert "total_actual_score" in evaluation
        assert "total_points_deducted" in evaluation
        assert "percentage_score" in evaluation
        assert "evaluation_categories" in evaluation
        
        # Verify values
        assert evaluation["attempt_number"] == 1
        assert evaluation["final_score"] == 85
        assert evaluation["duration_taken"] == 28
        assert evaluation["strengths"] == "Good communication skills, thorough history taking"
        assert evaluation["next_steps"] == "Practice auscultation techniques, improve differential diagnosis"
        
        # Verify evaluation categories
        assert len(evaluation["evaluation_categories"]) == 4
        
        # Check each category
        categories = evaluation["evaluation_categories"]
        category_names = [cat["category_name"] for cat in categories]
        assert "Communication" in category_names
        assert "Clinical Reasoning" in category_names
        assert "Patient Care" in category_names
        assert "Technical Skills" in category_names
    
    def test_view_evaluation_not_found(self, new_student, db_session):
        """Test viewing evaluation for non-existent consultation."""
        with pytest.raises(ValueError, match="Student consultation .* not found"):
            new_student.view_evaluation("non-existent-id", db_session)
    
    def test_view_evaluation_wrong_student(self, new_student, db_session, sample_data):
        """Test viewing evaluation for consultation belonging to another student."""
        with pytest.raises(ValueError, match="Student consultation .* not found"):
            new_student.view_evaluation(sample_data["student_consultation_id"], db_session)
    
    def test_get_consultation_history(self, student, db_session):
        """Test getting consultation history."""
        history = student.get_consultation_history(db_session)
        
        # Verify it's a list
        assert isinstance(history, list)
        
        # Verify structure of each item
        if history:
            item = history[0]
            assert "id" in item
            assert "consultation_id" in item
            assert "attempt_number" in item
            assert "in_progress" in item
            assert "completed" in item
            assert "final_score" in item
            assert "duration_taken" in item
            assert "started_date" in item
            assert "completed_date" in item
    
    def test_get_consultation_history_empty(self, new_student, db_session):
        """Test getting consultation history for student with no consultations."""
        history = new_student.get_consultation_history(db_session)
        assert history == []
    
    def test_student_repr(self, new_student):
        """Test the string representation of a student."""
        repr_str = repr(new_student)
        assert "Student" in repr_str
        assert new_student.id in repr_str
        assert new_student.name in repr_str
        assert new_student.username in repr_str
    
    def test_student_with_multiple_consultations(self, new_student, db_session):
        """Test student with multiple different consultations."""
        # Create multiple consultations
        consultation1 = Consultation(
            id=str(uuid.uuid4()),
            name="Consultation 1",
            duration=30,
            difficulty="beginner",
            conversational_flow_file="/flows/consultation1.json",
            evaluation_template="/templates/consultation1.json"
        )
        
        consultation2 = Consultation(
            id=str(uuid.uuid4()),
            name="Consultation 2",
            duration=45,
            difficulty="intermediate",
            conversational_flow_file="/flows/consultation2.json",
            evaluation_template="/templates/consultation2.json"
        )
        
        db_session.add(consultation1)
        db_session.add(consultation2)
        db_session.commit()
        
        # Start consultations
        sc1 = new_student.start_consultation(consultation1.id, db_session)
        sc2 = new_student.start_consultation(consultation2.id, db_session)
        
        # Submit consultations
        new_student.submit_consultation(sc1.id, db_session)
        new_student.submit_consultation(sc2.id, db_session)
        
        # Check metrics
        metrics = new_student.view_metrics(db_session)
        assert metrics["total_attempts"] == 2
        assert metrics["consultations_taken"] == 2
        
        # Check history
        history = new_student.get_consultation_history(db_session)
        assert len(history) == 2


class TestStudentModelIntegration:
    """Integration tests for Student model with other components."""
    
    @pytest.fixture(scope="class")
    def engine(self):
        """Create test database engine."""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=engine)
        return engine
    
    @pytest.fixture(scope="class")
    def SessionLocal(self, engine):
        """Create test database session factory."""
        return sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    @pytest.fixture
    def db_session(self, SessionLocal):
        """Create a fresh database session for each test."""
        session = SessionLocal()
        yield session
        session.close()
    
    def test_full_consultation_workflow(self, db_session):
        """Test the complete consultation workflow."""
        # Create student
        student = Student(
            id=str(uuid.uuid4()),
            name="Workflow Test Student",
            username="workflowtest",
            email="workflow.test@university.edu",
            password="hashed_password"
        )
        db_session.add(student)
        
        # Create consultation
        consultation = Consultation(
            id=str(uuid.uuid4()),
            name="Workflow Test Consultation",
            duration=30,
            difficulty="beginner",
            conversational_flow_file="/flows/workflow_test.json",
            evaluation_template="/templates/workflow_test.json"
        )
        db_session.add(consultation)
        db_session.commit()
        
        # 1. Start consultation
        student_consultation = student.start_consultation(consultation.id, db_session)
        assert student_consultation.in_progress is True
        assert student_consultation.completed is False
        
        # 2. Submit consultation
        result = student.submit_consultation(student_consultation.id, db_session)
        assert result is True
        
        # 3. Verify submission
        db_consultation = db_session.query(StudentConsultation).filter_by(id=student_consultation.id).first()
        assert db_consultation.in_progress is False
        assert db_consultation.completed is True
        
        # 4. Check metrics
        metrics = student.view_metrics(db_session)
        assert metrics["total_attempts"] == 1
        assert metrics["consultations_taken"] == 1
        
        # 5. Check history
        history = student.get_consultation_history(db_session)
        assert len(history) == 1
        assert history[0]["consultation_id"] == consultation.id
    
    def test_evaluation_categories_integration(self, db_session):
        """Test integration with evaluation categories."""
        # Create student and consultation
        student = Student(
            id=str(uuid.uuid4()),
            name="Evaluation Test Student",
            username="evaltest",
            email="eval.test@university.edu",
            password="hashed_password"
        )
        db_session.add(student)
        
        consultation = Consultation(
            id=str(uuid.uuid4()),
            name="Evaluation Test Consultation",
            duration=30,
            difficulty="beginner",
            conversational_flow_file="/flows/eval_test.json",
            evaluation_template="/templates/eval_test.json"
        )
        db_session.add(consultation)
        db_session.commit()
        
        # Start and submit consultation
        student_consultation = student.start_consultation(consultation.id, db_session)
        student.submit_consultation(student_consultation.id, db_session)
        
        # Add evaluation categories
        categories = [
            EvaluationCategory(
                id=str(uuid.uuid4()),
                student_consultation_id=student_consultation.id,
                category_name="Test Category 1",
                max_score=25,
                student_score=20,
                feedback="Good performance",
                points_deducted=5
            ),
            EvaluationCategory(
                id=str(uuid.uuid4()),
                student_consultation_id=student_consultation.id,
                category_name="Test Category 2",
                max_score=25,
                student_score=22,
                feedback="Excellent performance",
                points_deducted=3
            )
        ]
        
        for category in categories:
            db_session.add(category)
        db_session.commit()
        
        # Test evaluation view
        evaluation = student.view_evaluation(student_consultation.id, db_session)
        assert len(evaluation["evaluation_categories"]) == 2
        assert evaluation["total_possible_score"] == 50
        assert evaluation["total_actual_score"] == 42
        assert evaluation["percentage_score"] == 84.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
