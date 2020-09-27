

Videosリソースの`contentDetails`に動画の長さが入っている

https://developers.google.com/youtube/v3/docs/videos?hl=ja

> | `contentDetails`          | `object` `contentDetails` オブジェクトには、動画の長さとアスペクト比を含む、動画コンテンツに関する情報が格納されます。 |
> | ------------------------- | ------------------------------------------------------------ |
> | `contentDetails.duration` | `string` 動画の長さ。このタグの値は、[ISO 8601](https://en.wikipedia.org/wiki/ISO_8601#Durations) に従って、持続期間を `PT#M#S` の形式で表したものです。文字 `PT` は期間を表す値、文字 `M` は分数、`S` は秒数を示します。文字 `M` と `S` の前に付く `#` はどちらも整数値で、動画の長さを分または秒単位で指定します。たとえば、`PT15M51S` という値は、動画の長さが 15 分 51 秒であることを示します。 |


```
pip install google-api-python-client, oauth2client
```







----




OAuth、サービスアカウントはユーザーのデータにアクセスする場合
アプリケーションがAPIを使用してGoogleユーザーのデータにアクセスする場合、こちらを行います。
http://homework.hatenablog.jp/entry/2016/11/30/134132
2つの方法でデータにアクセスできる
- OAuth2.0 認証
- サービスアカウント

APIを利用するのにAPIキーが必要
アプリケーションがGoogle APIとやり取りするために認証が必要です。
http://homework.hatenablog.jp/entry/2016/12/06/155612


Youtubeの検索などははAPIキーさえあれば利用できる
プレイリスト更新はユーザデータへのアクセス

------
1. APIを有効にする

2. APIキーを作成

----

APIを有効にする

https://developers.google.com/drive/api/v3/enable-drive-api

[Google API Console](https://console.developers.google.com/).



APIとサービス



![image-20200927183217564](/Users/daisuke/Library/Application Support/typora-user-images/image-20200927183217564.png)


---
YoutubeのプレイリストをSlackから操作しようとして失敗した話
https://roy29fuku.com/web/youtube-data-api-insert-playlistitems/
