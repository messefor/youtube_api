
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

# https://google-auth.readthedocs.io/en/latest/reference/google.oauth2.service_account.html
# https://developers.google.com/sheets/api/quickstart/python
# --------------------------------------------------------

from google.oauth2 import service_account

CREDENTIAL_FILE = 'config/youtube-data-api-291411-7aa5797d4450.json'
credentials =\
  service_account.Credentials.from_service_account_file(CREDENTIAL_FILE)


SAMPLE_SPREADSHEET_ID = '1CL0pg_LDpASaHQqagDxBDKonmD64NRS6CQnpAbVDjhs'
SAMPLE_RANGE_NAME = 'Class Data!A1:B4'

service = build('sheets', 'v4', credentials=credentials)
sheet = service.spreadsheets()

result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                            range=SAMPLE_RANGE_NAME).execute()
values = result.get('values', [])