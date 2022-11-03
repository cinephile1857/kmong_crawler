import googleapiclient.discovery

# API information
api_service_name = "youtube"
api_version = "v3"

# API key
DEVELOPER_KEY = "AIzaSyB5K8CCGzL-5e2u4VvwUEUWBPeUoCHOqdA"

# cinephile1854: AIzaSyB5K8CCGzL-5e2u4VvwUEUWBPeUoCHOqdA
# agayong93: AIzaSyDzbqF9EhH0TOYFc4JSy-kWrXRyuW_yo6Y

# API client
youtube = googleapiclient.discovery.build(
    api_service_name, api_version, developerKey = DEVELOPER_KEY)

# Request body
comment_request = youtube.commentThreads().list(
        part="snippet,replies",
        maxResults=100,
        order = "relevance", # "time",
        videoId = "wlmKkCKu7H4",
        pageToken = ""
)


# Request execution
comment_response = comment_request.execute()


print(comment_response)



comment_nextPageToken = ''
if 'nextPageToken' in comment_response:
    comment_nextPageToken = comment_response["nextPageToken"]

items = comment_response["items"]




for comment in items:
    comment_dict = {}
    reply_dict = {}
    comment_dict["comment_or_reply"] = "comment"
    comment_dict["id"] = comment["id"]
    comment_dict["reply_count"] = comment["snippet"]["totalReplyCount"]
    comment_dict["parent_id"] = ""
    comment_dict["text"] = comment["snippet"]["topLevelComment"]["snippet"]["textOriginal"]
    comment_dict["author_name"] = comment["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"]
    comment_dict["author_profile_image"] = comment["snippet"]["topLevelComment"]["snippet"]["authorProfileImageUrl"]
    comment_dict["author_channel_url"] = comment["snippet"]["topLevelComment"]["snippet"]["authorChannelUrl"]
    comment_dict["author_channel_id"] = comment["snippet"]["topLevelComment"]["snippet"]["authorChannelId"]["value"]
    comment_dict["like_count"] = comment["snippet"]["topLevelComment"]["snippet"]["likeCount"]
    comment_dict["publish_time"] = comment["snippet"]["topLevelComment"]["snippet"]["publishedAt"]
    comment_dict["update_time"] = comment["snippet"]["topLevelComment"]["snippet"]["updatedAt"]

    if 'replies' in comment:
        if comment["snippet"]["totalReplyCount"] == len(comment["replies"]["comments"]):
            replies = comment["replies"]["comments"]
            for reply in replies:
                reply_dict["comment_or_reply"] = "reply"
                reply_dict["id"] = reply["id"]
                reply_dict["reply_count"] = ""
                reply_dict["parent_id"] = reply["snippet"]["parentId"]
                reply_dict["text"] = reply["snippet"]["textOriginal"]
                reply_dict["author_name"] = reply["snippet"]["authorDisplayName"]
                reply_dict["author_profile_image"] = reply["snippet"]["authorProfileImageUrl"]
                reply_dict["author_channel_url"] = reply["snippet"]["authorChannelUrl"]
                reply_dict["author_channel_id"] = reply["snippet"]["authorChannelId"]["value"]
                reply_dict["like_count"] = reply["snippet"]["likeCount"]
                reply_dict["publish_time"] = reply["snippet"]["publishedAt"]
                reply_dict["update_time"] = reply["snippet"]["updatedAt"]

                reply_list.append(reply_dict)
                print()

        else:
            reply_list = []
            while True:
                reply_nextPageToken = ''
                reply_request = youtube.comments().list(
                    part="snippet",
                    maxResults=100,
                    parentId=comment["id"],
                    pageToken=reply_nextPageToken
                )
                reply_response = reply_request.execute()

                replies = reply_response["items"]
                for reply in replies:
                    reply_dict["comment_or_reply"] = "reply"
                    reply_dict["id"] = reply["id"]
                    reply_dict["reply_count"] = ""
                    reply_dict["parent_id"] = reply["snippet"]["parentId"]
                    reply_dict["text"] = reply["snippet"]["textOriginal"]
                    reply_dict["author_name"] = reply["snippet"]["authorDisplayName"]
                    reply_dict["author_profile_image"] = reply["snippet"]["authorProfileImageUrl"]
                    reply_dict["author_channel_url"] = reply["snippet"]["authorChannelUrl"]
                    reply_dict["author_channel_id"] = reply["snippet"]["authorChannelId"]["value"]
                    reply_dict["like_count"] = reply["snippet"]["likeCount"]
                    reply_dict["publish_time"] = reply["snippet"]["publishedAt"]
                    reply_dict["update_time"] = reply["snippet"]["updatedAt"]

                    reply_list.append(reply_dict)
                    print()

                if 'nextPageToken' in reply_response:
                    reply_nextPageToken = reply_response["nextPageToken"]
                else:
                    break








