import spotipy
import logging
import pandas as pd
from datetime import datetime
from spotipy.oauth2 import SpotifyClientCredentials
import requests

spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
logger = logging.getLogger()

from sklearn import metrics
def cv_silhouette_scorer(estimator, X):
    estimator.fit(X)
    cluster_labels = estimator['model'].labels_
    num_labels = len(set(cluster_labels))
    num_samples = len(X.index)
    if num_labels == 1 or num_labels == num_samples:
        return -1
    else:
        return metrics.silhouette_score(X, cluster_labels)


def extract_audio_feature(ids_list):
    list_features = []
    try:
        list_features = spotify.audio_features(ids_list)
    except Exception as e:
        print(e)
        logger.info(e)
    return list_features


def get_features(df):
    tracks_features_list = []

    total_tracks = df.shape[0]

    start = datetime.now()
    print("start = ", start)
    for tracks_nbr in range(0, total_tracks, 100):
        print(f"Progression of tracks: {tracks_nbr}/{total_tracks}")
        tracks_features_list += extract_audio_feature(','.join(df.track_id[tracks_nbr:tracks_nbr + 100]))
    remaining_tracks = total_tracks % 100
    if remaining_tracks:
        tracks_features_list += extract_audio_feature(','.join(df.track_id[-remaining_tracks:]))
    end = datetime.now()
    print("finish = ", end)
    print("duration = ", (end - start).total_seconds())
    tracks_features_list = [track for track in tracks_features_list if isinstance(track, dict)]
    df2 = pd.DataFrame(tracks_features_list)
    df2.drop_duplicates(inplace=True)
    final_df = df.set_index('track_id').join(df2.set_index('id'), how='inner')
    columns = ['id', 'track_name', 'artist_name', 'popularity', 'duration_ms',
               'danceability', 'time_signature', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness',
               'instrumentalness', 'liveness', 'valence', 'tempo']

    nominal_cols = ['id', 'track_name', 'artist_name']
    discret_cols = ['key', 'mode']
    continuous_cols = ['popularity', 'duration_ms', 'danceability', 'time_signature', 'loudness', 'speechiness',
                       'instrumentalness', 'liveness', 'valence', 'tempo', 'acousticness*energy']
    useful_cols = discret_cols + continuous_cols
    final_df['acousticness*energy'] = final_df['acousticness'] * final_df['energy']
    final_df = final_df[useful_cols]
    return final_df


def predict_playlist(list_playlist_id):
    tracks_data_list = []

    start = datetime.now()
    print("start = ", start)
    try:
        for playlist_id in list_playlist_id:
            track_results = spotify.playlist_tracks(playlist_id=playlist_id)
            while track_results:
                for track in track_results['items']:
                    single_track_dict = {
                        'track_name': track['track']['name'],
                        'artist_name': track['track']['artists'][0]['name'],
                        'track_id': track['track']['id'],
                        'popularity': track['track']['popularity']
                    }
                    tracks_data_list.append(single_track_dict)
                track_results = spotify.next(track_results)
            print(f"Progression of playlists: {list_playlist_id.index(playlist_id) + 1}/{len(list_playlist_id)}")
    except Exception as e:
        logger.error(e)
    end = datetime.now()
    print("finish = ", end)
    print("duration = ", (end - start).total_seconds())
    df = pd.DataFrame(tracks_data_list)
    df.drop_duplicates(inplace=True)
    return get_features(df)


def predict_track(track_ids: list):
    tracks_data_list = []

    start = datetime.now()
    print("start = ", start)
    try:
        track_results = spotify.tracks(track_ids)
        for track in track_results['tracks']:
            single_track_dict = {
                'track_name': track['name'],
                'artist_name': track['artists'][0]['name'],
                'track_id': track['id'],
                'popularity': track['popularity']
            }
            tracks_data_list.append(single_track_dict)
    except Exception as e:
        logger.error(e)
    end = datetime.now()
    print("finish = ", end)
    print("duration = ", (end - start).total_seconds())
    df = pd.DataFrame(tracks_data_list)
    df.drop_duplicates(inplace=True)
    return get_features(df)


def comparaison(list_playlist_id, track_ids):
    print("list playlist:", list_playlist_id)
    print("list tracks:", track_ids)
    df_playlist = predict_playlist(list_playlist_id)
    df_tracks = predict_track(track_ids)
    print("playlists", df_playlist)
    print("tracks", df_tracks)
    # df_playlist['prediction'] = requests.get('http://localhost:5000/prediction', json=df_playlist.to_json()).json()
    # df_tracks['prediction'] = requests.get('http://localhost:5000/prediction', json=df_tracks.to_json()).json()
    # df_playlist['prediction'] = requests.get('https://wilts-model.herokuapp.com/prediction', json=df_playlist.to_json()).json()
    # df_tracks['prediction'] = requests.get('https://wilts-model.herokuapp.com/prediction', json=df_tracks.to_json()).json()
    df_playlist['prediction'] = requests.get('https://wilts-predict.azurewebsites.net/prediction', json=df_playlist.to_json()).json()
    df_tracks['prediction'] = requests.get('https://wilts-predict.azurewebsites.net/prediction', json=df_tracks.to_json()).json()
    thresh = 0.03
    liked_clusters = df_playlist['prediction'].value_counts()[
        df_playlist['prediction'].value_counts() >= thresh * len(df_playlist['prediction'])].index
    if df_tracks['prediction'].values[0] in liked_clusters:
        return True
    return False


# list_playlist_id=['2seEyHNHF6LiVzLRQjSwHn']
# track_ids=['3JEye8rsrvGdlrBvZUgNIL']
# print(comparaison(list_playlist_id, track_ids))
