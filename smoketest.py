import requests


def run_smoketest():
    base_url = "http://localhost:5003/api"
    username = "test"
    password = "test"

    book_mockingbird = {
        "title":"To Kill a Mockingbird",
        "authors":"Harper Lee",
        "isbn":"9782253115847",
        "shelf":"FINISHED",
    }

    book_gatsby = {
        "title":"The Great Gatsby",
        "authors":"F. Scott Fitzgerald",
        "isbn":"9780333791035",
        "shelf":"CURRENTLY_READING",
    }

    health_response = requests.get(f"{base_url}/health")
    assert health_response.status_code == 200
    assert health_response.json()["status"] == "success"

    delete_user_response = requests.delete(f"{base_url}/reset-users")
    assert delete_user_response.status_code == 200
    assert delete_user_response.json()["status"] == "success"
    print("Reset users successful")

    delete_book_response = requests.delete(f"{base_url}/reset-books")
    assert delete_book_response.status_code == 200
    assert delete_book_response.json()["status"] == "success"
    print("Reset book successful")

    create_user_response = requests.put(f"{base_url}/create-user", json={
        "username": username,
        "password": password
    })
    assert create_user_response.status_code == 201
    assert create_user_response.json()["status"] == "success"
    print("User creation successful")
    
    session = requests.Session()


    # Log in
    login_resp = session.post(f"{base_url}/login", json={
        "username": username,
        "password": password
    })
    assert login_resp.status_code == 200
    assert login_resp.json()["status"] == "success"
    print("Login successful")

    create_book_resp = session.post(f"{base_url}/create-book", json=book_mockingbird)
    assert create_book_resp.status_code == 201
    assert create_book_resp.json()["status"] == "success"
    print("book creation successful")

    # Change password
    change_password_resp = session.post(f"{base_url}/change-password", json={
        "new_password": "new_password"
    })
    assert change_password_resp.status_code == 200
    assert change_password_resp.json()["status"] == "success"
    print("Password change successful")

    # Log in with new password
    login_resp = session.post(f"{base_url}/login", json={
        "username": username,
        "password": "new_password"
    })
    assert login_resp.status_code == 200
    assert login_resp.json()["status"] == "success"
    print("Login with new password successful")


    create_book_resp = session.post(f"{base_url}/create-book", json=book_gatsby)
    assert create_book_resp.status_code == 201
    assert create_book_resp.json()["status"] == "success"
    print("book creation successful")

    # Log out
    logout_resp = session.post(f"{base_url}/logout")
    assert logout_resp.status_code == 200
    assert logout_resp.json()["status"] == "success"
    print("Logout successful")

    create_book_logged_out_resp = session.post(f"{base_url}/create-book", json=book_mockingbird)
    # This should fail because we are logged out
    assert create_book_logged_out_resp.status_code == 401
    assert create_book_logged_out_resp.json()["status"] == "error"
    print("Book creation failed as expected")

if __name__ == "__main__":
    run_smoketest()



    