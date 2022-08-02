#Run python3 -m pytest to test to prevent import errors ou faire . deactivate pour désactiver la base
import pytest
import os
from flaskr.model import User, Historique


@pytest.mark.parametrize("path", ["home", "signup", "log"])
def test_no_auth_ok(client, path):
    response = client.get(path)
    assert response.status_code == 200


def test_redirect(client):
    response = client.get("/")
    assert response.status_code == 302


@pytest.mark.parametrize("path", ["profile", "logged", "logout", "list_playlists", "users", "historique"])
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

@pytest.mark.parametrize("path", ["historique", "users"])
def test_access_admin(client, path):
    _login_user(client, os.environ['ADMIN_MAIL'], os.environ['ADMIN_PASSWORD'])
    response = client.get(path)
    assert response.status_code == 200

@pytest.mark.parametrize("path", ["historique", "users"])
def test_blocked_admin_access(client, path):
    _create_user(client, "email2@gmail.com", "ka", "password", True)
    response = client.get(path)
    assert 'href="/profile' in response.data.decode()
    assert response.status_code == 302


def test_list_playlists(client):
    _create_user(client, "email2@gmail.com", "ka", "password", True)
    response = client.get(
        "/list_playlists", follow_redirects=True
    )
    assert response.status_code == 200
    assert "list_playlists_id" in str(response.data)
    assert "list_playlists_name" in str(response.data)


@pytest.mark.parametrize("playlist_id", ["75Bn4tkz4dpUxcyss6X4xb", "https://open.spotify.com/playlist/0yC9wHLQhqrwFT60RiQgVJ?si=45d190cac2554919"])
def test_get_playlist_name(client, playlist_id):
    _create_user(client, "email2@gmail.com", "ka", "password", True)
    to_send = dict(playlist=playlist_id)
    response = client.post(
        "/playlist_name", data=to_send, follow_redirects=True
    )
    assert response.status_code == 200
    assert "playlist_id" in str(response.data)
    assert "playlist_name" in str(response.data)


@pytest.mark.parametrize("track_id", ["4dfprWJe7cI6yoZachjCwt", "https://open.spotify.com/track/1cM3Yg2598GAgtV8uu2hBZ?si=a9ea332f6b284721"])
def test_get_track_name(client, track_id):
    _create_user(client, "email2@gmail.com", "ka", "password", True)
    to_send = dict(track=track_id)
    response = client.post(
        "/track_name", data=to_send, follow_redirects=True
    )
    assert response.status_code == 200
    assert "track_id" in str(response.data)
    assert "track_name" in str(response.data)


def test_prediction(client):
    with client.application.app_context():
        _create_user(client, "email2@gmail.com", "ka", "password", True)
        list_playlists_id = "75Bn4tkz4dpUxcyss6X4xb, https://open.spotify.com/playlist/0yC9wHLQhqrwFT60RiQgVJ?si=45d190cac2554919"
        list_tracks_id = "4dfprWJe7cI6yoZachjCwt"
        to_send = dict(list_playlists=list_playlists_id, list_tracks=list_tracks_id)
        response = client.post(
            "/prediction", data=to_send, follow_redirects=True
        )
        assert response.status_code == 200
        assert Historique.query.filter(Historique.id == 1).first()


def test_update_self_user(client):
    _create_user(client, "email2@gmail.com", "ka", "password", True)
    userid = 2
    to_send = dict(userid=userid)
    response = client.post(
        "/update", data=to_send
    )
    assert response.status_code == 200


def test_update_admin_user(client):
    _create_user(client, "email2@gmail.com", "ka", "password", True)
    _logout_user(client)
    _login_user(client, os.environ['ADMIN_MAIL'], os.environ['ADMIN_PASSWORD'])
    userid = 2
    to_send = dict(userid=userid)
    response = client.post(
        "/update", data=to_send
    )
    assert response.status_code == 200


def test_not_update_other_user(client):
    _create_user(client, "email2@gmail.com", "ka", "password", True)
    userid = 1
    to_send = dict(userid=userid)
    response = client.post(
        "/update", data=to_send
    )
    assert 'href="/profile' in response.data.decode()
    assert response.status_code == 302


@pytest.mark.parametrize("path", ["/update", "update_user/1", "update_histo/1", "delete_histo/1", "delete_user/1"])
def test_not_update_unlogged(client, path):
    response = client.post(
        path
    )
    assert 'href="/log?next=' in response.data.decode()
    assert response.status_code == 302


def test_admin_update_historique(client):
    _login_user(client, os.environ['ADMIN_MAIL'], os.environ['ADMIN_PASSWORD'])
    historiqueid = 1
    to_send = dict(historiqueid=historiqueid)
    response = client.post(
        "/update", data=to_send
    )
    assert response.status_code == 200


def test_user_not_update_historique(client):
    _create_user(client, "email2@gmail.com", "ka", "password", True)
    historiqueid = 1
    to_send = dict(historiqueid=historiqueid)
    response = client.post(
        "/update", data=to_send
    )
    assert 'href="/profile' in response.data.decode()
    assert response.status_code == 302


def test_user_added_to_db(client):
    with client.application.app_context():
        _create_user(client, "email2@gmail.com", "ka", "password", True)
        assert User.query.filter(User.email == "email2@gmail.com").first()


def test_update_user(client):
    with client.application.app_context():
        _create_user(client, "email2@gmail.com", "ka", "password", True)
        to_send = dict(spotifyID="newid")
        response = client.post(
            "/update_user/2", data=to_send , follow_redirects=True
        )
        assert response.status_code == 200
        assert User.query.filter(User.spotifyid == "newid").first()


def test_update_user_admin(client):
    with client.application.app_context():
        _create_user(client, "email2@gmail.com", "ka", "password", True)
        _logout_user(client)
        _login_user(client, os.environ['ADMIN_MAIL'], os.environ['ADMIN_PASSWORD'])
        to_send = dict(spotifyID="newid")
        response = client.post(
            "/update_user/2", data=to_send , follow_redirects=True
        )
        assert response.status_code == 200
        assert User.query.filter(User.spotifyid == "newid").first()


def test_delete_user(client):
    with client.application.app_context():
        _create_user(client, "email2@gmail.com", "ka", "password", True)
        response = client.post(
            "/delete_user/2", follow_redirects=True
        )
        assert response.status_code == 200
        assert not User.query.filter(User.email == "email2@gmail.com").first()


def test_delete_user_admin(client):
    with client.application.app_context():
        _create_user(client, "email2@gmail.com", "ka", "password", True)
        _logout_user(client)
        _login_user(client, os.environ['ADMIN_MAIL'], os.environ['ADMIN_PASSWORD'])
        response = client.post(
            "/delete_user/2", follow_redirects=True
        )
        assert response.status_code == 200
        assert not User.query.filter(User.email == "email2@gmail.com").first()


@pytest.mark.parametrize("path", ["/update_histo/1", "delete_histo/1"])
def test_not_histo(client, path):
    _create_user(client, "email2@gmail.com", "ka", "password", True)
    response = client.post(
        path
    )
    assert 'href="/profile' in response.data.decode()
    assert response.status_code == 302


@pytest.mark.parametrize("satisfaction", ["True", "False", "None"])
def test_update_histo(client, satisfaction):
    with client.application.app_context():
        _login_user(client, os.environ['ADMIN_MAIL'], os.environ['ADMIN_PASSWORD'])
        list_playlists_id = "75Bn4tkz4dpUxcyss6X4xb, https://open.spotify.com/playlist/0yC9wHLQhqrwFT60RiQgVJ?si=45d190cac2554919"
        list_tracks_id = "4dfprWJe7cI6yoZachjCwt"
        to_send = dict(list_playlists=list_playlists_id, list_tracks=list_tracks_id)
        client.post(
            "/prediction", data=to_send, follow_redirects=True
        )
        to_send = dict(satisfaction=satisfaction)
        response = client.post(
            "/update_histo/1", data=to_send, follow_redirects=True
        )
        assert response.status_code == 200
        assert str(Historique.query.filter(Historique.id == 1).first().satisfaction) == satisfaction


def test_delete_histo(client):
    with client.application.app_context():
        _login_user(client, os.environ['ADMIN_MAIL'], os.environ['ADMIN_PASSWORD'])
        list_playlists_id = "75Bn4tkz4dpUxcyss6X4xb, https://open.spotify.com/playlist/0yC9wHLQhqrwFT60RiQgVJ?si=45d190cac2554919"
        list_tracks_id = "4dfprWJe7cI6yoZachjCwt"
        to_send = dict(list_playlists=list_playlists_id, list_tracks=list_tracks_id)
        client.post(
            "/prediction", data=to_send, follow_redirects=True
        )
        response = client.post(
            "/delete_histo/1", follow_redirects=True
        )
        assert response.status_code == 200
        assert not Historique.query.filter(Historique.id == 1).first()
