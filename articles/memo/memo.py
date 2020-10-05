""" """


import os
import sys

import httplib2
import toml
import pandas as pd

# from apiclient import discovery
from googleapiclient.discovery import build

from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

CLIENT_SECRET_FILE = 'config/client_secret.json'
YOUTUBE_READ_WRITE_SCOPE = 'https://www.googleapis.com/auth/youtube'
APPLICATION_NAME = 'youtube-api'

credential_dir = 'config'
credential_path = os.path.join(credential_dir, 'google_drive.json')


def get_credentials(credential_store_path):
    flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE,
                                    scope=YOUTUBE_READ_WRITE_SCOPE)
    storage = Storage(credential_store_path)
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        flags = tools.argparser.parse_args()
        credentials = tools.run_flow(flow, storage, flags)
    return credentials

youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                http=credentials.authorize(httplib2.Http()))

# ------------------------------------------------------------------------
# Trials
# q = 'Sideway Shuffle'
# response = youtube.search().list(part='snippet',
#                                 q=q,
#                                 order='viewCount',
#                                 type='video',).execute()

# --------------------------------------------------------------------
# Get channel ID via search
# --------------------------------------------------------------------
# Search chennel ID
# q = 'B-life'
# response = youtube.search().list(part='snippet',
#                                 q=q,
#                                 order='viewCount',
#                                 type='channel').execute()
# item = response['items'][1]
# print('title:', item['snippet']['title'], 'id:', item['id'])

# --------------------------------------------------------------------

# Fetch most viewed chennel
# TODO: get from toml
# channel_id = item['id']['channelId']

