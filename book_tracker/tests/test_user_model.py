import pytest
from book_tracker.models.user_model import Users

@pytest.fixture
def sample_user():
    return {
        "username": "testuser",
        "password": "securepassword123"
    }

#### IMPLEMENT THESE
def test_create_user(): return True

def test_create_duplicate_user(): return True