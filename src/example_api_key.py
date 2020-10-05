
from googleapiclient.discovery import build

# 利用するAPIサービス
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'
YOUTUBE_API_KEY = 'Your-API-KEY-here'

# API のビルドと初期化
youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
            developerKey=YOUTUBE_API_KEY)


q = 'Overjoyed'
response = youtube.search().list(part='snippet',
                                q=q,
                                order='viewCount',
                                type='video',).execute()
