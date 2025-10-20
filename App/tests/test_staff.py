import pytest
from App.main import create_app
from App.database import db
from App.models import Student, Staff
from App.controllers import (
    create_staff,
    create_student,
    log_hours_for_student,
    confirm_student_hours,
    get_pending_confirmations,
    request_hours_confirmation
)


@pytest.fixture(autouse=True, scope="module")
def empty_db():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


class TestStaffUnit:
    
    def test_new_staff(self):
        """Test creating a new staff member"""
        staff = Staff(username="staffuser", password="staffpass", name="Staff User")
        assert staff.username == "staffuser"
        assert staff.name == "Staff User"
        assert staff.user_type == "staff"


class TestStaffIntegration:
    
    def test_create_staff_controller(self):
        """Test creating staff via controller"""
        app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
        with app.app_context():
            staff = create_staff("teacher1", "pass123", "Mr. Smith")
            assert staff.username == "teacher1"
            assert staff.name == "Mr. Smith"
            db.session.rollback()
    
    def test_log_hours_for_student(self):
        """Test staff logging hours for student"""
        app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
        with app.app_context():
            staff = create_staff("teacher2", "pass", "Ms. Johnson")
            student = create_student("student1", "pass", "Student One")
            db.session.flush()
            
            result, error = log_hours_for_student(staff.id, student.id, 20)
            assert error is None
            assert result.total_hours == 20
            
            db.session.rollback()
    
    def test_log_hours_invalid_student(self):
        """Test staff logging hours for non-existent student"""
        app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
        with app.app_context():
            staff = create_staff("teacher3", "pass", "Mr. Davis")
            db.session.flush()
            
            result, error = log_hours_for_student(staff.id, 99999, 20)
            assert error == "Student not found"
            assert result is None
            
            db.session.rollback()
    
    def test_confirm_student_hours(self):
        """Test staff confirming student hours"""
        app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
        with app.app_context():
            staff = create_staff("teacher4", "pass", "Mrs. Wilson")
            student = create_student("student2", "pass", "Student Two")
            db.session.flush()
            
            request_hours_confirmation(student.id)
            assert student.confirmation_requested == True
            
            result, error = confirm_student_hours(staff.id, student.id)
            assert error is None
            assert result.confirmation_requested == False
            
            db.session.rollback()
    
    def test_pending_confirmations(self):
        """Test getting pending confirmation requests"""
        app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
        with app.app_context():
            s1 = create_student("pending1", "pass", "Pending One")
            s2 = create_student("pending2", "pass", "Pending Two")
            s3 = create_student("pending3", "pass", "Pending Three")
            db.session.flush()
            
            request_hours_confirmation(s1.id)
            request_hours_confirmation(s3.id)
            
            pending = get_pending_confirmations()
            assert len(pending) == 2
            
            names = [s['name'] for s in pending]
            assert "Pending One" in names
            assert "Pending Three" in names
            assert "Pending Two" not in names
            
            db.session.rollback()
