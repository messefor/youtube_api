'''YouTube API: 再生時間が条件に合う動画を選んで再生リストを作成

https://messefor.hatenablog.com/entry/2020/10/04/001645


'''

import os
import re
import pickle
from datetime import datetime, timedelta, timezone
import toml

import numpy as np
import pandas as pd

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


def get_video_list_in_channel(youtube, channel_id, max_req_cnt=2):
    '''特定のチャンネルの動画情報を取得し、必要な動画情報を返す

        公開時刻が新しい順に50ずつリクエスト
        デフォルトでは最大2リクエストで終了
    '''

    n_requested = 50

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

        # 取得動画の最も遅い公開日時の1秒前以前を次の動画一覧の取得条件とする
        last_publishedtime = video_info['publishTime'].min()
        last_publishedtime_next =\
            datetime.strptime(last_publishedtime, '%Y-%m-%dT%H:%M:%SZ') - timedelta(seconds=1)

        earliest_publishedtime =\
            last_publishedtime_next.strftime('%Y-%m-%dT%H:%M:%SZ')

        if req_cnt > max_req_cnt:
            # リクエスト回数がmax_req_cntを超えたらループを抜ける
            print('Result count exceeded max count {}.'.format(max_req_cnt))
            break

        if len(response['items']) < n_requested:
            # リクエストした動画数より少ない数が返った場合はループを抜ける
            print('Number of results are less than {}.'.format(n_requested))
            break

    if len(result) > 1:
        df_video_list = pd.concat(result, axis=0).reset_index(drop=True)
    else:
        df_video_list = result[0]

    return df_video_list


def fetch_video_info(response, as_df=True):
    '''APIのレスポンスから必要な動画情報を抜き出す'''
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


def get_contents_detail_core(youtube, videoids):
    '''動画の詳細情報を取得'''
    part = ['snippet', 'contentDetails']
    response = youtube.videos().list(part=part, id=videoids).execute()
    results = []
    for item in response['items']:
        info = get_basicinfo(item)
        info['duration'] = get_duration(item)
        results.append(info)
    return pd.DataFrame(results)


def get_contents_detail(youtube, videoids):
    '''必要に応じて50件ずつにIDを分割し、詳細情報を取得'''
    n_req_pre_once = 50

    # IDの数が多い場合は50件ずつ動画IDのリストを作成
    if len(videoids) > n_req_pre_once:
        videoids_list = np.array_split(videoids, len(videoids) // n_req_pre_once + 1)
    else:
        videoids_list = [videoids,]

    # 50件ずつ動画IDのリストを渡し、動画の詳細情報を取得
    details_list = []
    for vids in videoids_list:
        df_video_details_part =\
            get_contents_detail_core(youtube, vids.tolist())
        details_list.append(df_video_details_part)

    df_video_details =\
        pd.concat(details_list, axis=0).reset_index(drop=True)
    return df_video_details


def get_duration(item):
    '''動画時間を抜き出す（ISO表記を秒に変換）'''
    content_details = item['contentDetails']
    pt_time = content_details['duration']
    return pt2sec(pt_time)


def get_basicinfo(item):
    '''動画の基本情報の抜き出し'''
    basicinfo = dict(id=item['id'])
    # snippets
    keys = ('title', 'description', 'channelTitle')
    snippets = {k: item['snippet'][k] for k in keys}
    basicinfo.update(snippets)
    return basicinfo


def pt2sec(pt_time):
    '''ISO表記の動画時間を秒に変換 '''
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


def get_credentials(client_secret_file, scopes,
                    token_storage_pkl='token.pickle'):
    '''google_auth_oauthlibを利用してOAuth2認証

        下記URLのコードをほぼそのまま利用。Apache 2.0
        https://developers.google.com/drive/api/v3/quickstart/python#step_1_turn_on_the_api_name
    '''
    creds = None
    # token.pickleファイルにユーザのアクセス情報とトークンが保存される
    # ファイルは初回の認証フローで自動的に作成される
    if os.path.exists(token_storage_pkl):
        with open(token_storage_pkl, 'rb') as token:
            creds = pickle.load(token)

    # 有効なクレデンシャルがなければ、ユーザーにログインしてもらう
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secret_file, scopes=scopes)
            creds = flow.run_local_server(port=0)

        # クレデンシャルを保存（次回以降の認証のため）
        with open(token_storage_pkl, 'wb') as token:
            pickle.dump(creds, token)

    return creds


def main():

    # 利用するAPIサービス
    YOUTUBE_API_SERVICE_NAME = 'youtube'
    YOUTUBE_API_VERSION = 'v3'

    # APIキー
    credential_dir = 'config'
    apikey_path = os.path.join(credential_dir, 'youtube_v3_api.toml')


    # Set Youtube APIKEY
    if os.path.exists(apikey_path):
        config = toml.load(apikey_path)
        YOUTUBE_API_KEY = config['YOUTUBE_API_KEY']
    else:
        YOUTUBE_API_KEY = 'Your-API-KEY-here'

    # API のビルドと初期化
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                developerKey=YOUTUBE_API_KEY)

    # B-life channel ID
    channel_id = 'UCd0pUnH7i5CM-Y8xRe7cZVg'

    df_video_list = get_video_list_in_channel(youtube, channel_id)


    # 動画ID
    videoids = df_video_list['videoId'].values

    # 動画の詳細情報を取得
    df_video_details = get_contents_detail(youtube, videoids)


    # 再生時間が10分以上、15分以下の動画に絞り込む
    lower_duration = 10 * 60  # 10分以上
    upper_duration = 15 * 60  # 15分以下
    is_match_cond =\
        df_video_details['duration'].between(lower_duration, upper_duration)

    df_video_playlist = df_video_details.loc[is_match_cond, :]

    # 出力
    # df_video_playlist.head()

    print('videoids to be added:', df_video_playlist['id'].values)


    '''OAuth認証とAPIのビルド実行'''

    # OAuthのスコープとクレデンシャルファイル
    YOUTUBE_READ_WRITE_SCOPE = 'https://www.googleapis.com/auth/youtube'
    CLIENT_SECRET_FILE = 'config/client_secret.json'

    # OAuth認証：クレデンシャルを作成
    creds = get_credentials(
                        client_secret_file=CLIENT_SECRET_FILE,
                        scopes=YOUTUBE_READ_WRITE_SCOPE
                        )

    # API のビルドと初期化
    youtube_auth = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                        credentials=creds)


    '''新規再生リストの作成'''

    title = 'B-life Test 10分〜15分'
    description = '再生時間が10分〜15分の動画のプレイリスト'
    privacy_status = 'public'

    # 新規プレイリストを追加
    # https://developers.google.com/youtube/v3/docs/playlists/insert
    playlists_insert_response = youtube_auth.playlists().insert(
      part="snippet, status",
      body=dict(
        snippet=dict(
          title=title,
          description=description
        ),
        status=dict(
          privacyStatus=privacy_status
        )
      )
    ).execute()

    '''再生リストへの動画の追加 '''

    # 動画ID
    videoids = df_video_playlist['id'].values

    # videoids = ['nZSe3ZZUSJw', 'EYqPH91q5nE', 'Zw_osQctQKs', 'kBLCmz8pODg',
    #             'IBt5l9Um_rY', 'WWxKW8ncPe0', 'CmWJJWKLeKg', 'e9HR7-3I3MA',]

    # プレイリストに動画を追加
    # https://stackoverflow.com/questions/20650415/insert-video-into-a-playlist-with-youtube-api-v3/22190766

    playlistid = playlists_insert_response['id']  # 作成した再生リストのIDを取得

    # 動画IDをループ
    for videoid in videoids:

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
    print('Done.')