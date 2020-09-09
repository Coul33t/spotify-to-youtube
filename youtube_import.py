import httplib2
import os
import sys

import isodate

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

class YoutubePlaylistImport:
    def __init__(self, playlist_name='Unnamed playlist',
                       playlist_description='No description provided',
                       playlist_visiblity='public'):

        self.playlist_name = playlist_name
        self.playlist_description = playlist_description
        self.playlist_visiblity = playlist_visiblity

        self.youtube = None

        self.playlist_id = None

        self.access_to_youtube()

    """
        See https://www.reddit.com/r/learnpython/comments/389yn0/google_python_youtube_playlist_api/
    """

    def access_to_youtube(self):
        CLIENT_SECRETS_FILE = "client_id.json"
        MISSING_CLIENT_SECRETS_MESSAGE ='WARNING: Please configure OAuth 2.0'

        # This OAuth 2.0 access scope allows for full read/write access to the
        # authenticated user's account.
        YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
        YOUTUBE_API_SERVICE_NAME = "youtube"
        YOUTUBE_API_VERSION = "v3"

        flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
                                    message=MISSING_CLIENT_SECRETS_MESSAGE,
                                    scope=YOUTUBE_READ_WRITE_SCOPE)

        storage = Storage("oauth2.json")
        credentials = storage.get()

        if credentials is None or credentials.invalid:
            flags = argparser.parse_args()
            credentials = run_flow(flow, storage, flags)

        self.youtube = build(YOUTUBE_API_SERVICE_NAME,
                        YOUTUBE_API_VERSION,
                        http=credentials.authorize(httplib2.Http()))

    def create_playlist(self):
        # This code creates a new, private playlist in the authorized user's channel.
        playlists_insert_response = self.youtube.playlists().insert(
        part="snippet,status",
        body=dict(
            snippet=dict(
            title=self.playlist_name,
            description=self.playlist_description
            ),
            status=dict(
            privacyStatus=self.playlist_visiblity
            )
        )
        ).execute()

        print(f"New playlist id: {playlists_insert_response['id']}")
        self.playlist_id = playlists_insert_response['id']

    def get_video(self, desired_video_info):
        print(f'Looking for {desired_video_info}...')
        # TODO: take care of musics longer than 59min 59s
        keywords = desired_video_info[:desired_video_info.find("(")-1].replace('[', '').replace(']', '')
        music_length = desired_video_info[desired_video_info.find("(")+1:desired_video_info.find(")")]
        music_length_sec = int(music_length[:music_length.find(':')]) * 60 + int(music_length[music_length.find(':')+1:])

        # TODO: try with
        # self.youtube.search().list(q=keywords, part='contentDetails', type='video', maxResults=3, pageToken=None)
        req = self.youtube.search().list(q=keywords, part='snippet', type='video', maxResults=3, pageToken=None)
        all_res = req.execute()

        closest_length = 999999
        closest_match = None

        for res in all_res['items']:
            req2 = self.youtube.videos().list(part='snippet,contentDetails', id=res['id']['videoId'])
            res2 = req2.execute()

            video_length_sec = int(isodate.parse_duration(res2['items'][0]['contentDetails']['duration']).total_seconds())

            difference = abs(music_length_sec - video_length_sec)

            if difference == 0:
                print(f"Found a video with same length: {res2['items'][0]['snippet']['title']}")
                return res2['items'][0]['id']

            elif closest_length > difference:
                closest_length = difference
                closest_match = res2

        print(f"Closest match found: {closest_match['items'][0]['snippet']['title']} ({closest_match['items'][0]['contentDetails']['duration']})")
        return closest_match['items'][0]['id']

    def add_video_to_playlist(self, video_id):
        add_video_request= self.youtube.playlistItems().insert(
        part="snippet",
        body={
                'snippet': {
                'playlistId': self.playlist_id, 
                'resourceId': {
                        'kind': 'youtube#video',
                    'videoId': video_id
                    }
                #'position': 0
                }
        }
        ).execute()

    def populate_playlist(self, filename):
        if self.playlist_id == None:
            print('ERROR: playlist ID is None.')
            return

        with open(filename, 'r', encoding='utf-8') as pl_file:
            songs = pl_file.readlines()
            for song in songs:
                song_id = self.get_video(song[:-1])
                self.add_video_to_playlist(song_id)

if __name__ == '__main__':
    filename = 'Suprem Kontin'
    yt_import = YoutubePlaylistImport(playlist_name=filename,
                       playlist_description='No description provided',
                       playlist_visiblity='public')
    yt_import.create_playlist()
    yt_import.populate_playlist(f'text_playlists/{filename}.txt')
    #yt_import.get_video("The Globalist [Muse] (10:00)")