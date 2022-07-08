from flask import Blueprint, Flask, render_template, request, redirect, url_for, jsonify, session, request, flash
from prediction.predict import comparaison
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from .model import User, Historique
from . import db
from datetime import datetime
import re

main = Blueprint('main', __name__)

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@main.route('/users')
@login_required
def users():
    if current_user.role == 'admin':
        full_query = User.query.all()
        data = [user.as_dict() for user in full_query]
        columns = [{"field": col, "title": col, "sortable": True} for col in User.__table__.columns.keys()]
        return render_template("users.html",
                               data=data,
                               columns=columns,
                               title='Users')
    return redirect(url_for('main.profile'))

@main.route('/historique')
@login_required
def historique():
    if current_user.role == 'admin':
        full_query = Historique.query.all()
        data = [hist.as_dict() for hist in full_query]
        columns = [{"field": col, "title": col, "sortable": True} for col in Historique.__table__.columns.keys()]
        return render_template("historique.html",
                               data=data,
                               columns=columns,
                               title='Historique')
    return redirect(url_for('main.profile'))

@main.route('/')
def index():
    return redirect('/home')

@main.route('/home')
def home():
    return render_template('home.html')

@main.route('/prediction', methods=['POST'])
def prediction():
    list_playlists_id = request.values.get('list_playlists')
    list_tracks_id = request.values.get('list_tracks')
    if list_playlists_id and list_tracks_id:
        list_playlists_id = list_playlists_id.split(",")
        list_tracks_id = list_tracks_id.split(",")
        results = []
        for comp in comparaison(list_playlists_id, list_tracks_id):
            print("COMP: ", comp)
            if comp:
                results.append(1)
            else:
                results.append(0)
        for i in range(len(list_tracks_id)):
            # create new user with the form data. Hash the password so plaintext version isn't saved.
            histo = Historique(userid=current_user.id, playlistsid=str(list_playlists_id), trackid=list_tracks_id[i],
                               prediction=results[i], date=datetime.today())
            # add the new user to the database
            db.session.add(histo)
            db.session.commit()
        return jsonify({"results": results})

@main.route('/log')
def login():
    return render_template('login.html')

@main.route('/signup')
def signup():
    return render_template('signup.html')

@main.route('/logged')
@login_required
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
        return redirect(url_for('main.login')) # if user doesn't exist or password is wrong, reload the page

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
    new_user = User(email=email, spotifyid=spotifyid, password=generate_password_hash(password, method='sha256'), role="user")

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
    spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
    results = spotify.user_playlists(current_user.spotifyid)
    while results:
        for playlist in results['items']:
            list_playlists_id.append(playlist['id'])
            list_playlists_name.append(playlist['name'])
        results = spotify.next(results)
    if not list_playlists_name:
        if not list_playlists_id:
            return jsonify({"list_playlists_id": [], "list_playlists_name": []})
    return jsonify({"list_playlists_id": list_playlists_id, "list_playlists_name": list_playlists_name})


@main.route('/playlist_name', methods=['POST'])
def get_playlist_name():
    playlist_url = request.values.get('playlist')
    pattern_playlist = '(?<=playlist[:|/])[^?]*'
    if re.search(pattern_playlist, playlist_url):
        playlist_id=re.search(pattern_playlist, playlist_url).group(0)
    else:
        playlist_id=playlist_url
    spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
    playlist_name = spotify.playlist(playlist_id)['name']
    return jsonify({"playlist_id": playlist_id, "playlist_name": playlist_name})


@main.route('/track_name', methods=['POST'])
def get_track_name():
    track_url = request.values.get('track')
    pattern_track = '(?<=track[:|/])[^?]*'
    if re.search(pattern_track, track_url):
        track_id = re.search(pattern_track, track_url).group(0)
    else:
        track_id = track_url
    spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
    results = spotify.track(track_id)
    track_name = results['name'] + " - " + results['artists'][0]['name']
    return jsonify({"track_id": track_id, "track_name": track_name})


@main.route('/update', methods=['GET', 'POST'])
@login_required
def update():
    if request.form.get('userid'):
        userid = request.form.get('userid')
        if str(current_user.id) == userid or current_user.role == 'admin':
            if request.method == 'POST':
                return render_template('update_user.html', user=db.session.query(User).filter(User.id == userid).first())
                user.spotifyid = request.form.get('spotifyID')
                db.session.commit()
                if current_user.role == 'admin':
                    return redirect(url_for('main.users'))
    if request.form.get('historiqueid'):
        historiqueid = request.form.get('historiqueid')
        if current_user.role == 'admin':
            if request.method == 'POST':
                return render_template('update_histo.html',
                                       histo=db.session.query(Historique).filter(Historique.id == historiqueid).first())
                if request.form.get("satisfaction"):
                    histo.satisfaction = request.form.get("satisfaction")
                db.session.commit()
                return redirect(url_for('main.historique'))
    return redirect(url_for('main.profile'))


@main.route('/update_user/<userid>', methods=['POST'])
@login_required
def update_user(userid):
    if str(current_user.id) == userid or current_user.role == 'admin':
        user=db.session.query(User).filter(User.id == userid).first()
        user.spotifyid = request.form.get('spotifyID')
        db.session.commit()
        if current_user.role == 'admin':
            return redirect(url_for('main.users'))
    return redirect(url_for('main.profile'))


@main.route('/delete_user/<userid>', methods=['POST', 'GET'])
@login_required
def delete_user(userid):
    if str(current_user.id) == userid or current_user.role == 'admin':
        user = db.session.query(User).filter(User.id == userid).first()
        if str(current_user.id) == userid:
            logout_user()
        db.session.delete(user)
        db.session.commit()
        try:
            if current_user.role == 'admin':
                return redirect(url_for('main.users'))
        except:
            pass
    return redirect(url_for('main.profile'))


@main.route('/update_histo/<histoid>', methods=['POST'])
@login_required
def update_histo(histoid):
    if current_user.role == 'admin':
        histo = db.session.query(Historique).filter(Historique.id == histoid).first()
        request_value = request.form.get('satisfaction')
        if request_value == 'None':
            request_value = None
        else:
            request_value = bool(request_value)
        histo.satisfaction = request_value
        db.session.commit()
        return redirect(url_for('main.historique'))
    return redirect(url_for('main.profile'))



@main.route('/delete_histo/<histoid>', methods=['POST'])
@login_required
def delete_histo(histoid):
    if current_user.role == 'admin':
        histo = db.session.query(Historique).filter(Historique.id == histoid).first()
        db.session.delete(histo)
        db.session.commit()
        return redirect(url_for('main.historique'))
    return redirect(url_for('main.profile'))


# https://github.com/charles-42/flask_tutorial/tree/master/channel_app
# https://github.com/SprinTech/sound-recognizer/tree/backend/backend
# https://github.com/pallets/flask/tree/2.0.3/examples/tutorial