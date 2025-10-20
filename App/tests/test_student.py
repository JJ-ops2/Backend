import pytest
from App.main import create_app
from App.database import db
from App.models import Student, Staff
from App.controllers import (
    create_student,
    get_student,
    add_hours_to_student,
    request_hours_confirmation,
    get_student_accolades,
    get_leaderboard
)


@pytest.fixture(autouse=True, scope="module")
def empty_db():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


class TestStudentUnit:
    
    def test_new_student(self):
        """Test creating a new student"""
        student = Student(username="testuser", password="testpass", name="Test User")
        assert student.username == "testuser"
        assert student.name == "Test User"
        assert student.total_hours == 0
        assert student.confirmation_requested == False
    
    def test_add_hours(self):
        """Test adding hours to student"""
        student = Student(username="testuser2", password="testpass", name="Test User 2")
        student.add_hours(5)
        assert student.total_hours == 5
        student.add_hours(10)
        assert student.total_hours == 15
    
    def test_negative_hours(self):
        """Test that negative hours raise an error"""
        student = Student(username="testuser3", password="testpass", name="Test User 3")
        with pytest.raises(ValueError):
            student.add_hours(-5)
    
    def test_request_confirmation(self):
        """Test requesting confirmation"""
        student = Student(username="testuser4", password="testpass", name="Test User 4")
        assert student.confirmation_requested == False
        student.request_confirmation()
        assert student.confirmation_requested == True
    
    def test_accolades(self):
        """Test accolade system"""
        app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
        with app.app_context():
            student = create_student("accolade_test", "pass", "Accolade Tester")
            db.session.flush()
            
            add_hours_to_student(student.id, 10)
            student = get_student(student.id)
            accolades = student.get_accolades()
            assert 10 in accolades
            
            add_hours_to_student(student.id, 15)
            student = get_student(student.id)
            accolades = student.get_accolades()
            assert 10 in accolades
            assert 25 in accolades
            
            db.session.rollback()


class TestStudentIntegration:
    
    def test_create_student_controller(self):
        """Test creating student via controller"""
        app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
        with app.app_context():
            student = create_student("john", "john123", "John Doe")
            assert student.username == "john"
            assert student.name == "John Doe"
            db.session.rollback()
    
    def test_add_hours_controller(self):
        """Test adding hours via controller"""
        app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
        with app.app_context():
            student = create_student("jane", "jane123", "Jane Doe")
            db.session.flush()
            
            updated = add_hours_to_student(student.id, 15)
            assert updated.total_hours == 15
            
            db.session.rollback()
    
    def test_leaderboard(self):
        """Test leaderboard functionality"""
        app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
        with app.app_context():
            s1 = create_student("leader1", "pass", "Leader One")
            s2 = create_student("leader2", "pass", "Leader Two")
            s3 = create_student("leader3", "pass", "Leader Three")
            db.session.flush()
            
            add_hours_to_student(s1.id, 50)
            add_hours_to_student(s2.id, 25)
            add_hours_to_student(s3.id, 75)
            
            leaderboard = get_leaderboard()
            assert leaderboard[0]['name'] == "Leader Three"
            assert leaderboard[0]['total_hours'] == 75
            assert leaderboard[1]['total_hours'] == 50
            assert leaderboard[2]['total_hours'] == 25
            
            db.session.rollback()
    
    def test_request_confirmation_controller(self):
        """Test requesting confirmation via controller"""
        app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
        with app.app_context():
            student = create_student("confirm_test", "pass", "Confirm Tester")
            db.session.flush()
            
            assert student.confirmation_requested == False
            updated = request_hours_confirmation(student.id)
            assert updated.confirmation_requested == True
            
            db.session.rollback()
