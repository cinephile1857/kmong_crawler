import googleapiclient.discovery
import os
from multiprocessing import Pool,cpu_count
import pandas as pd
import time
import natsort
import shutil

path = os.getcwd()
cpu_num = cpu_count()
api_service_name = "youtube"
api_version = "v3"
developer_key_list = ["AIzaSyB5K8CCGzL-5e2u4VvwUEUWBPeUoCHOqdA", "AIzaSyDzbqF9EhH0TOYFc4JSy-kWrXRyuW_yo6Y",
                      "AIzaSyDiphH_2k82YHau7ilhDbYQTTe4r9Y1xTg", "AIzaSyBUwZ2JPzdnUS764k3WyMn_cabuQnmxxIo",
                      "AIzaSyAkA567O88D-wIdOcLnM1FyQnLxsLoaGkg", "AIzaSyCHGHU46vSrSwcv8xVEqRb1ZiqrrVXbjHM"]


def read_input():
    new_input_list = []
    video_id_list = []
    filename = 'input.xlsx'
    try:
        df = pd.read_excel(filename, header=None, engine='openpyxl')
        input_list = df.values.tolist()
        for i in input_list:
            new_input_list.append(i[0])
    except:
        print("You Need input.xlsx")
        quit()
    for i in new_input_list:
        if "v=" in i:
            v_id = i[(i.find("v=")+2):]
            video_id_list.append(v_id)
        else:
            v_id = i[(i.find("shorts") + len("/shorts")):]
            video_id_list.append(v_id)
    return video_id_list


def delete_folder(directory):
    if os.path.exists(directory):
       shutil.rmtree(directory, ignore_errors=True)


def create_folder(directory):
    delete_folder(directory)
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
            print('Error: Creating directory.' + directory)


def delete_file(directory):
    if os.path.exists(directory):
        os.remove(directory)


def overwrite_csv(data,directory):
    data = pd.DataFrame.from_dict([data])
    if not os.path.exists(directory):
        data.to_csv(directory, mode='w', index=False, header=True, encoding='utf-8-sig')
    else:
        data.to_csv(directory, mode='a', index=False, header=False, encoding='utf-8-sig')


def create_comment_dictionary(comment:dict):
    comment_dict = {}
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
    return comment_dict


def create_reply_dictionary(reply:dict):
    reply_dict = {}
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
    return reply_dict


def crawling_video(video_path):
    pid = os.getpid()
    path = video_path
    video_id = path[path.rfind("\\")+len("\\"):]
    key_num = 0
    comment_and_reply_path = path + "\\comment_and_reply.csv"
    comment_path = path + "\\comment.csv"
    reply_path = path + "\\reply.csv"
    reply_tmp_path = path + "\\reply_tmp.csv"
    delete_file(comment_and_reply_path)
    delete_file(comment_path)
    delete_file(reply_path)
    developer_key = developer_key_list[key_num]
    comment_nextPageToken = ''
    count = 0
    while True:
        try:
            youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey=developer_key)
            comment_request = youtube.commentThreads().list(
                    part="snippet,replies",
                    maxResults=100,
                    order="time",
                    videoId=video_id,
                    pageToken=comment_nextPageToken
            )
            comment_response = comment_request.execute()
            items = comment_response["items"]
            for comment in items:
                comment_dict = create_comment_dictionary(comment)
                count += 1
                overwrite_csv(comment_dict, comment_and_reply_path)
                overwrite_csv(comment_dict, comment_path)
                print("##############" + str(pid) + " save comment: " + str(
                    count) + " ##############")
                if 'replies' in comment:
                    reply_count = 0
                    if comment["snippet"]["totalReplyCount"] == len(comment["replies"]["comments"]):
                        replies = comment["replies"]["comments"]
                        for reply in replies:
                            reply_dict = create_reply_dictionary(reply)
                            reply_count += 1
                            count += 1
                            overwrite_csv(reply_dict, reply_tmp_path)
                            print("=======save reply: " + str(reply_count) + "/" + str(
                                comment_dict["reply_count"]) + "=======")
                            reply_tmp = pd.read_csv(reply_tmp_path)
                            reply_tmp = reply_tmp[::-1]
                            reply_tmp = reply_tmp.to_dict('records')
                            for tmp in reply_tmp:
                                overwrite_csv(tmp, comment_and_reply_path)
                                overwrite_csv(tmp, reply_path)
                            delete_file(reply_tmp_path)
                    else:
                        reply_nextPageToken = ''
                        while True:
                            try:
                                reply_request = youtube.comments().list(
                                    part="snippet",
                                    maxResults=100,
                                    parentId=comment["id"],
                                    pageToken=reply_nextPageToken
                                )
                                reply_response = reply_request.execute()
                                replies = reply_response["items"]
                                for reply in replies:
                                    reply_dict = create_reply_dictionary(reply)
                                    reply_count += 1
                                    count += 1
                                    overwrite_csv(reply_dict, reply_tmp_path)
                                    print("=======" + str(pid) + "save reply: " + str(reply_count) + "/" + str(
                                        comment_dict["reply_count"]) + "=======")
                                if 'nextPageToken' in reply_response:
                                    reply_nextPageToken = reply_response["nextPageToken"]
                                else:
                                    reply_tmp = pd.read_csv(reply_tmp_path)
                                    reply_tmp = reply_tmp[::-1]
                                    reply_tmp = reply_tmp.to_dict('records')
                                    for tmp in reply_tmp:
                                        overwrite_csv(tmp, comment_and_reply_path)
                                        overwrite_csv(tmp, reply_path)
                                    delete_file(reply_tmp_path)
                                    break
                            except googleapiclient.errors.HttpError as e:
                                print(str(developer_key_list[key_num]) + " is exceed quota")
                                key_num += 1
                                developer_key = developer_key_list[key_num]
                                youtube = googleapiclient.discovery.build(api_service_name, api_version,
                                                                          developerKey=developer_key)
            if 'nextPageToken' in comment_response:
                comment_nextPageToken = comment_response["nextPageToken"]
            else:
                break
        except googleapiclient.errors.HttpError as e:
            print(str(developer_key_list[key_num]) + " is exceed quota")
            key_num += 1
            developer_key = developer_key_list[key_num]
    print("☆☆☆☆☆☆☆☆☆☆ " + str(pid) + "is finish" + " ☆☆☆☆☆☆☆☆☆☆ " )




if __name__ == '__main__':
    start = time.time()

    root_path = input("save_path?: ")  # "C:\\Users\\agayo\\Desktop\\크몽\\daily_test\\youtube"
    order = input("order: time? or like?")
    video_id_list = read_input()
    path_list = []
    for i in video_id_list:
        create_folder(root_path + "\\" + i)
        path_list.append(root_path + "\\" + i)

    process = Pool(cpu_num)
    progress = process.map_async(crawling_video, path_list)
    finish = progress.get()
    process.close()
    process.join()

    print("time :", time.time() - start)
















