# OSCE Simulator Models

This package contains the SQLAlchemy ORM models for the OSCE Simulator application.

## Architecture Overview

The system uses a simple 4-entity design:

1. **Student** (inherits from User)
2. **Consultation** (standardized test/simulation)
3. **StudentConsultation** (individual attempt record)
4. **EvaluationCategory** (detailed scoring breakdown)

## Models

### User (Abstract Base Class)
- Base class for all users in the system
- Contains common fields: id, name, username, email, password
- Includes timestamps for created_at and updated_at

### Student
- Inherits from User
- Represents medical students using the system
- Has methods for:
  - `start_consultation()`: Begin a new consultation attempt
  - `submit_consultation()`: Submit completed consultation for evaluation
  - `view_metrics()`: View performance analytics
  - `view_evaluation()`: View detailed evaluation results

### Consultation
- Represents standardized OSCE scenarios
- Contains:
  - Basic info: name, duration, difficulty level
  - Configuration flags: flag1, flag2
  - File paths: conversational_flow_file, evaluation_template
- Each consultation has predefined evaluation criteria

### StudentConsultation
- Tracks individual student attempts at consultations
- Records:
  - Attempt metadata: attempt_number, in_progress, completed
  - Performance data: final_score, duration_taken
  - Feedback: strengths, next_steps
  - Timestamps: started_date, completed_date, submitted_date

### EvaluationCategory
- Detailed scoring breakdown for each consultation attempt
- Contains:
  - Category info: category_name, max_score
  - Student performance: student_score, points_deducted
  - Personalized feedback for each category

## Relationships

```
User <|-- Student
Student "1" -- "0..*" StudentConsultation : attempts
Consultation "1" -- "0..*" StudentConsultation : taken_by
StudentConsultation "1" -- "0..*" EvaluationCategory : evaluated_in
```

## Usage

### Database Setup
```python
from app.models import create_tables, get_db

# Create tables
create_tables()

# Get database session
db = next(get_db())
```

### Seeding Sample Data
```python
from app.models.seed_data import seed_sample_data

# Seed with sample data for testing
sample_data = seed_sample_data(db)
```

### Basic CRUD Operations
```python
from app.models import Student, Consultation, StudentConsultation

# Create a new student
student = Student(
    id=str(uuid.uuid4()),
    name="Jane Smith",
    username="janesmith",
    email="jane.smith@university.edu",
    password="hashed_password"
)
db.add(student)
db.commit()

# Query consultations
consultations = db.query(Consultation).filter_by(difficulty="beginner").all()

# Get student's consultation history
student_consultations = db.query(StudentConsultation).filter_by(student_id=student.id).all()
```

## Database Configuration

The database configuration is handled in `database.py`:
- Default: SQLite database (`osce_simulator.db`)
- Configurable via `DATABASE_URL` environment variable
- Supports PostgreSQL, MySQL, etc.

## Migration Strategy

For production deployments, consider using Alembic for database migrations:
1. Install Alembic: `pip install alembic`
2. Initialize: `alembic init alembic`
3. Create migrations: `alembic revision --autogenerate -m "Initial migration"`
4. Apply migrations: `alembic upgrade head`
