YouTube API: 再生時間が条件に合う動画を選んで再生リストを作成（2/2）

[前回](https://messefor.hatenablog.com/entry/2020/10/04/001645)は[B-life](https://www.youtube.com/channel/UCd0pUnH7i5CM-Y8xRe7cZVg)のYouTubeチャンネルを題材に、チャンネル中にある動画情報一覧および再生時間を取得し、再生時間が10分以上15分以下の条件に収まる動画のみに絞り込みを行いました。本投稿では、これら動画を使って再生リストを作成します。



前回掲載した全ステップの中のでいうと**本投稿はステップ3を説明します**。

1. 特定のチャンネル（B-life）の中にある動画ID一覧を取得する

2. 動画の再生時間を取得し、再生時間で絞り込む

3. **自分のYouTubeアカウント上に該当する動画の再生リストを作成する**

   0. 準備
   1. OAuth認証とAPIのビルド
   2. 再生リストの作成と動画の追加

   

## 0.準備

### APIの認証情報について

前回`search`APIを使うにはAPIキーさえあれば良かったですが、API経由でYouTube再生リストを作成するにはOAuth 2.0 クライアントクレデンシャルが必要です。これはYouTube再生リストは各ユーザーが作成・保持するもので、ユーザデータへのアクセスが必要になるためです。OAuth2.0認証はユーザーデータへ安全にアクセスできるよう、許可する権限範囲など細かに指定できる仕組みを提供します。

今回具体的に必要なものは、クライアントクレデンシャル情報が書き込まれた`.json`ファイルです。[Google API Console](https://console.developers.google.com/)で作成してダウンロードしておきます。



### 認証用ライブラリのインストール

認証部分は[Googleのドキュメント：quickstart.py](https://developers.google.com/drive/api/v3/quickstart/python#step_3_set_up_the_sample)にあるコードの丸パクリですが、このサンプルコードが`google_auth_oauthlib`を使っているのでインストールしておきます。

```bash
pip google-auth-oauthlib
```



## 1. OAuth認証とAPIのビルド

OAuth認証の処理部分は以下の`get_credentials`関数で行います。引数`token_storage_pkl`で指定された場所に有効なトークンがなければ、ユーザにログイン（OAuth認証処理）をしてもらい、データへのアクセスを許可してもらいます。ユーザの許可により有効なトークンが得られれば、次回以降のアクセスのためにそれを`token_storage_pkl`にpickleとして保存します。

```python
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
```

実行部分のコードは以下です。`YOUTUBE_READ_WRITE_SCOPE`がOAuth認証で使われるスコープになります。今回はYouTubeアカウントの管理権限（全読み書き）を範囲にしていますが、[OAuth 2.0 Scopes for Google APIs](https://developers.google.com/identity/protocols/oauth2/scopes#youtube)を見て、適宜必要な最小限のスコープを絞ってください。

```python
'''OAuth認証とAPIのビルド実行'''

# 利用するAPIサービス
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

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


>>> 
# 出力されるメッセージ
Please visit this URL to authorize this application: https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=hoge.apps.googleusercontent.com&redirect_uri=http%3A%2F%2Flocalhost%3A54887%2F&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fyoutube&state=hoge&access_type=offline
```

このコードを実行すると、`token_storage_pkl`で指定された場所に有効なトークンがない場合、ブラウザが立ち上がって以下のようなGoolge ユーザログイン画面が表示されます。（ブラウザが立ち上がらない場合は、出力されるメッセージに含まれるURLをクリックして、OAuth認証を行ってください）

<img src="/Users/daisuke/Library/Application Support/typora-user-images/image-20201004101204483.png" alt="image-20201004101204483" style="zoom:25%;" />

さらに警告画面が表示されますが、実験なので無視して`詳細 >（安全でないページ）に移動`と遷移すると

<img src="/Users/daisuke/Library/Application Support/typora-user-images/image-20201004102602338.png" alt="image-20201004102602338" style="zoom:25%;" />

YouTubeアカウントの管理権限を許可するかどうか聞かれますので、`許可`を選択します。

<img src="/Users/daisuke/Library/Application Support/typora-user-images/image-20201004102800373.png" alt="image-20201004102800373" style="zoom:25%;" />

再度確認されるので、`許可`を押します。

<img src="/Users/daisuke/Library/Application Support/typora-user-images/image-20201004103004696.png" alt="image-20201004103004696" style="zoom:25%;" />

これでユーザ側のOAuth認証許可の処理が完了になります。これでAPI経由で再生リストを作成するための権限が与えられました。次は実際に再生リストを作成して、動画を追加します。

## 2. 再生リストの作成と動画の追加

### 新規再生リストの作成

まず新規再生リストを追加します。タイトルと説明、再生リストを公開にするか限定するかを指定しています。

```python
'''新規再生リストの作成'''

title = 'B-life Test 10分〜15分'
description = '再生時間が10分〜15分の動画の再生リスト'
privacy_status = 'public'  # 'private'

# 新規再生リストを追加
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
```



これを実行して、YouTubeサイトに行って自分のライブラリを確認すると`B-life Test 10分〜15分 `という再生リストが作成されています。



<img src="/Users/daisuke/Library/Application Support/typora-user-images/image-20201004111724521.png" alt="image-20201004111724521" style="zoom:25%;" />



まだ動画は一本も含まれていないので、クリックしても「この再生リストには動画がありません」と表示されます。

![image-20201004111608479](/Users/daisuke/Library/Application Support/typora-user-images/image-20201004111608479.png)

### 再生リストへの動画の追加

追加する動画は、[前回](https://messefor.hatenablog.com/entry/2020/10/04/001645)は作成した動画IDリストとします。`df_video_playlist`データフレームの`id`カラムに動画IDが格納されています。また、追加先となる再生リストのIDは新規再生リストの作成時のレスポンスとして取得できていますので、それを利用します。

```python
'''再生リストへの動画の追加 '''

# 動画ID
videoids = df_video_playlist['id'].values

# example videodis
# 前回の続きとして実行しない場合は以下のコメントを外す
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
```

先程の再生リストを見ると10分〜15分の動画が追加されているのが分かります。良かった。

<img src="/Users/daisuke/Library/Application Support/typora-user-images/image-20201004114428855.png" alt="image-20201004114428855" style="zoom:25%;" />

