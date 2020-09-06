""" """
import pandas as pd
import toml
from datetime import datetime, timedelta
from googleapiclient.discovery import build

def pt2sec(pt_time):
    t = datetime.strptime(pt_time,"PT%MM%SS")
    return timedelta(minutes=t.minute, seconds=t.second).total_seconds()

def get_duration(item):
    content_details = item['contentDetails']
    pt_time = content_details['duration']
    return pt2sec(pt_time)

def get_basicinfo(snippet):
    keys = ('title', 'description', 'channelTitle')
    return {k: snippet[k] for k in keys}

# --------------------------------------------------------------------

# Set Youtube APIKEY
configpath = 'config.toml'
if os.path.exists(configpath):
    config = toml.load(configpath)
    YOUTUBE_API_KEY = config['YOUTUBE_API_KEY']
else:
    YOUTUBE_API_KEY = 'Your-API-KEY-here'

service = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# Trials
q = 'Sideway Shuffle'
response = service.search().list(part='snippet',
                                q=q,
                                order='viewCount',
                                type='video',).execute()

# Search chennel ID
q = 'B-life'
response = service.search().list(part='snippet',
                                q=q,
                                order='viewCount',
                                type='channel').execute()
item = response['items'][0]
print('title:', item['snippet']['title'], 'id:', item['id'])

# --------------------------------------------------------------------

# Fetch most viewed chennel
chennel_id = item['id']['channelId']


# Fetch all video snippets in specified channels
response = service.search().list(part='snippet',
                                channelId=chennel_id,
                                order='viewCount',
                                type='video',
                                maxResults=50).execute()
videoids = [item['id']['videoId']
                for item in response['items']]
len(videoids)


# publishedAfter
# publishedBefore
# --------------------------------------------------------------------

part = ['snippet', 'contentDetails']
response = service.videos().list(part=part, id=videoids).execute()

results = []
for item in response['items']:
    info = get_basicinfo(item['snippet'])
    info['duration'] = get_duration(item)
    results.append(info)

pd.DataFrame(results)
