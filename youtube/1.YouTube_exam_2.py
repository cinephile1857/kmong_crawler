# -*- coding: utf-8 -*-
"""
Created on Tue Jul 19 14:31:35 2022

@author: agayo
"""

#%%

# API client library
import googleapiclient.discovery

# The data will be stored using pandas
import pandas as pd

# API information
api_service_name = "youtube"
api_version = "v3"
DEVELOPER_KEY = 'AIzaSyBOeAtA3A2V_4exdj_kROKaULBImIO-tu0'

# API client
youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = DEVELOPER_KEY)


# Cats query
cats_videos_ids = youtube.search().list(
    part="id",
    type='video',
    regionCode="KR",
    order="relevance",
    q="kitties",
    maxResults=7,
    fields="items(id(videoId))"
).execute()


# Dictionary to store cats video data
cats_info = {
    'id':[],
    'duration':[],
    'views':[],
    'likes':[],
    'dislikes':[],
    'favorites':[],
    'comments':[]
}


# For loop to obtain the information of each cats video
for item in cats_videos_ids['items']:
    
    # Getting the id
    vidId = item['id']['videoId']
    
    # Getting stats of the video
    r = youtube.videos().list(
        part="statistics,contentDetails",
        id=vidId,
        fields="items(statistics," + \
                     "contentDetails(duration))"
    ).execute()
 
    # We will only consider videos which contains all properties we need.
    # If a property is missing, then it will not appear as dictionary key,
    # this is why we need a try/catch block
    
    cats_info['id'].append(vidId)
    try:
        duration = r['items'][0]['contentDetails']['duration']
        cats_info['duration'].append(duration)        
    except:
        #pass
        cats_info['duration'].append('-') 
    try:
        views = r['items'][0]['statistics']['viewCount']
        cats_info['views'].append(views)        
    except:
        #pass  
        cats_info['views'].append('-')
    try:
        likes = r['items'][0]['statistics']['likeCount']
        cats_info['likes'].append(likes)        
    except:
        #pass   
        cats_info['likes'].append('-') 
    try:
        dislikes = r['items'][0]['statistics']['dislikeCount']
        cats_info['dislikes'].append(dislikes)        
    except:
        #pass     
        cats_info['dislikes'].append('-')  
    try:
        favorites = r['items'][0]['statistics']['favoriteCount']
        cats_info['favorites'].append(favorites)        
    except:
        #pass   
        cats_info['favorites'].append('-')   
    try:
        comments = r['items'][0]['statistics']['commentCount']
        cats_info['comments'].append(comments)        
    except:
        #pass       
        cats_info['comments'].append('-')  


    
#pd.DataFrame(data=cats_info).to_csv("cats.csv", index=False,na_rep='NaN')
pd.DataFrame(data=cats_info).to_csv("cats.csv", index=False) 


#누적쓸때
"""
import os
if not os.path.exists('cats.csv'):
    pd.DataFrame(data=cats_info).to_csv('cats.csv', index=False, mode='w')
else:
    pd.DataFrame(data=cats_info).to_csv('cats.csv', index=False, mode='a',header=False)
"""

#%%
    
    
    