import spotipy
import pandas as pd
from sentry_sdk import capture_exception
from spotipy.oauth2 import SpotifyClientCredentials
import requests

spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())


def extract_audio_feature(ids_list):
    """
    :param ids_list: List of track ids (max 100 ids, spotify API can not handle more)
    :return: List of feature of this tracks
    Take list of track id as parameter and return a list of their audio features
    """
    list_features = []
    try:
        list_features = spotify.audio_features(ids_list)
    except Exception as e:
        capture_exception(e)
    return list_features


def get_features(df):
    """
    :param df: Dataframe containing all the track ids
    :return: Dataframe containing the track ids with their audio features
    Given a dataframe, return a dataframe containing all the audio features ready for prediction
    """
    tracks_features_list = []
    total_tracks = df.shape[0]
    for tracks_nbr in range(0, total_tracks, 100):
        tracks_features_list += extract_audio_feature(','.join(df.track_id[tracks_nbr:tracks_nbr + 100]))
    remaining_tracks = total_tracks % 100
    if remaining_tracks:
        tracks_features_list += extract_audio_feature(','.join(df.track_id[-remaining_tracks:]))
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
    """
    :param list_playlist_id: List of playlists id
    :return: Dataframe containing the audio features for all the given playlists
    This dataframe is ready for prediction
    """
    tracks_data_list = []

    try:
        for playlist_id in list_playlist_id:
            track_results = spotify.playlist_items(playlist_id=playlist_id, additional_types=(['track']))
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
        capture_exception(e)
    df = pd.DataFrame(tracks_data_list)
    df.drop_duplicates(inplace=True)
    return get_features(df)


def predict_track(track_ids: list):
    """
    :param track_ids: List of track ids
    :return: Dataframe containing the audio features for all the given tracks
    This dataframe is ready for prediction
    """
    tracks_data_list = []

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
        capture_exception(e)
    df = pd.DataFrame(tracks_data_list)
    index = pd.Series([i for i in range(df.shape[0])], dtype=int)
    return get_features(df).set_index(index)


def comparaison(list_playlist_id, track_ids):
    """
    :param list_playlist_id: List of playlist ids
    :param track_ids: List of track ids
    :return: List of boolean containing if each track are similar to the given playlists
    """
    df_playlist = predict_playlist(list_playlist_id)
    df_tracks = predict_track(track_ids)
    # df_playlist['prediction'] = requests.get('http://localhost:5000/prediction', json=df_playlist.to_json()).json()
    # df_tracks['prediction'] = requests.get('http://localhost:5000/prediction', json=df_tracks.to_json()).json()
    # df_playlist['prediction'] = requests.get('https://wilts-model.herokuapp.com/prediction', json=df_playlist.to_json()).json()
    # df_tracks['prediction'] = requests.get('https://wilts-model.herokuapp.com/prediction', json=df_tracks.to_json()).json()
    df_playlist['prediction'] = requests.get('https://wilts-predict.azurewebsites.net/prediction', json=df_playlist.to_json()).json()
    df_tracks['prediction'] = requests.get('https://wilts-predict.azurewebsites.net/prediction', json=df_tracks.to_json()).json()
    thresh = 0.05
    liked_clusters = df_playlist['prediction'].value_counts()[
        df_playlist['prediction'].value_counts() >= thresh * len(df_playlist['prediction'])].index
    results = [cluster in liked_clusters for cluster in df_tracks['prediction'].values]
    return results

