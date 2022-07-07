#Run python3 -m pytest to test to prevent import errors ou faire . deactivate pour désactiver la base
import pytest


@pytest.mark.parametrize("path", ["home", "signup", "log"])
def test_no_auth_ok(client, path):
    response = client.get(path)
    assert response.status_code == 200


def test_redirect(client):
    response = client.get("/")
    assert response.status_code == 302


@pytest.mark.parametrize("path", ["profile", "logged", "logout", "list_playlists"])
def test_must_login(client, path):
    response = client.get(path)
    assert 'href="/log?next=' in response.data.decode()
    assert response.status_code == 302


def _create_user(client, email, spotifyid, password, remember):
    response = client.post(
        "/signup",
        data=dict(email=email, spotifyid=spotifyid, password=password, remember=remember),
        follow_redirects=True,
    )
    assert response.status_code == 200


def _login_user(client, email, password):
    response = client.post(
        "/login", data=dict(email=email, password=password), follow_redirects=True
    )
    assert response.status_code == 200
    data = response.data.decode()
    assert data.find("Login User") == -1


def _logout_user(client):
    response = client.get("/logout", follow_redirects=True)
    assert response.status_code == 200


def test_signup_user_success(client):
    _create_user(client, "email2@gmail.com", "ka", "password", True)


def test_signup_user_bad_input(client):
    with pytest.raises(AttributeError):
        client.post("/signup", follow_redirects=True)


def test_register_user_email_exists(client):
    _create_user(client, "email2@gmail.com", "ka", "password", True)
    _logout_user(client)
    response = client.post(
        "/signup",
        data=dict(email="email2@gmail.com", spotifyid="ka", password="password", remember=True),
        follow_redirects=True,
    )
    # We make sure that if the user already exists, user returns to sign up page
    assert "signup" in str(response.request)


def test_login_user_invalid_credentials(client):
    response = client.post(
        "/login",
        data=dict(email="abc@gmail.com", password="password"),
        follow_redirects=True,
    )
    # We make sure that if the user has wrong credentials, it stays on the log page
    assert "log'" in str(response.request)


def test_login_user_bad_data(client):
    response = client.post("/login", follow_redirects=True)
    # We make sure that if the user has wrong credentials, it stays on the log page
    assert "log'" in str(response.request)


def test_login_user_success(client):
    _create_user(client, "email2@gmail.com", "ka", "password", True)
    _logout_user(client)
    _login_user(client, "email@gmail.com", "password")

@pytest.mark.parametrize("path", ["profile", "logged", "list_playlists"])
def test_logged(client, path):
    _create_user(client, "email2@gmail.com", "ka", "password", True)
    response = client.get(path)
    assert response.status_code == 200
