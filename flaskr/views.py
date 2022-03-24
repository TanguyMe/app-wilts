from flask import Flask, render_template, request, redirect, url_for
from flaskr import app
from prediction.predict import comparaison

@app.route('/')
def hello():
    return render_template('home.html')

@app.route('/playlist_input')
def playlist_input(playlist):
    return render_template(playlist)

@app.route('/input')
def input():
    return render_template('input.html')

@app.route('/prediction')
def prediction():
    id_playlist = request.values.get('id_playlist')
    id_track = request.values.get('id_track')
    if comparaison([id_playlist], [id_track]):
        return "Bon choix"
    return "Laisse tomber"
    # return redirect(url_for("input"))



# https://github.com/charles-42/flask_tutorial/tree/master/channel_app
# https://github.com/SprinTech/sound-recognizer/tree/backend/backend
# https://github.com/pallets/flask/tree/2.0.3/examples/tutorial