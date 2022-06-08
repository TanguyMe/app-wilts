#Run python3 -m pytest to test to prevent import errors ou faire . deactivate pour désactiver la base
from tests.conftest import client


def test_home_ok(client):
    response = client.get('/')
    assert response.status_code == 200
    response = client.get('/home')
    assert response.status_code == 200


def _create_user(client, email, spotifyid, password, remember):
    rv = client.post(
        "/signup",
        data=dict(email=email, spotifyid=spotifyid, password=password, remember=remember),
        follow_redirects=True,
    )
    assert rv.status_code == 200
    # data = rv.data.decode()
    # assert data.find("Register User") == -1


def test_login_user_success(client, db_session):
    _create_user(client, "ka", "email2@gmail.com", "password", True)
    # _logout_user(client)
    # _login_user(client, "email@gmail.com", "password")

# def _login_user(client, email, password):
#     rv = client.post(
#         "/login", data=dict(email=email, password=password), follow_redirects=True
#     )
#     assert rv.status_code == 200
#     data = rv.data.decode()
#     assert data.find("Login User") == -1