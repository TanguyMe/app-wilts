from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flaskr import create_app
from prediction.predict import comparaison
import spotipy
import os
app=create_app()
@app.route('/')
def hello():
    return redirect('/home')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/playlist_input')
def playlist_input(playlist):
    return render_template(playlist)

@app.route('/input')
def input():
    return render_template('input.html')

@app.route('/unlogged')
def unlogged():
    return render_template('continueunlogged.html')

@app.route('/unlogged/byplaylistID')
def byplaylistID():
    return render_template('input_unlogged_playlists.html')

@app.route('/prediction', methods=['POST'])
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

@app.route('/prediction2')
def prediction2():
    id_playlist = request.values.get('id_playlist')
    id_track = request.values.get('id_track')
    if comparaison([id_playlist], [id_track]):
        return "Bon choix"
    return "Laisse tomber"
    # return redirect(url_for("input"))

@app.route('/login/')
def login():
    scope = "user-library-read"
    sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id=os.environ["SPOTIPY_CLIENT_ID"], client_secret=os.environ["SPOTIPY_CLIENT_SECRET"], redirect_uri = ["SPOTIPY_REDIRECT_URI"], scope = scope)
    auth_url = sp_oauth.get_authorize_url()
    print(os.environ["SPOTIPY_REDIRECT_URI"])
    print(auth_url)
    return redirect(auth_url)

@app.route('/callback')
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
@app.route('/json')
def json():
    return render_template('json.html')

#background process happening without any refreshing
@app.route('/background_process_test')
def background_process_test():
    print ("Hello")
    return ("nothing")

listed = ["patate 1", "patate 2", "patate 3"]
@app.route('/patate', methods=['GET', 'POST'])
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


@app.route('/data', methods=['GET', 'POST'])
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