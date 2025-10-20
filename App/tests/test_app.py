import os, tempfile, pytest, logging, unittest
from werkzeug.security import check_password_hash, generate_password_hash

from App.main import create_app
from App.database import db, create_db
from App.models import User
from App.controllers import (
    create_user,
    get_all_users_json,
    login,
    get_user,
    get_user_by_username,
    update_user
)


LOGGER = logging.getLogger(__name__)

'''
   Unit Tests
'''
class UserUnitTests(unittest.TestCase):

    def test_new_user(self):
        user = User("bob", "bobpass", "Bob User")
        assert user.username == "bob"
        assert user.name == "Bob User"

    # pure function no side effects or integrations called
    def test_get_json(self):
        user = User("bob", "bobpass", "Bob User")
        user_json = user.get_json()
        assert user_json['username'] == "bob"
        assert user_json['name'] == "Bob User"
    
    def test_hashed_password(self):
        password = "mypass"
        user = User("bob", password, "Bob User")
        assert user.password != password

    def test_check_password(self):
        password = "mypass"
        user = User("bob", password, "Bob User")
        assert user.check_password(password)

'''
    Integration Tests
'''

# This fixture creates an empty database for the test and deletes it after the test
# scope="class" would execute the fixture once and resued for all methods in the class
@pytest.fixture(autouse=True, scope="module")
def empty_db():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
    create_db()
    yield app.test_client()
    db.drop_all()


def test_authenticate():
    user = create_user("bob", "bobpass", "Bob User")
    assert login("bob", "bobpass") != None

class UsersIntegrationTests(unittest.TestCase):

    def test_create_user(self):
        user = create_user("rick", "bobpass", "Rick User")
        assert user.username == "rick"
        assert user.name == "Rick User"

    def test_get_all_users_json(self):
        users_json = get_all_users_json()
        assert len(users_json) >= 2

    # Tests data changes in the database
    def test_update_user(self):
        update_user(1, "ronnie")
        user = get_user(1)
        assert user.username == "ronnie"
