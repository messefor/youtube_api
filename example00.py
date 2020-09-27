'''


【Google API Console】クライアントID・クライアントシークレットを取得する
https://qiita.com/pasaremon/items/df461947344bb76ee25f

'''

import os
import sys

import re
import toml
from datetime import datetime, timedelta, timezone

import httplib2
import toml
import pandas as pd

from googleapiclient.discovery import build

from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage


def get_credentials(credential_store_path):
    flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE,
                                    scope=YOUTUBE_READ_WRITE_SCOPE)
    storage = Storage(credential_store_path)
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        flags = tools.argparser.parse_args()
        credentials = tools.run_flow(flow, storage, flags)
    return credentials


def pt2sec(pt_time):
    pttn_time = re.compile(r'PT(\d+H)?(\d+M)?(\d+S)?')
    keys = ['hours', 'minutes', 'seconds']
    m = pttn_time.search(pt_time)
    if m:
        kwargs = {k: 0 if v is None else int(v[:-1])
                    for k, v in zip(keys, m.groups())}
        return timedelta(**kwargs).total_seconds()
    else:
        msg = '{} is not valid ISO time format.'.format(pt_time)
        raise ValueError(msg)


def get_duration(item):
    content_details = item['contentDetails']
    pt_time = content_details['duration']
    return pt2sec(pt_time)


def get_basicinfo(item):
    basicinfo = dict(id=item['id'])
    # snippets
    keys = ('title', 'description', 'channelTitle')
    snippets = {k: item['snippet'][k] for k in keys}
    basicinfo.update(snippets)
    return basicinfo


def fetch_video_info(response, as_df=True):
    info_list = []
    for item in response['items']:
        info = {}
        info['title'] = item['snippet']['title']
        info['kind'] = item['id']['kind']
        info['videoId'] = item['id']['videoId']
        info['description'] = item['snippet']['description']
        info['publishTime'] = item['snippet']['publishTime']
        info['channelTitle'] = item['snippet']['channelTitle']
        info['thumbnails_url'] = item['snippet']['thumbnails']['default']['url']
        info_list.append(info)
    if as_df:
        return pd.DataFrame(info_list)
    else:
        info_list


def get_video_list_in_channel(youtube, channel_id):

    n_requested = 50
    max_req_cnt = 2

    earliest_publishedtime =\
        datetime.now(tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    req_cnt = 0
    result = []
    while True:
        response = youtube.search().list(part='snippet',
                                        channelId=channel_id,
                                        order='date',
                                        type='video',
                                        publishedBefore=earliest_publishedtime,
                                        maxResults=n_requested).execute()
        req_cnt += 1
        video_info = fetch_video_info(response)
        result.append(video_info)
        earliest_publishedtime = video_info['publishTime'].min()
        print(response['pageInfo'])

        if req_cnt > max_req_cnt:
            print('Result count exceeded max count {}.'.format(max_req_cnt))
            break

        if len(response['items']) < n_requested:
            print('Number of results are less than {}.'.format(n_requested))
            break

    if len(result) > 1:
        df_video_list = pd.concat(result, axis=0)
    else:
        df_video_list = result[0]

    return df_video_list


def get_contents_detail(youtube, videoids):
    part = ['snippet', 'contentDetails']
    response = youtube.videos().list(part=part, id=videoids).execute()
    results = []
    for item in response['items']:
        info = get_basicinfo(item)
        info['duration'] = get_duration(item)
        results.append(info)
    return pd.DataFrame(results)


def main():

    # --------------------------------------------------------------------
    # API Access
    # --------------------------------------------------------------------

    YOUTUBE_READ_WRITE_SCOPE = 'https://www.googleapis.com/auth/youtube'
    YOUTUBE_API_SERVICE_NAME = 'youtube'
    YOUTUBE_API_VERSION = 'v3'

    CLIENT_SECRET_FILE = 'config/client_secret.json'
    APPLICATION_NAME = 'youtube-api'

    # B-life channel ID
    channel_id = 'UCd0pUnH7i5CM-Y8xRe7cZVg'


    credential_dir = 'config'
    credential_path = os.path.join(credential_dir, 'google_drive.json')
    apikey_path = os.path.join(credential_dir, 'youtube_v3_api.toml')


    # Set Youtube APIKEY
    if os.path.exists(apikey_path):
        config = toml.load(apikey_path)
        YOUTUBE_API_KEY = config['YOUTUBE_API_KEY']
    else:
        YOUTUBE_API_KEY = 'Your-API-KEY-here'

    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    developerKey=YOUTUBE_API_KEY)


    # --------------------------------------------------------------------
    # Get video ids list in the chennel
    # --------------------------------------------------------------------

    df_video_list = get_video_list_in_channel(youtube, channel_id)

    df_video_list.shape

    csv_path = 'df_video.csv'
    # df_video_list.to_csv(csv_path)
    df_video = pd.read_csv(csv_path)

    # --------------------------------------------------------------------
    # Request contents details of video ids
    # --------------------------------------------------------------------


    # Because movies are duplicated when on the edge of time range
    # make them unique
    videoids = list(df_video_list['videoId'].unique())
    max_req_cnt = 50
    videoids_req = videoids[:max_req_cnt]

    df_video_details = get_contents_detail(youtube, videoids_req)


    # --------------------------------------------------------------------
    # Build Playlist consist of videos that matches condition
    # --------------------------------------------------------------------

    is_match_cond = df_video_details['duration'].between(10 * 60, 15 * 60)
    df_video_playlist = df_video_details.loc[is_match_cond, :]

    # videoid = df_video_playlist['id'].iloc[0]

    credential_store_path = os.path.join(credential_dir, 'google_drive.json')


    credentials = get_credentials(credential_store_path)

    youtube_auth = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    http=credentials.authorize(httplib2.Http()))

    # Add Playlist
    # This code creates a new, private playlist in the authorized user's channel.
    playlists_insert_response = youtube_auth.playlists().insert(
      part="snippet,status",
      body=dict(
        snippet=dict(
          title='B-Lifeプレイリスト Test',
          description='再生時間が10分〜15分'
        ),
        status=dict(
          privacyStatus="private"
        )
      )
    ).execute()


    videoids = df_video_playlist['id'].iloc[1:50].values

    # Add video into Playlist
    # insert video into a playlist with youtube api v3
    # https://stackoverflow.com/questions/20650415/insert-video-into-a-playlist-with-youtube-api-v3/22190766

    for videoid in videoids:

        playlistid = playlists_insert_response['id']
        resourceid = dict(kind='youtube#video',
                          videoId=videoid)

        response = youtube_auth.playlistItems().insert(
                    part='snippet',
                      body=dict(
                        snippet=dict(
                          playlistId=playlistid,
                          resourceId=resourceid
                          )
                       )
                ).execute()

if __name__ == '__main__':
    main()
