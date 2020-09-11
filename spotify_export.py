# Core library import
import os
import json

# External library imports
import spotipy
import spotipy.oauth2 as oauth2

# Personal imports
from spotify_info import CLIENT_ID, CLIENT_SECRET
from tools import ms_to_min_sec_text

class SpotifyPlaylistExport:
    def __init__(self):
        self.token = None
        self.spotify = None
        self.tracks_with_metadata = []

        self.access_to_spotify()

    def generate_token(self):
        """ Generate the token. Please respect these credentials :) """
        credentials = oauth2.SpotifyClientCredentials(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET)
        self.token = credentials.get_access_token()

    def access_to_spotify(self):
        self.generate_token()
        self.spotify = spotipy.Spotify(auth=self.token)

    def get_playlist_tracks(self, username,playlist_id):
        results = self.spotify.user_playlist(username, playlist_id, fields='tracks, next, name')
        results = results['tracks']
        self.tracks_with_metadata = results['items']

        while results['next']:
            results = self.spotify.next(results)
            self.tracks_with_metadata.extend(results['items'])

    def format_tracks_to_text(self):
        formated_tracks = []

        for track in self.tracks_with_metadata:
            track = track['track']
            artists = [x['name'] for x in track['artists']]
            artists = ", ".join(artists)
            formated_tracks.append(f"{track['name']} [{artists}] ({int(track['duration_ms'] / 1000)})")

        return formated_tracks

    def format_tracks_to_json(self):
        formated_tracks = []

        for track in self.tracks_with_metadata:
            track = track['track']
            artists = [x['name'] for x in track['artists']]
            artists = ", ".join(artists)

            formated_tracks.append({'title': track['name'], 'artist': artists, 'duration': int(track['duration_ms'] / 1000), 'Spotify id': track['id']})

        return formated_tracks

    def export_to_text_file(self, filename="tracks.txt"):
        formatted_tracks = self.format_tracks_to_text()

        if '.txt' not in filename:
            filename += '.txt'

        if not os.path.exists('text_playlists'):
            os.makedirs('text_playlists')

        with open('text_playlists/' + filename, 'w', encoding='utf-8') as output_file:
            for track in formatted_tracks:
                output_file.write(f'{track}\n')

    def export_to_json_file(self, filename='tracks.json'):
        formatted_tracks = self.format_tracks_to_json()

        if '.json' not in filename:
            filename += '.json'

        if not os.path.exists('text_playlists'):
            os.makedirs('text_playlists')

        with open('text_playlists/' + filename, 'w', encoding='utf-8') as output_file:
            json.dump(formatted_tracks, output_file, indent=4)


if __name__ == '__main__':
    spot = SpotifyPlaylistExport()
    spot.get_playlist_tracks('Coulis', 'spotify:playlist:3R2EyheKQiUeqoV3VyoTI4')
    spot.export_to_json_file('Suprem Kontin')
