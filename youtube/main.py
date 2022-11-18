import googleapiclient.discovery
import os
from multiprocessing import Pool,cpu_count
import pandas as pd
import time
import natsort
import shutil

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


def read_directory(directory):
    file_list = os.listdir(directory)
    file_list = natsort.natsorted(file_list)
    return file_list


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
    comment_path = path + "\\comment_recent.csv"
    reply_path = path + "\\reply.csv"
    reply_tmp_path = path + "\\reply_tmp.csv"
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


def sort_comment_oldest(video_path):
    path = video_path
    comment_tmp = pd.read_csv(path+"\\"+"comment_recent.csv")
    comment_tmp = comment_tmp.sort_values(by='publish_time')
    comment_tmp = comment_tmp.to_dict('records')
    for tmp in comment_tmp:
        overwrite_csv(tmp, path+"\\"+"comment_oldest.csv")
    file_list = read_directory(path)
    for i in file_list:
        if "comment" in i:
            if i != "comment_oldest.csv":
                delete_file(path+"\\"+i)


def sort_comment_like(video_path):
    path = video_path
    comment_tmp = pd.read_csv(path+"\\"+"comment_recent.csv")
    comment_tmp = comment_tmp.sort_values(by=['like_count','publish_time'],ascending=[False,False])
    comment_tmp = comment_tmp.to_dict('records')
    for tmp in comment_tmp:
        overwrite_csv(tmp, path+"\\"+"comment_like.csv")
    file_list = read_directory(path)
    for i in file_list:
        if "comment" in i:
            if i != "comment_like.csv":
                delete_file(path+"\\"+i)


def sort_comment_reply(video_path):
    path = video_path
    comment_tmp = pd.read_csv(path+"\\"+"comment_recent.csv")
    comment_tmp = comment_tmp.sort_values(by=['reply_count','publish_time'],ascending=[False,False])
    comment_tmp = comment_tmp.to_dict('records')
    for tmp in comment_tmp:
        overwrite_csv(tmp, path+"\\"+"comment_reple.csv")
    file_list = read_directory(path)
    for i in file_list:
        if "comment" in i:
            if i != "comment_reple.csv":
                delete_file(path+"\\"+i)


def sort_reply_oldest(video_path):
    path = video_path
    comment_tmp = pd.read_csv(path+"\\"+"reply.csv")
    comment_tmp = comment_tmp.sort_values(by='publish_time')
    comment_tmp = comment_tmp.to_dict('records')
    for tmp in comment_tmp:
        overwrite_csv(tmp, path+"\\"+"reply_oldest.csv")
    file_list = read_directory(path)
    for i in file_list:
        if "reply" in i:
            if i != "reply_oldest.csv":
                delete_file(path+"\\"+i)


def sort_reply_recent(video_path):
    path = video_path
    comment_tmp = pd.read_csv(path+"\\"+"reply.csv")
    comment_tmp = comment_tmp.sort_values(by='publish_time',ascending=False)
    comment_tmp = comment_tmp.to_dict('records')
    for tmp in comment_tmp:
        overwrite_csv(tmp, path+"\\"+"reply_recent.csv")
    file_list = read_directory(path)
    for i in file_list:
        if "reply" in i:
            if i != "reply_recent.csv":
                delete_file(path+"\\"+i)


def integration_comment_reply(video_path):
    print("not yet")


if __name__ == '__main__':
    start = time.time()

    root_path = input("save_path?: ")

    comment_order = input("comment_order? \n[0]:recent(최신순, 내림차순)\n[1]:order(오래된순, 오름차순)"
                          "\n[2]:like(좋아요순, 동일시 최신순)\n[3]:reply(답글순, 동일시 최신순)\n")
    reply_order = input("reply_order? \n[0]:recent(최신순, 내림차순)\n[1]:order(오래된순, 오름차순)\n")

    video_id_list = read_input()
    path_list = []
    for i in video_id_list:
        create_folder(root_path + "\\" + i)
        path_list.append(root_path + "\\" + i)

    crawling_process = Pool(cpu_num)
    crawling_progress = crawling_process.map_async(crawling_video, path_list)
    crawling_finish = crawling_progress.get()
    crawling_process.close()
    crawling_process.join()

    comment_order_process = Pool(cpu_num)
    if comment_order == "0":
        pass
    elif comment_order == "1":
        comment_order_progress = comment_order_process.map_async(sort_comment_oldest, path_list)
        comment_order_finish = comment_order_progress.get()
    elif comment_order == "2":
        comment_order_progress = comment_order_process.map_async(sort_comment_like, path_list)
        comment_order_finish = comment_order_progress.get()
    else:
        comment_order_progress = comment_order_process.map_async(sort_comment_reply, path_list)
        comment_order_finish = comment_order_progress.get()
    comment_order_process.close()
    comment_order_process.join()

    reply_order_process = Pool(cpu_num)
    if reply_order == "0":
        reply_order_progress = reply_order_process.map_async(sort_reply_recent, path_list)
        reply_order_finish = reply_order_progress.get()
    else:
        reply_order_progress = reply_order_process.map_async(sort_reply_oldest, path_list)
        reply_order_finish = reply_order_progress.get()
    reply_order_process.close()
    reply_order_process.join()

    print("time :", time.time() - start)
















