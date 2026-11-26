import pytest
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from app.models import Base


@pytest.fixture(scope="session")
def test_engine():
    """Create a test database engine for the entire test session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture(scope="session")
def TestSessionLocal(test_engine):
    """Create a test session factory for the entire test session."""
    return sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture
def db_session(TestSessionLocal):
    """Create a fresh database session for each test."""
    session = TestSessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def clean_db(db_session):
    """Ensure database is clean before each test."""
    # Clear all tables
    for table in reversed(Base.metadata.sorted_tables):
        db_session.execute(table.delete())
    db_session.commit()
    return db_session


@pytest.fixture(autouse=True)
def clean_database_before_test(db_session):
    """Automatically clean database before each test."""
    # Clear all tables before each test
    for table in reversed(Base.metadata.sorted_tables):
        db_session.execute(table.delete())
    db_session.commit()
    yield
    # Clean up after test
    try:
        for table in reversed(Base.metadata.sorted_tables):
            db_session.execute(table.delete())
        db_session.commit()
    except Exception:
        # If there's an error (like rollback), just rollback and continue
        db_session.rollback()
