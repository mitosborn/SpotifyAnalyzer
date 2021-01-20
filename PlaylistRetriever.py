from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import pandas as pd
import time



def __get_audio_features(track_ids, sp, tracks_per_call=100):
    begin = 0
    end = min(tracks_per_call, len(track_ids))
    remaining = len(track_ids)
    data = list()
    while remaining > 0:
        data += sp.audio_features(tracks=track_ids[begin:end])
        remaining -= (end - begin)
        begin = end
        end += min(tracks_per_call, remaining)
    return pd.DataFrame.from_dict(data)[['danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
                                         'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'id']]

# Returns the id, popularity, and name of all songs within a playlist
def __get_track_info(playlist_id, sp):
    # Get song ids from album
    response = sp.playlist(playlist_id,
                           fields='tracks.items.track.album.release_date, tracks.items.track.id, tracks.items.track.name, tracks.items.track.album.name, tracks.items.track.artists.name,tracks.items.track.popularity,name')
    data = list(map(lambda x: x['track'], response['tracks']['items']))
    #print(data[2])
    dataframe = pd.DataFrame(data)
    dataframe['playlist'] = response['name']
    dataframe['year'] = dataframe['album'].apply(lambda x: x['release_date'][:4])
    dataframe['album'] = dataframe['album'].apply(lambda x: x['name'])
    dataframe['artists'] = dataframe['artists'].apply(lambda x: list(map(lambda y: y['name'], x)))

    return dataframe


def get_user_playlists(playlist_ids):
    sp = spotipy.Spotify(
        client_credentials_manager=SpotifyClientCredentials(client_id="e014b57873a64cf6bcae2e75f096f0d7",
                                                            client_secret="463ff7b476934c5c874fcfc64ccb8d85"))
    playlists = list()
    for playlist_id in playlist_ids:
        # Ensure id is in proper format

        # Get song ids, popularity, and names from album
        info = __get_track_info(playlist_id, sp)

        # Create df from audio features and popularity of songs
        merged_df = pd.merge(__get_audio_features(info['id'], sp), info, on='id')

        # Append to master_df
        playlists.append(merged_df)
    return pd.DataFrame().append(playlists)

# s = time.time()
# x = Retriever()
# data = x.get_user_playlists(
#     ['spotify:playlist:28mI8s2FBTx0pzWfQ7dTwA', '7s5PGUSUudnrdcueQuxWW0', 'spotify:playlist:6wObnEPQ63a4kei1sEcMdH'])
# print(time.time() - s)
