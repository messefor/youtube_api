

import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account.
YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def get_credentials_old(credential_store_path):
    flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE,
                                    scope=YOUTUBE_READ_WRITE_SCOPE)
    storage = Storage(credential_store_path)
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        flags = tools.argparser.parse_args()
        credentials = tools.run_flow(flow, storage, flags)
    return credentials


def get_credentials(client_secret_file, scopes,
                    token_storage_pkl='token.pickle'):
    '''OAuth2 via google_auth_oauthlib

        https://developers.google.com/drive/api/v3/quickstart/python#step_1_turn_on_the_api_name
    '''
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(token_storage_pkl):
        with open(token_storage_pkl, 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secret_file, scopes=scopes)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_storage_pkl, 'wb') as token:
            pickle.dump(creds, token)

    return creds

# ------------------------------------------------------------------------


YOUTUBE_READ_WRITE_SCOPE = 'https://www.googleapis.com/auth/youtube'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

CLIENT_SECRET_FILE = 'config/client_secret.json'
APPLICATION_NAME = 'youtube-api'


creds = get_credentials(
                    client_secret_file=CLIENT_SECRET_FILE,
                    scopes=YOUTUBE_READ_WRITE_SCOPE,
                    token_storage_pkl='config/token.pkl'
                    )

service = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                credentials=creds)
