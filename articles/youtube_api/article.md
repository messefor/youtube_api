YouTube API: 再生時間が条件に合う動画の再生リストを作成（1/2）

YouTubeで再生時間の条件で動画のプレイリストを作りたくなることありませんか？今回[YouTube Data API](https://developers.google.com/youtube/v3/getting-started?hl=ja)を使って再生時間が10分以上、15分以下の動画のみを含むプレイリスト作成するコードを書いたので共有します。長くなりそうなので、2回に分けて投稿します。



## 背景：YouTubeのフィルタが微妙

運動不足解消のため、毎朝妻と一緒に[B-life](https://www.youtube.com/channel/UCd0pUnH7i5CM-Y8xRe7cZVg)というYouTubeのヨガレッスンやっています。B-lifeのチャンネルには質の高いレッスン動画が多くアップロードされていて嬉しいのですが、毎朝やっているとその日やる動画を選ぶのも結構迷います。このとき「今日は時間がないので5分のレッスンが良い」という状況が頻繁にあるので、再生時間の条件でプレイリストが作れると便利です。

ただし残念ながらYouTubeの検索フィルタでは細かい再生時間の絞り込みはできなさそうです。



IMAGE

YouTube APIを使ったらできるだろうということでやってみました。

## 実現したかったこと

今回YouTube APIを使って実現したことをまとめると次の3つです。

1. 特定のチャンネル（B-life）の中にある動画ID一覧を取得する

2. 動画の再生時間を取得し、フィルタをかける

3. 自分のYouTubeアカウント上に該当する動画の再生リストを作成する



1と2に関しては、認証も必要なくAPIキーさえ用意すればOKで気軽に行えます。3にはOAuth認証が必要になります。上記手順を一つひとつ見ていきたいと思います。

## 0. 準備

### YouTubeチャンネルのIDを確認

APIで動画やチャンネルを指定するためには、それらのIDが必要です。準備として対象とするYouTubeチャンネルのIDを確認します。チャンネルIDはURLから直接分かります。YouTubeチャンネルのURL`https://www.youtube.com/channel/<チャンネルID>`となっているので、ブラウザでアクセスして確認します。

 ちなみにB-lifeのチャンネルIDは`UCd0pUnH7i5CM-Y8xRe7cZVg`でした。	



IMAGE

### ライブラリをインストール

pipでPythonのGoogle API Client、をインストールしておきましょう。あと`pandas`も使います。

```bash
pip install --upgrade google-api-python-client
```





## 1. チャンネルにある動画ID一覧を取得

YouTubeチャンネルの中にある動画ID一覧を取得していきます。



### APIのビルドと初期化

まずAPIの初期化を行います。Google APIを使うためには、APIキーが必要です。[Google Cloud Console](https://console.cloud.google.com/)から作成して、`YOUTUBE_API_KEY = 'your-api-key-here'`を作成したAPIキーに書き換えてください

```python
from googleapiclient.discovery import build

# 利用するAPIサービス
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

# APIキー
YOUTUBE_API_KEY = 'your-api-key-here'

# API のビルドと初期化
youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                developerKey=YOUTUBE_API_KEY)
```



### 動画情報一覧を取得

まず関数`get_video_list_in_channel()`を定義しています。 `get_video_list_in_channel()`はチャンネルIDを入力とし、動画情報を出力します。`search()`APIを使って、指定したチャンネルIDの中で公開日時が新しいものから50件ずつ最大2リクエストします。1日あたりのAPI使用量（クォータ）が限られているので引数`max_req_cnt=2`の部分で小さめに指定しています。

```python
from datetime import datetime, timedelta
import pandas as pd

        
def get_video_list_in_channel(youtube, channel_id, max_req_cnt=2):
    '''特定チャンネルの動画情報一覧を取得し、必要な動画情報を返す
    
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
        
        earliest_publishedtime = last_publishedtime_next.strftime('%Y-%m-%dT%H:%M:%SZ')

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

```

実行部分は以下です。`df_video_list`が取得した情報です。
`df_video_list`の`videoId`列が動画IDになります。動画ID一覧が取得できました。

```python
# 動画一覧を取得したいチャンネルID
channel_id = 'UCd0pUnH7i5CM-Y8xRe7cZVg'

# 動画一覧を取得
df_video_list = get_video_list_in_channel(youtube, channel_id)

# 出力
df_video_list
```



​	IMAGE



## 2. 動画の再生時間を取得し、フィルタをかける

上で取得した動画情報一覧に動画の再生時間は含まれていませんので、別途APIを使って取得する必要があります。再生時間を取得した後は`pandas`で条件に合ったものを絞り込むだけです。

### 再生時間を取得

再生時間を取得するには`video()`APIに動画IDを渡して詳細情報を取得します。いくつかラッパー関数を定義しています。

| 関数                                              | 機能概要                   |
| ------------------------------------------------- | -------------------------- |
| get_contents_detail(), get_contents_detail_core() | 動画の詳細情報取得         |
| get_duration(), get_basicinfo(),                  | レスポンスjsonのパース     |
| pt2sec()                                          | 再生時間のフォーマット変換 |

1回のリクエストで50動画IDまでしか問い合わせできないみたいなので、`get_contents_detail()`では動画ID一覧を50件ずつに分割してから処理しています。

```python
import re
import numpy as np

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
        df_video_details_part = get_contents_detail_core(youtube, vids.tolist())
        details_list.append(df_video_details_part)

    df_video_details = pd.concat(details_list, axis=0).reset_index(drop=True)
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
```

再生時間取得の実行部分です。`df_video_details`が結果で、`duration`カラムに再生時間が入っています。再生時間の単位は秒です。

```python
# 動画ID
videoids = df_video_list['videoId'].values

# 動画の詳細情報を取得
df_video_details = get_contents_detail(youtube, videoids)

df_video_details.head()
```

IMAGE

### 再生時間でフィルタをかける

ここでは`pandas.between()`を使って10分以上15分以下の動画に絞り込みこみました。

```python
# 再生時間が10分以上、15分以下の動画に絞り込む
lower_duration = 10 * 60  # 10分以上
upper_duration = 15 * 60  # 15分以下
is_match_cond = df_video_details['duration'].between(lower_duration, upper_duration)

df_video_playlist = df_video_details.loc[is_match_cond, :]

# 出力
df_video_playlist.head()
```

これで10分以上、15分以下の動画IDのリストができましたので、次回はプレイリストをAPI経由で生成したいと思います。



----

久々にGoogle APIを触りました。サービスも年々増えているみたいで、やりさえすれば色々楽しめそうです。やりさえすれば。。。日々精進