import pytest
import json
from App.main import create_app
from App.database import db
from App.controllers import create_student, create_staff


@pytest.fixture(autouse=True, scope="module")
def client():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        create_student("apitest_student", "student123", "API Test Student")
        create_staff("apitest_staff", "staff123", "API Test Staff")
        
        yield app.test_client()
        
        db.drop_all()


class TestAPIIntegration:
    
    def test_login_student(self, client):
        """Test student login"""
        response = client.post('/api/login',
            json={'username': 'apitest_student', 'password': 'student123'})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'access_token' in data
    
    def test_login_staff(self, client):
        """Test staff login"""
        response = client.post('/api/login',
            json={'username': 'apitest_staff', 'password': 'staff123'})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'access_token' in data
    
    def test_login_invalid(self, client):
        """Test invalid login"""
        response = client.post('/api/login',
            json={'username': 'invalid', 'password': 'wrong'})
        assert response.status_code == 401
    
    def test_get_student_profile(self, client):
        """Test getting student profile"""
        login_resp = client.post('/api/login',
            json={'username': 'apitest_student', 'password': 'student123'})
        token = json.loads(login_resp.data)['access_token']
        
        response = client.get('/api/students/me',
            headers={'Authorization': f'Bearer {token}'})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['username'] == 'apitest_student'
        assert data['user_type'] == 'student'
    
    def test_request_confirmation(self, client):
        """Test student requesting confirmation"""
        login_resp = client.post('/api/login',
            json={'username': 'apitest_student', 'password': 'student123'})
        token = json.loads(login_resp.data)['access_token']
        
        response = client.post('/api/students/me/request-confirmation',
            headers={'Authorization': f'Bearer {token}'})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Confirmation request sent'
    
    def test_get_leaderboard(self, client):
        """Test getting leaderboard"""
        login_resp = client.post('/api/login',
            json={'username': 'apitest_student', 'password': 'student123'})
        token = json.loads(login_resp.data)['access_token']
        
        response = client.get('/api/leaderboard',
            headers={'Authorization': f'Bearer {token}'})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
    
    def test_staff_log_hours(self, client):
        """Test staff logging hours"""
        login_resp = client.post('/api/login',
            json={'username': 'apitest_staff', 'password': 'staff123'})
        token = json.loads(login_resp.data)['access_token']
        
        response = client.post('/api/staff/log-hours',
            headers={'Authorization': f'Bearer {token}'},
            json={'student_id': 1, 'hours': 15})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'message' in data
    
    def test_unauthorized_access(self, client):
        """Test accessing protected route without token"""
        response = client.get('/api/students/me')
        assert response.status_code in [401, 403]
