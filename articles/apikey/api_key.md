Google APIs: APIキーとOAuth2.0 クライアントID、サービスアカウントキー

GoogleのサービスをAPI経由で利用する際、大きく3つの認証情報が登場します。「APIキー」、「OAuth2.0クライアントID」、「サービスアカウントキー」です。本投稿ではこれらの用途をざっくりと整理し、取得方法を説明します。正確に理解していない可能性がありますので、間違っていたら教えて下さい。





# まとめ

* Google APIsを使うには、下表の3ついずれかの認証情報が必要です
* APIで**どういうデータ**に、**どういう形でアクセスするか**に依って使うべき認証情報が異なります
* いずれの認証情報も[Google Cloud Console](https://console.cloud.google.com/)の `APIとサービス > 認証情報`から作成することができます
  * Googleアカウントが無い方は、まずGoogleアカウントを作成し、Google Cloud Consoleでプロジェクト作成が必要です

| #    | 必要となるもの         | アクセス可能なデータ          | 誰としてアクセスするか | 具体例                                                       |
| ---- | ---------------------- | ----------------------------- | ---------------------- | ------------------------------------------------------------ |
| 1    | APIキー                | 一般公開データ                | 匿名ユーザ             | YouTubeにある動画をアプリケーション経由で検索する            |
| 2    | OAuth2.0クライアトID   | 一般公開データ/ユーザーデータ | ユーザアカウント       | あるユーザ（エンドユーザ）の代わりにユーザのGoogleドライブにアプリケーションを経由でデータを保存 |
| 3    | サービスアカウントキー | 一般公開データ/ユーザーデータ | サービスアカウント     | 共同作業メンバのGoogleカレンダー情報にアプリケーションを経由してアクセスする |



## 基本事項のおさらい

認証情報について理解する上で知っておいたほうが良い基本事項についてまとめます。必要ない方は飛ばしてください。

### APIの性質

 API（Application Programming Interface）はサービスを外部のプログラムやアプリケーションから利用できるようにした窓口です。例えば、Google MapはGoogleのサービスの一つで、普通私たちユーザはブラウザやGoogle Map Appを自分で操作してGoogle Mapを利用します。一方で自身が開発するアプリの中でGoogle Map機能の一部を利用したい場合は、アプリの中のプログラムを介してGoogle Map機能を操作する必要があります。ここで利用されるのがAPIというプログラムから呼び出すインターフェースです。

一般に**APIはプログラムやアプリケーションから利用されます**。



### 認証情報の役割

Google は許可されたアプリケーションからしかAPI利用をさせてくれません。そのため我々API利用者はGoogleアカウントを作成し、[Google Cloud Console]()内でAPIを利用するアプリケーションの登録を行う必要があります。

つまり**どの開発者が登録した、どのアプリケーションがAPIを叩いているのかをGoolge様にお知らせするのがAPIキーやOAuth2.0クライアトIDなど認証情報の役割の一つ**です。

またAPI利用は使用量の無料枠上限を超えると課金が発生します。**API利用がどのアプリでどの程度発生しているかをGoogle様にお知らせする**のも認証情報の役割です。課金管理はプロジェクト単位で行われるため**認証情報はGoogleアカウント内のプロジェクトと紐付ける必要があります**。これが認証情報を作成する際にプロジェクトが必要な理由です。



### 3つの認証情報は想定される利用シーンが異なる

APIキー、OAuth2.0クライアントID、サービスアカウントキーの3種類のいずれかがあればAPIを使うことが可能です。ただし三者は用途が異なり、用途にあった認証情報を選択するのが自然です。たとえば一般公開データにしかアクセスしないのに、OAuthクライアントIDを使う必要はありません。用途に応じた必要最低限の認証情報を使います。

以上を踏まえて３つの認証情報をそれぞれ見ていきましょう。



## 1. APIキー

まずはAPIキーについてです。[Google Cloud ドキュメント：API キーの使用](https://cloud.google.com/docs/authentication/api-keys?hl=ja)には次のように説明されています。

> API キーは、[プリンシパル](https://cloud.google.com/docs/authentication?hl=ja#principals)なしでアプリケーションを識別する暗号化された単純な文字列です。一般公開データに匿名でアクセスする場合に便利で、割り当てや課金のために API リクエストをプロジェクトに関連付けるために使用されます。

YouTubeでの検索機能のように一般公開データにのみアクセスできれば十分な場合、利用者にユーザアカウントでログインしてもらうような必要はありません。このようなケースではAPIキーを使ってAPIを利用します。APIキーは暗号化された単純な文字列で、作成も取り扱いも比較的簡単です。

### 取得方法

事前にGoogle Cloud アカウント作成とプロジェクト作成が必要です。まだな方は[ココ]()を参考にしてください。
プロジェクト作成が完了したら次の手順でAPIキーを作成します。



#### 1. プロジェクトを選択

[Google Cloud Console]()にログインして、APIを利用するプロジェクトを選択します。



<img src="/Users/daisuke/prj/900_analysis/youtube_api/src/APIキー01.png" alt="APIキー01" style="zoom:25%;" />



APIとサービス > 認証情報

<img src="/Users/daisuke/prj/900_analysis/youtube_api/src/APIキー02.png" alt="APIキー02" style="zoom:25%;" />



<img src="/Users/daisuke/prj/900_analysis/youtube_api/src/APIキー03.png" alt="APIキー03" style="zoom:25%;" />

#### 2. APIキーの作成

「認証情報の作成」をクリック

<img src="/Users/daisuke/prj/900_analysis/youtube_api/src/APIキー04.png" alt="APIキー04" style="zoom:25%;" />



「APIキー」を選択

<img src="/Users/daisuke/prj/900_analysis/youtube_api/src/APIキー05.png" alt="APIキー05" style="zoom:25%;" />

APIキーが表示されたボックスの右側にあるコピーマークをクリックし、閉じる

<img src="/Users/daisuke/prj/900_analysis/youtube_api/src/APIキー06.png" alt="APIキー06" style="zoom:25%;" />

#### 3. キーで利用するAPIを制限する（オプショナル）

作成直後の状態ではすべてのAPIの利用が可能となっているので、利用したいAPIのみに制限します

作成したAPIキーを選択

<img src="/Users/daisuke/prj/900_analysis/youtube_api/src/APIキー07.png" alt="APIキー07" style="zoom: 33%;" />

APIの制限 > キーを制限

<img src="/Users/daisuke/prj/900_analysis/youtube_api/src/APIキー08.png" alt="APIキー08" style="zoom:25%;" />





### Pythonでの利用例

例として、PythonからAPIキーを使ってYouTubeのsearchAPIを使うサンプルコードを掲載します。

```python
from googleapiclient.discovery import build

# 利用するAPIサービス
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

# APIキーを指定
YOUTUBE_API_KEY = 'Your-API-KEY-here'

# API のビルドと初期化
youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
            developerKey=YOUTUBE_API_KEY)

# YouTubeでキーワード検索（視聴数の多い順）
q = 'Overjoyed'
response = youtube.search().list(part='snippet',
                                q=q,
                                order='viewCount',
                                type='video',).execute()

response
>>>  # 出力
{'etag': 'QvSya4g44W8aUkApKibFr-o5JqA',
 'items': [{'etag': 'Jw9SPInmYcoJg21LlKvbdDhk1IU',
            'id': {'kind': 'youtube#video', 'videoId': '_a1LogyX9Uw'},
            'kind': 'youtube#searchResult',
            'snippet': {'channelId': 'UCOo4Oc-PYSrzEeappVyoM-Q',
                        'channelTitle': 'beechoppers',
                        'description': 'please enjoy the music! music and '
                                       'lyrics by stevie wonder clip design by '
                                       'R. Norton.',
                        'liveBroadcastContent': 'none',
```





## 2.OAuth2.0クライントID

アプリ経由で利用者のGoogleドライブにファイルを保存をする場合など、アプリケーションがエンドユーザーに代わって Google Cloud APIs にアクセスします。このケースで利用するのがOAuth2.0クライアントIDです。OAuth2.0プロトコルを利用することで、アプリケーションが特定ユーザとしてサービスを利用します。その際に許可する権限の範囲（スコープ）が制限できます。

![image-20201004222949949](/Users/daisuke/Library/Application Support/typora-user-images/image-20201004222949949.png)

OAuth2.0クライントIDは、OAuth2.0クライアントクレデンシャル（資格情報）というJSONファイルとしてダウンロードし利用することが多いと思います。OAuth2.0クライアントクレデンシャルには、OAuth2.0認証を利用するアプリの情報（クライアントID、クライアントシークレット）が含まれます。



### 取得方法

OAuth認証は作成する同意画面の設定やアプリの種類など状況によって適切に設定する必要がありますが、本投稿ではテストとして最短で利用する手順を書いてみます。

#### 1.同意画面の設定

OAuth認証では、認証時ユーザにログインをしてもらったり、許可してもらう権限の範囲を示したりする必要があるため、認証画面に表示する情報は重要です。以下は[connpass](https://connpass.com/)にTwitterアカウントでログインする際のOAuth認証画面です。画面にはconnpassのロゴなど表示され、どのアプリがアカウント情報を利用しようとしているかひと目で分かります。

<img src="/Users/daisuke/Library/Application Support/typora-user-images/image-20201005220247586.png" alt="image-20201005220247586" style="zoom:25%;" />

[Google Cloud Console]()にログインして、APIを利用するプロジェクトを選択します。



<img src="/Users/daisuke/prj/900_analysis/youtube_api/src/APIキー01.png" alt="APIキー01" style="zoom:25%;" />



APIとサービス > 認証情報

<img src="/Users/daisuke/prj/900_analysis/youtube_api/src/APIキー02.png" alt="APIキー02" style="zoom:25%;" />



「OAuth同意画面」を選択し、適当なアプリ名とメールアドレスを入力します

<img src="/Users/daisuke/prj/900_analysis/youtube_api/src/oauth_screen_1.png" alt="oauth_screen_1" style="zoom:25%;" />



## 3. サービスアカウントキー

工事中