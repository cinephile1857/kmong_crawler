import pandas as pd
import os
import time
import natsort


def delete_file(directory):
    if os.path.exists(directory):
        os.remove(directory)


def csv_to_excel(src_dir,save_dir):
    src = pd.read_csv(src_dir)
    src.to_excel(save_dir,index=None,header=True,engine='xlsxwriter')


def overwrite_csv(data,directory):
    if not os.path.exists(directory):
        data.to_csv(directory, mode='w', index=False, header=True, encoding='utf-8-sig')
    else:
        data.to_csv(directory, mode='a', index=False, header=False, encoding='utf-8-sig')


def read_directory(directory):
    file_list = os.listdir(directory)
    file_list = natsort.natsorted(file_list)
    return file_list


def column_fix(video_path_list):
    map = {"0": "comment_or_reply",
           "1": "id",
           "2": "reply_count",
           "3": "parent_id",
           "4": "text",
           "5": "author_name",
           "6": "author_profile_image",
           "7": "author_channel_url",
           "8": "author_channel_id",
           "9": "like_count",
           "10": "publish_time",
           "11": "update_time"
           }
    eng_kr = {"comment_or_reply": "댓글/답글",
              "id": "댓글 아이디",
              "reply_count": "답글 개수",
              "parent_id": "상위 댓글 아이디",
              "text": "텍스트",
              "author_name": "작성자 아이디",
              "author_profile_image": "작성자 프로필 사진 URL",
              "author_channel_url": "작성자 채널 URL",
              "author_channel_id": "작성자 채널 ID",
              "like_count": "종아요 개수",
              "publish_time": "작성 시간",
              "update_time": "수정 시간"
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
        result_path = i + "\\" + src_file[:src_file.find('.')] + "_colum_fix.csv"
        excel_result_path = i + "\\" + src_file[:src_file.find('.')] + "_colum_fix.xlsx"
        delete_file(result_path)
        delete_file(excel_result_path)
        cnt_max = 0
        for cnt, chunk in enumerate(pd.read_csv(src_path, chunksize=1)):
            cnt_max = cnt
        for cnt, chunk in enumerate(pd.read_csv(src_path, chunksize=1)):
            new_chunk = {}
            for column in column_order:
                new_chunk[eng_kr[map[column]]] = chunk[map[column]].values[0]
            print(str(cnt) + "/" + str(cnt_max))
            overwrite_csv(pd.DataFrame([new_chunk]), result_path)
        csv_to_excel(result_path, excel_result_path)


if __name__ == '__main__':
    start = time.time()

    path = input("path: ")
    file_list = read_directory(path)

    path_list = []
    for i in file_list:
        path_list.append(path + "\\" + i)

    column_fix(path_list)

    print("time :", time.time() - start)
