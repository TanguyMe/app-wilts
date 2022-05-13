from flask import Blueprint, Flask, render_template, request, redirect, url_for, jsonify, session, request, flash
from prediction.predict import comparaison
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from .model import User
from . import db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('home.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', spotifyid=current_user.spotifyid)

@main.route('/')
def hello():
    return redirect('/home')

@main.route('/home')
def home():
    return render_template('home.html')

@main.route('/playlist_input')
def playlist_input(playlist):
    return render_template(playlist)

@main.route('/input')
def input():
    return render_template('input.html')

@main.route('/unlogged')
def unlogged():
    return render_template('continueunlogged.html')

@main.route('/unlogged/byplaylistID')
def byplaylistID():
    return render_template('input_unlogged_playlists.html')

@main.route('/prediction', methods=['POST'])
def prediction():
    list_playlists_url = request.values.get('list_playlists')
    list_tracks_url = request.values.get('list_tracks')
    if list_playlists_url and list_tracks_url:
        list_playlists_url = list_playlists_url.split(",")
        list_tracks_url = list_tracks_url.split(",")
        import re
        pattern_playlist = '(?<=playlist[:|/])[^?]*'
        pattern_track = '(?<=track[:|/])[^?]*'
        list_playlists_id = [re.search(pattern_playlist, url).group() for url in list_playlists_url]
        list_tracks_id = [re.search(pattern_track, url).group() for url in list_tracks_url]
        results = []
        for track in list_tracks_id:
            if comparaison(list_playlists_id, [track]):
                results.append("Bon choix")
            else:
                results.append("Laisse tomber")
        print("RESULTS: ", results)
        print(jsonify({"results": results}))
        return jsonify({"results": results})

@main.route('/prediction2')
def prediction2():
    id_playlist = request.values.get('id_playlist')
    id_track = request.values.get('id_track')
    if comparaison([id_playlist], [id_track]):
        return "Bon choix"
    return "Laisse tomber"
    # return redirect(url_for("input"))

@main.route('/logging')
def logging():
    return render_template('logging.html')

@main.route('/log')
def login():
    return render_template('login.html')

@main.route('/signup')
def signup():
    return render_template('signup.html')

@main.route('/logged')
def logged():
    return render_template('logged.html')

@main.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    # check if user actually exists
    # take the user supplied password, hash it, and compare it to the hashed password in database
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login')) # if user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('main.logged'))

@main.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    spotifyid = request.form.get('spotifyid')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

    if user: # if a user is found, we want to redirect back to signup page so user can try again
        flash('Email address already exists')
        return redirect(url_for('main.signup'))

    # create new user with the form data. Hash the password so plaintext version isn't saved.
    new_user = User(email=email, spotifyid=spotifyid, password=generate_password_hash(password, method='sha256'))

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    login_user(new_user, remember=remember)
    return redirect(url_for('main.logged'))

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@main.route('/list_playlists', methods=['GET', 'POST'])
@login_required
def list_playlists():
    list_playlists_id = []
    list_playlists_name = []
    print("USER", current_user.email)
    print("id", current_user.spotifyid)
    spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
    results = spotify.user_playlists(current_user.spotifyid)
    print("results: ", results)
    while results:
        for playlist in results['items']:
            list_playlists_id.append(playlist['id'])
            list_playlists_name.append(playlist['name'])
        results = spotify.next(results)
    print("playlist name: ", list_playlists_name)
    print("playlist id: ", list_playlists_id)
    if not list_playlists_name:
        if not list_playlists_id:
            return jsonify({"list_playlists_id": ['vide'], "list_playlists_name": ['vide']})
    return jsonify({"list_playlists_id": list_playlists_id, "list_playlists_name": list_playlists_name})


@main.route('/playlist_name', methods=['POST'])
def get_playlist_name():
    playlist_url = request.values.get('playlist')
    print("playlist", playlist_url)
    import re
    pattern_playlist = '(?<=playlist[:|/])[^?]*'
    if re.match(pattern_playlist, playlist_url):
        playlist_id=re.search(pattern_playlist, playlist_url)
    else:
        playlist_id=playlist_url
    spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
    playlist_name = spotify.playlist(playlist_id)['name']
    return jsonify({"playlist_id": playlist_id, "playlist_name": playlist_name})


@main.route('/track_name', methods=['POST'])
def get_track_name():
    track_url = request.values.get('track')
    print("track", track_url)
    import re
    pattern_track = '(?<=track[:|/])[^?]*'
    if re.match(pattern_track, track_url):
        track_id = re.search(pattern_track, track_url)
    else:
        track_id = track_url
    spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
    results = spotify.track(track_id)
    track_name = results['name'] + " - " + results['artists'][0]['name']
    return jsonify({"track_id": track_id, "track_name": track_name})

# @main.route('/login/')
# def login():
#     scope = "user-library-read"
#     sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id=os.environ["SPOTIPY_CLIENT_ID"], client_secret=os.environ["SPOTIPY_CLIENT_SECRET"], redirect_uri = ["SPOTIPY_REDIRECT_URI"], scope = scope)
#     auth_url = sp_oauth.get_authorize_url()
#     print(os.environ["SPOTIPY_REDIRECT_URI"])
#     print(auth_url)
#     return redirect(auth_url)

@main.route('/callback')
def callback():
    # Don't reuse a SpotifyOAuth object because they store token info and you could leak user tokens if you reuse a SpotifyOAuth object
    scope = "user-library-read"
    sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id=os.environ["SPOTIPY_CLIENT_ID"],
                                           client_secret=os.environ["SPOTIPY_CLIENT_SECRET"],
                                           redirect_uri=["SPOTIPY_REDIRECT_URI"], scope=scope)
    print("URI REDIRECT: ", os.environ["SPOTIPY_REDIRECT_URI"])
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)

    # Saving the access token along with all other token related info
    session["token_info"] = token_info
    return redirect("home")

#rendering the HTML page which has the button
@main.route('/json')
def json():
    return render_template('json.html')

#background process happening without any refreshing
@main.route('/background_process_test')
def background_process_test():
    print ("Hello")
    return ("nothing")

listed = ["patate 1", "patate 2", "patate 3"]
@main.route('/patate', methods=['GET', 'POST'])
def patate():
    desc=""
    id_value = request.form.get('datasource')
    def description_value(select):
        for data in listed:
            if data == select:
                return data
    if id_value:
        desc = description_value(id_value)
    return render_template('json.html', two_dimensional_list=listed, desc=desc)


@main.route('/data', methods=['GET', 'POST'])
def data():
    id_value = request.form.get('datasource')
    def description_value(select):
        for data in listed:
            if data == select:
                return data
    return description_value(id_value)

# https://github.com/charles-42/flask_tutorial/tree/master/channel_app
# https://github.com/SprinTech/sound-recognizer/tree/backend/backend
# https://github.com/pallets/flask/tree/2.0.3/examples/tutorial