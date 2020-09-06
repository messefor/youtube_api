""" """

import pandas as pd
import os

import toml
from datetime import datetime, timedelta, timezone
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


def fetch_video_info(response, as_df=True):
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
# TODO: get from toml
chennel_id = item['id']['channelId']


# Fetch all video snippets in specified channels
# if response['pageInfo'] > 500:

n_requested = 50
earliest_publishedtime =\
    datetime.now(tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
result = []
while True:
    response = service.search().list(part='snippet',
                                    channelId=chennel_id,
                                    order='date',
                                    type='video',
                                    publishedBefore=earliest_publishedtime,
                                    maxResults=n_requested).execute()
    video_info = fetch_video_info(response)
    result.append(video_info)
    earliest_publishedtime = video_info['publishTime'].min()
    print(response['pageInfo'])
    if len(response['items']) < n_requested:
        break

if len(result) > 1:
    df_video_list = pd.concat(result, axis=0)
else:
    df_video_list = result[0]


# --------------------------------------------------------------------
# Request contents details of video ids
# --------------------------------------------------------------------
part = ['snippet', 'contentDetails']
videoids = list(df_video_list['videoId'].unique())
response = service.videos().list(part=part, id=videoids).execute()

results = []
for item in response['items']:
    info = get_basicinfo(item['snippet'])
    info['duration'] = get_duration(item)
    results.append(info)

pd.DataFrame(results)
