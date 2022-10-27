import TikToK_Scraper
import TikTok_Parser
from multiprocessing import Pool,cpu_count
import time
import System
import os
import pandas as pd
import math

path = os.getcwd()
cpu_num = cpu_count()
input_list = System.read_input()
scraper = TikToK_Scraper.Scraper()


def get_video_path_list():
    video_id = System.read_directory(path + "\\" + "comment")
    video_path_list = []
    for i in video_id:
        video_path_list.append(path + "\\" + "comment" + "\\" + i)
    return video_path_list


def api_scraping():
    print("====================API Scraping====================")
    scraping_process = Pool(cpu_num)
    System.delete_folder(path + "\\" + "comment")
    scraper_progress = scraping_process.map_async(scraper.comment, input_list)
    scraper_finish = scraper_progress.get()
    scraping_process.close()
    scraping_process.join()


def comment_parsing(video_path_list):
    print("====================comment API Parsing====================")
    comment_parsing_process = Pool(cpu_num)
    comment_parser_progress = comment_parsing_process.map_async(TikTok_Parser.comment_parser, video_path_list)
    comment_parser_finish = comment_parser_progress.get()
    comment_parsing_process.close()
    comment_parsing_process.join()


def reply_parsing(video_path_list):
    print("====================reply API Parsing====================")
    reply_parsing_process = Pool(cpu_num)
    reply_parser_progress = reply_parsing_process.map_async(TikTok_Parser.reply_parser, video_path_list)
    reply_parser_finish = reply_parser_progress.get()
    reply_parsing_process.close()
    reply_parsing_process.join()


def user_list(video_path_list):
    print("====================user_list====================")
    user_list_process = Pool(cpu_num)
    user_list_progress = user_list_process.map_async(scraper.user_list, video_path_list)
    reply_parser_finish = user_list_progress.get()
    user_list_process.close()
    user_list_process.join()


def integration(video_path_list):
    print("====================user list create====================")
    user_list(video_path_list)
    print("====================comment_and_reply integration====================")
    integration_process = Pool(cpu_num)
    integration_progress = integration_process.map_async(TikTok_Parser.integrate_comment_and_reply, video_path_list)
    reply_parser_finish = integration_progress.get()
    integration_process.close()
    integration_process.join()


def translate(video_path_list):
    print("====================translate====================")
    translate_process = Pool(cpu_num)
    translate_progress = translate_process.map_async(TikTok_Parser.translate, video_path_list)
    reply_parser_finish = translate_progress.get()
    translate_process.close()
    translate_process.join()


def user_info(video_path_list):
    print("====================user_info====================")
    cpu_num = 4
    user_info_process = Pool(cpu_num)
    if len(video_path_list) == 1:
        user_list_list = []
        if not os.path.exists(video_path_list[0] + "\\" + "user_list_0.csv"):
            user_num = 0
            for cnt, chunk in enumerate(pd.read_csv(video_path_list[0] + "\\" + "user_list.csv", chunksize=1)):
                user_num = cnt
            user_num += 1
            size = math.ceil(user_num/cpu_num)
            index = 0
            for cnt, chunk in enumerate(pd.read_csv(video_path_list[0] + "\\" + "user_list.csv", chunksize=size)):
                chunk.to_csv(video_path_list[0] + "\\" + "user_list_" + str(index) + ".csv", mode='w', index=False, encoding='utf-8-sig')
                user_list_list.append(video_path_list[0] + "\\" + "user_list_" + str(index) + ".csv")
                index += 1
        else:
            directory = System.read_directory(video_path_list[0])
            for file in directory:
                if 'user_list_' in file:
                    if '_info' not in file and '_exception' not in file:
                        user_list_list.append(video_path_list[0] + "\\" + file)
        user_info_progress = user_info_process.map_async(scraper.user_info_single, user_list_list)
    else:
        user_info_progress = user_info_process.map_async(scraper.user_info_multi, video_path_list)
    user_info_finish = user_info_progress.get()
    user_info_process.close()
    user_info_process.join()


def user_integration(src_file, video_path_list):
    print("====================user_info_integration====================")
    if len(video_path_list) == 1:
        user_list_info = video_path_list[0] + "\\user_list_info.csv"
        System.delete_file(user_list_info)
        directory = System.read_directory(video_path_list[0])
        for file in directory:
            if 'user_list_' in file:
                if '_info' in file:
                    for cnt, chunk in enumerate(pd.read_csv(video_path_list[0] + "\\" + file, chunksize=1)):
                        System.overwrite_csv(chunk, user_list_info)
    user_integration_process = Pool(cpu_num)
    if src_file == "result.csv":
        user_integration_progress = user_integration_process.map_async(TikTok_Parser.user_info_integration,
                                                                   video_path_list)
    elif src_file == "result_t.csv":
        user_integration_progress = user_integration_process.map_async(TikTok_Parser.user_info_integration_translate,
                                                                   video_path_list)
    else:
        quit()
    user_integration_finish = user_integration_progress.get()
    user_integration_process.close()
    user_integration_process.join()


def column_fix(video_path_list):
    map = {"0": "comment_or_reply",
           "1": "create_time",
           "2": "user_unique_id",
           "3": "user_nickname",
           "4": "like_count",
           "5": "reply_count",
           "6": "author_like",
           "7": "language",
           "8": "text",
           "9": "translate",
           "10": "follower_count",
           "11": "following_count",
           "12": "heart_count",
           "13": "video_count"
           }
    eng_kr = {"comment_or_reply": "댓글/답글",
              "create_time": "작성 시간",
              "user_unique_id": "아이디",
              "user_nickname": "닉네임",
              "like_count": "좋아요 수",
              "reply_count": "답글 수",
              "author_like": "작성자 좋아요 유무",
              "language": "언어",
              "text": "내용",
              "translate": "번역 내용",
              "follower_count": "작성자 팔로워 수",
              "following_count": "작성자 팔로잉 수",
              "heart_count": "작성자 좋아요 수",
              "video_count": "작성자 비디오 수"
              }
    src_file = input("src_file: ")
    column_num = input("column_num: ")
    column_order = []
    for i in map:
        print(str(i)+":"+map[i])
    for i in range(int(column_num)):
        i = input()
        column_order.append(i)

    for i in video_path_list:
        print("====================column fix start====================")
        print(i)
        src_path = i + "\\" + src_file
        result_path = i + "\\" + "final.csv"
        System.delete_file(result_path)
        cnt_max = 0
        for cnt, chunk in enumerate(pd.read_csv(src_path, chunksize=1)):
            cnt_max = cnt
        for cnt, chunk in enumerate(pd.read_csv(src_path, chunksize=1)):
            new_chunk = {}
            for column in column_order:
                new_chunk[eng_kr[map[column]]] = chunk[map[column]].values[0]
            print(str(cnt) + "/" + str(cnt_max))
            System.overwrite_csv(pd.DataFrame([new_chunk]), result_path)


def wordcloud(video_path_list):
    print("====================wordcloud====================")
    wordcloud_process = Pool(cpu_num)
    wordcloud_progress = wordcloud_process.map_async(TikTok_Parser.wordcloud, video_path_list)
    wordcloud_finish = wordcloud_progress.get()
    wordcloud_process.close()
    wordcloud_process.join()


if __name__ == '__main__':
    print("====================TikTok Comment Crawling===================")
    print("<<Choose Step...>>")
    print("All_In_One = 0\nAPI_Scraping = 1\nComment_Parsing = 2\nReply_Parsing = 3\nComment_Reply_Integration = 4")
    print("Translate = 5\nUser_Info = 6\nUser_Info_Integration = 7\nColumn_Fix = 8\nWord_Cloud = 9\nCSV_to_EXCEL = 10")
    step = input("step : ")
    print("<<Choose Root Path...>>")
    root = input("You use default path? [Y|N]")
    if root == "Y" or root == "y":
        pass
    else:
        path = input("write the path : ")
    scraper.set_path(path)

    start = time.time()
    if step == str(0):
        api_scraping()
        video_path = get_video_path_list()
        comment_parsing(video_path)
        reply_parsing(video_path)
        integration(video_path)
    elif step == str(1):
        api_scraping()
        video_path = get_video_path_list()
    elif step == str(2):
        video_path = get_video_path_list()
        comment_parsing(video_path)
    elif step == str(3):
        video_path = get_video_path_list()
        reply_parsing(video_path)
    elif step == str(4):
        video_path = get_video_path_list()
        integration(video_path)
    elif step == str(5):
        video_path = get_video_path_list()
        translate(video_path)
    elif step == str(6):
        use_proxy = input("You need Proxy? [Y|N]: ")
        if use_proxy == "Y" or use_proxy == "y":
            scraper.set_proxy()
        video_path = get_video_path_list()
        user_info(video_path)
    elif step == str(7):
        video_path = get_video_path_list()
        src = input("src_file: ")
        user_integration(src, video_path)
    elif step == str(8):
        video_path = get_video_path_list()
        column_fix(video_path)
    elif step == str(9):
        video_path = get_video_path_list()
        wordcloud(video_path)
    elif step == str(10):
        print("write full path")
        src_dir = input("input path : ")
        save_dir = input("save path : ")
        System.csv_to_excel(src_dir,save_dir)
    else:
        quit()
    delta_t = time.time() - start
    print(delta_t)


