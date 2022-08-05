import pytest
from prediction import predict


def test_valid_comparaison():
    playlists_id = ['https://open.spotify.com/playlist/7plzYiCWpsJlK46zrNKZIf']
    tracks_id = ['https://open.spotify.com/track/3JEye8rsrvGdlrBvZUgNIL?si=b1919f56af994064&nd=1']
    comparaison = predict.comparaison(playlists_id, tracks_id)
    assert type(comparaison) == list
    for comp in comparaison:
        assert(type(comp)) == bool


def test_invalid_playlist_comparaison():
    with pytest.raises(KeyError):
        playlists_id = ['abc']
        tracks_id = ['https://open.spotify.com/track/3JEye8rsrvGdlrBvZUgNIL?si=b1919f56af994064&nd=1']
        predict.comparaison(playlists_id, tracks_id)

def test_invalid_track_comparaison():
    with pytest.raises(KeyError):
        playlists_id = ['https://open.spotify.com/playlist/7plzYiCWpsJlK46zrNKZIf']
        tracks_id = ['abc']
        predict.comparaison(playlists_id, tracks_id)

