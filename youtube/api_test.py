import googleapiclient.discovery
import os
import pandas as pd


"""

응답으로부터 딕셔너리 만드는 부분 모두 함수로 변경

리플라이는 저장하고 거꾸로 읽도록 변경

api 키 리스트로 만들고

초과하면 알아서 다음 키로 사용하게 코드 수정


"""


def overwrite_csv(data,directory):
    data = pd.DataFrame.from_dict([data])
    if not os.path.exists(directory):
        data.to_csv(directory, mode='w', index=False, header=True, encoding='utf-8-sig')
    else:
        data.to_csv(directory, mode='a', index=False, header=False, encoding='utf-8-sig')


# API information
api_service_name = "youtube"
api_version = "v3"
DEVELOPER_KEY = "AIzaSyB5K8CCGzL-5e2u4VvwUEUWBPeUoCHOqdA"
# cinephile1854: AIzaSyB5K8CCGzL-5e2u4VvwUEUWBPeUoCHOqdA
# agayong93: AIzaSyDzbqF9EhH0TOYFc4JSy-kWrXRyuW_yo6Y

save_path = "C:\\Users\\agayo\\Desktop\\크몽\\daily_test\\comment_test.csv"







youtube = googleapiclient.discovery.build(
    api_service_name, api_version, developerKey = DEVELOPER_KEY)


comment_request = youtube.commentThreads().list(
        part="snippet,replies",
        maxResults=100,
        order = "relevance", # "time",
        videoId = "wlmKkCKu7H4",
        pageToken = ""
)

comment_response = comment_request.execute()


comment_nextPageToken = ''
if 'nextPageToken' in comment_response:
    comment_nextPageToken = comment_response["nextPageToken"]





items = comment_response["items"]



comment_count = 0

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

    comment_count += 1
    overwrite_csv(comment_dict, save_path)
    print("================"+"save comment: "+str(comment_count)+"================")

    if 'replies' in comment:
        reply_count = 0
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

                reply_count += 1
                overwrite_csv(reply_dict, save_path)
                print("=======save reply: "+str(reply_count)+"/"+str(comment_dict["reply_count"])+"=======")

        else:
            reply_nextPageToken = ''
            while True:
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

                    reply_count += 1
                    overwrite_csv(reply_dict, save_path)
                    print("=======save reply: " + str(reply_count) + "/" + str(comment_dict["reply_count"]) + "=======")

                if 'nextPageToken' in reply_response:
                    reply_nextPageToken = reply_response["nextPageToken"]
                else:
                    break








