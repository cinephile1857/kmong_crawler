# -*- coding: utf-8 -*-
"""
Created on Tue Jul 19 11:35:46 2022

@author: agayo
"""


#%%
# API client library
import googleapiclient.discovery

# API information
api_service_name = "youtube"
api_version = "v3"

# API key
DEVELOPER_KEY = "YOUR_API_KEY"

# API client
youtube = googleapiclient.discovery.build(
    api_service_name, api_version, developerKey = DEVELOPER_KEY)


# 'request' variable is the only thing you must change
# depending on the resource and method you need to use
# in your query
request = youtube.search().list(
)
# To perform list method on playlists resource
request = youtube.playlists().list(
)
# To perform list method on videos resource
request = youtube.videos().list(
)
# to perform list method on channels resource
request = youtube.channels().list(
)

# Query execution
response = request.execute()

# Print the results
print(response)

#%%

# to request only id part properties
request = youtube.channels().list(
    part="id"
)
# to request only snippet part properties
request = youtube.channels().list(
    part="snippet"
)
# to request id and snippet parts properties
request = youtube.channels().list(
    part="id,snippet"
)

#%%

# API client library
import googleapiclient.discovery

# API information
api_service_name = "youtube"
api_version = "v3"
DEVELOPER_KEY = 'AIzaSyBOeAtA3A2V_4exdj_kROKaULBImIO-tu0'

# API client
youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = DEVELOPER_KEY)

# Request body
request = youtube.search().list(
        part="id,snippet",
        type='channel',
        q="ㄱ",
        regionCode='KR',
        maxResults=50
)

# Request execution
response = request.execute()
print(response)



#%%

# API client library
import googleapiclient.discovery

# API information
api_service_name = "youtube"
api_version = "v3"
DEVELOPER_KEY = 'AIzaSyBOeAtA3A2V_4exdj_kROKaULBImIO-tu0'

# API client
youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = DEVELOPER_KEY)

# Request body
request = youtube.search().list(
        part="snippet",
        type='channel',
        q="ㄱ",
        regionCode='KR',
        maxResults=50,
        fields="items(snippet(publishedAt,channelId,channelTitle,title,description))"
)

# Request execution
response = request.execute()
print(response)

#%%

# API client library
import googleapiclient.discovery

# API information
api_service_name = "youtube"
api_version = "v3"
DEVELOPER_KEY = 'AIzaSyBOeAtA3A2V_4exdj_kROKaULBImIO-tu0'

# API client
youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = DEVELOPER_KEY)

# Request body
request = youtube.search().list(
        part="snippet",
        type='channel',
        q="ㄱ",
        regionCode='KR',
        maxResults=50,
        fields="nextPageToken,items(snippet(publishedAt,channelId,channelTitle,title,description))"
)

# Request execution
response = request.execute()

# Getting next token from the first query
nextToken = response['nextPageToken']

# Second query
request2 = youtube.search().list(
        part="snippet",
        type='channel',
        q="ㄱ",
        regionCode='KR',
        maxResults=50,
        fields="nextPageToken,items(snippet(publishedAt,channelId,channelTitle,title,description))",
        pageToken=nextToken
)

response2 = request2.execute()

print("RESPONSE 1")
print(response)
print("\nRESPONSE 2")
print(response2)

#%%

print("RESPONSE 1")
print("Next page toke : ",response['nextPageToken'])
print("Channel ID : ",response['items'][0]['snippet']['channelId'])
print("Channel Title : ",response['items'][0]['snippet']['channelTitle'])

#%%

