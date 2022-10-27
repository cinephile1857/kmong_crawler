import time
import csv
import System
import pandas as pd
import os
from datetime import datetime
import googletrans
from konlpy.tag import Okt
import nltk
from nltk.tokenize import word_tokenize
from collections import Counter
from wordcloud import WordCloud


def comment_parser(directory):
    pid = os.getpid()
    print("====#%d comment api parsing start====" % pid)
    comment_dataframe = pd.DataFrame({
        'comment_or_reply': [],
        'comment_id': [],
        'reply_id': [],
        'reply_to_reply_id': [],
        'create_time': [],
        'user_id': [],
        'sec_uid': [],
        'user_unique_id': [],
        'user_nickname': [],
        'like_count': [],
        'reply_count': [],
        'author_like': [],
        'language': [],
        'text': []
    })
    print("#%d comment api convert csv..." % pid)
    response_directory = System.read_directory(directory)
    for each_response_path in response_directory:
        if 'comment' in each_response_path:
            comment_response = System.read_dictionary(directory + '\\' + each_response_path)
            comment_list = comment_response['comments']
            if comment_list != None:
                for comment in comment_list:
                    new_data = {
                        'comment_or_reply': "comment",
                        'comment_id': "'" + str(comment['cid']),
                        'reply_id': "'0",
                        'reply_to_reply_id': "'0",
                        'create_time': datetime.fromtimestamp(int(comment['create_time'])),
                        'user_id': "'" + str(comment['user']['uid']),
                        'sec_uid': comment['user']['sec_uid'],
                        'user_unique_id': comment['user']['unique_id'],
                        'user_nickname': comment['user']['nickname'],
                        'like_count': comment['digg_count'],
                        'reply_count': comment['reply_comment_total'],
                        'author_like': comment['is_author_digged'],
                        'language': comment['comment_language'],
                        'text': comment['text']
                        }
                    comment_dataframe = comment_dataframe.append(new_data, ignore_index=True)
    comment_save_path = directory + '\\' + 'result_c.csv'
    comment_dataframe.to_csv(comment_save_path, mode='w', index=False, encoding='utf-8-sig')
    print("#%d converted api delete..." % pid)
    for each_response_path in response_directory:
        if 'comment' in each_response_path:
            System.delete_file(directory + '\\' + each_response_path)


def reply_parser(directory):
    pid = os.getpid()
    print("====#%d reply api parsing start====" % pid)
    reply_dataframe = pd.DataFrame({
        'comment_or_reply': [],
        'comment_id': [],
        'reply_id': [],
        'reply_to_reply_id': [],
        'create_time': [],
        'user_id': [],
        'sec_uid': [],
        'user_unique_id': [],
        'user_nickname': [],
        'like_count': [],
        'reply_count': [],
        'author_like': [],
        'language': [],
        'text': []
    })
    print("#%d reply api convert csv..." % pid)
    response_directory = System.read_directory(directory)
    for each_response_path in response_directory:
        print(each_response_path)
        if 'reply' in each_response_path:
            reply_response = System.read_dictionary(directory + '\\' + each_response_path)
            reply_list = reply_response['comments']
            if reply_list != None:
                for reply in reply_list:
                    new_data = {
                        'comment_or_reply': "reply",
                        'comment_id': "'" + str(reply['cid']),
                        'reply_id': "'" + str(reply['reply_id']),
                        'reply_to_reply_id': "'" + str(reply['reply_to_reply_id']),
                        'create_time': datetime.fromtimestamp(int(reply['create_time'])),
                        'user_id': "'" + str(reply['user']['uid']),
                        'sec_uid': reply['user']['sec_uid'],
                        'user_unique_id': reply['user']['unique_id'],
                        'user_nickname': reply['user']['nickname'],
                        'like_count': reply['digg_count'],
                        'reply_count': 0,
                        'author_like': reply['is_author_digged'],
                        'language': reply['comment_language'],
                        'text': reply['text']
                        }
                    reply_dataframe = reply_dataframe.append(new_data, ignore_index=True)
    reply_save_path = directory + '\\' + 'result_r.csv'
    reply_dataframe.to_csv(reply_save_path, mode='w', index=False, encoding='utf-8-sig')
    print("#%d converted api delete..." % pid)
    for each_response_path in response_directory:
        if 'reply' in each_response_path:
            System.delete_file(directory + '\\' + each_response_path)


def integrate_comment_and_reply(directory):
    pid = os.getpid()
    print("====#%d integration start====" % pid)
    result_path = directory + "\\result.csv"
    System.delete_file(result_path)
    for cnt_comment, chunk_comment in enumerate(pd.read_csv(directory + '\\result_c.csv', chunksize=1)):
        if chunk_comment['reply_count'].any() == True:
            comment_id = chunk_comment['comment_id'].values[0]
            chunk_comment = chunk_comment.drop('comment_id', axis=1)
            chunk_comment = chunk_comment.drop('sec_uid', axis=1)
            chunk_comment = chunk_comment.drop('reply_id', axis=1)
            chunk_comment = chunk_comment.drop('reply_to_reply_id', axis=1)
            chunk_comment = chunk_comment.drop('user_id', axis=1)
            System.overwrite_csv(chunk_comment,result_path)
            for cnt_reply, chunk_reply in enumerate(pd.read_csv(directory + '\\result_r.csv', chunksize=1)):
                reply_id = chunk_reply['reply_id'].values[0]
                if comment_id == reply_id:
                    chunk_reply = chunk_reply.drop('comment_id', axis=1)
                    chunk_reply = chunk_reply.drop('sec_uid', axis=1)
                    chunk_reply = chunk_reply.drop('reply_id', axis=1)
                    chunk_reply = chunk_reply.drop('reply_to_reply_id', axis=1)
                    chunk_reply = chunk_reply.drop('user_id', axis=1)
                    System.overwrite_csv(chunk_reply, result_path)
        else:
            chunk_comment = chunk_comment.drop('comment_id', axis=1)
            chunk_comment = chunk_comment.drop('sec_uid', axis=1)
            chunk_comment = chunk_comment.drop('reply_id', axis=1)
            chunk_comment = chunk_comment.drop('reply_to_reply_id', axis=1)
            chunk_comment = chunk_comment.drop('user_id', axis=1)
            System.overwrite_csv(chunk_comment, result_path)
    print("====#%d integration finish====" % pid)


def translate(directory):
    # The maximum character limit on a single text is 15k.
    # You can get about 1000 requests / hour without hitting the req/IP block limit.
    # Also, individual requests are limited to less than 5000 characters per request.

    name = ['comment_or_reply', 'create_time', 'user_unique_id', 'user_nickname', 'like_count', 'reply_count',
            'author_like', 'language', 'text']

    translator = googletrans.Translator()
    source_path = directory + "\\result.csv"
    translate_path = directory + "\\result_t.csv"
    cnt_max = 0
    for cnt, chunk in enumerate(pd.read_csv(source_path, chunksize=1)):
        cnt_max = cnt

    if not os.path.exists(translate_path):
        for cnt, chunk in enumerate(pd.read_csv(source_path, chunksize=1)):
            time.sleep(1)
            chunk['translate'] = ""
            if chunk['language'].values[0] != 'ko' and pd.isna(chunk['language'].values[0]) == False:
                if "zh" in chunk['language'].values[0]:
                    try:
                        translate = translator.translate(str(chunk['text'].values[0]), dest='ko').text
                        chunk['translate'] = translate
                    except ValueError:
                        translate = chunk['text'].values[0]
                        chunk['translate'] = translate
                else:
                    try:
                        translate = translator.translate(str(chunk['text'].values[0]),
                                                         src=chunk['language'].values[0], dest='ko').text
                        chunk['translate'] = translate
                    except ValueError:
                        translate = chunk['text'].values[0]
                        chunk['translate'] = translate
            print(str(cnt)+"/"+str(cnt_max))
            System.overwrite_csv(chunk, translate_path)
    else:
        for cnt, chunk in enumerate(pd.read_csv(translate_path, chunksize=1)):
            skip_row = cnt+2
        for cnt, chunk in enumerate(pd.read_csv(source_path, names=name, skiprows=skip_row, chunksize=1)):
            #time.sleep(1)
            chunk['translate'] = ""
            if chunk['language'].values[0] != 'ko' and pd.isna(chunk['language'].values[0]) == False:
                if "zh" in chunk['language'].values[0]:
                    try:
                        translate = translator.translate(str(chunk['text'].values[0]), dest='ko').text
                        chunk['translate'] = translate
                    except ValueError:
                        translate = chunk['text'].values[0]
                        chunk['translate'] = translate
                else:
                    try:
                        translate = translator.translate(str(chunk['text'].values[0]),
                                                         src=chunk['language'].values[0], dest='ko').text
                        chunk['translate'] = translate
                    except ValueError:
                        translate = chunk['text'].values[0]
                        chunk['translate'] = translate
            print(str(cnt)+"/"+str(cnt_max-skip_row))
            System.overwrite_csv(chunk, translate_path)


def user_info_integration(directory):
    pid = os.getpid()
    print("====#%d user info integration start====" % pid)
    info_path = directory + "\\user_list_info.csv"
    source_path = directory + "\\result.csv"
    result_path = directory + "\\result_i.csv"
    System.delete_file(result_path)
    cnt_max = 0
    for cnt, chunk in enumerate(pd.read_csv(source_path, chunksize=1)):
        cnt_max = cnt
    for src_cnt, src_chunk in enumerate(pd.read_csv(source_path, chunksize=1)):
        user_id = src_chunk['user_unique_id'].values[0]
        src_chunk['follower_count'] = ""
        src_chunk['following_count'] = ""
        src_chunk['heart_count'] = ""
        src_chunk['video_count'] = ""
        for info_cnt, info_chunk in enumerate(pd.read_csv(info_path, chunksize=1)):
            if info_chunk['user_id'].values[0] == user_id:
                src_chunk['follower_count'] = info_chunk['follower_count'].values[0][1:]
                src_chunk['following_count'] = info_chunk['following_count'].values[0][1:]
                src_chunk['heart_count'] = info_chunk['heart_count'].values[0][1:]
                src_chunk['video_count'] = info_chunk['video_count'].values[0][1:]
        print("#" + str(pid) + ": " + str(src_cnt) + "/" + str(cnt_max))
        System.overwrite_csv(src_chunk, result_path)


def user_info_integration_translate(directory):
    pid = os.getpid()
    print("====#%d user info integration start====" % pid)
    info_path = directory + "\\user_list_info.csv"
    source_path = directory + "\\result_t.csv"
    result_path = directory + "\\result_i.csv"
    System.delete_file(result_path)
    cnt_max = 0
    for cnt, chunk in enumerate(pd.read_csv(source_path, chunksize=1)):
        cnt_max = cnt
    for src_cnt, src_chunk in enumerate(pd.read_csv(source_path, chunksize=1)):
        user_id = src_chunk['user_unique_id'].values[0]
        src_chunk['follower_count'] = ""
        src_chunk['following_count'] = ""
        src_chunk['heart_count'] = ""
        src_chunk['video_count'] = ""
        for info_cnt, info_chunk in enumerate(pd.read_csv(info_path, chunksize=1)):
            if info_chunk['user_id'].values[0] == user_id:
                src_chunk['follower_count'] = info_chunk['follower_count'].values[0][1:]
                src_chunk['following_count'] = info_chunk['following_count'].values[0][1:]
                src_chunk['heart_count'] = info_chunk['heart_count'].values[0][1:]
                src_chunk['video_count'] = info_chunk['video_count'].values[0][1:]
        print("#" + str(pid) + ": " + str(src_cnt) + "/" + str(cnt_max))
        System.overwrite_csv(src_chunk, result_path)


def wordcloud(directory):
    # nltk.download('punkt')
    # nltk.download('averaged_perceptron_tagger')
    # nltk.download('stopwords')
    pid = os.getpid()
    print("====#%d wordcloud start====" % pid)

    num = 100

    src_path = directory + "\\" + "result_t.csv"
    translation = True
    if not os.path.exists(src_path):
        src_path = directory + "\\" + "result.csv"
        translation = False
    okt = Okt()
    kr_list = []
    en_list = []
    for cnt, chunk in enumerate(pd.read_csv(src_path, chunksize=1)):
        if chunk['language'].values[0] == 'ko':
            text = chunk['text'].values[0]
            noun = okt.nouns(str(text))
            for n in noun:
                kr_list.append(n)
        elif chunk['language'].values[0] == 'en':
            text = chunk['text'].values[0]
            wordlist = word_tokenize(str(text))
            tagged = nltk.pos_tag(wordlist)
            noun = [word for word, pos in tagged if pos in['NN', 'NNP']] #명사만 추출
            noun = [w.lower() for w in noun] #대소문자 통일
            for n in noun:
                en_list.append(n)
        else:
            if translation:
                text = chunk['text'].values[0]
                noun = okt.nouns(str(text))
                for n in noun:
                    kr_list.append(n)
            else:
                pass
    with open("./stopword_kr.txt", encoding='utf-8') as f:
        kr_stopwords = f.readlines()
    kr_stopwords = [x.strip() for x in kr_stopwords]
    new_kr_list = [word for word in kr_list if not word in kr_stopwords]

    en_stopwords = nltk.corpus.stopwords.words('english')
    with open("./stopword_kr.txt", encoding='utf-8') as f:
        en_stopwords_txt = f.readlines()
    en_stopwords = en_stopwords + en_stopwords_txt
    new_en_list = [w for w in en_list if w not in en_stopwords and w.isalnum()]

    word_list = new_kr_list + new_en_list
    counts = Counter(word_list)
    tags = counts.most_common(num)
    tag_list = {}
    for i in tags:
        tag_list[i[0]] = i[1]
    with open(directory+'\\words_list.csv', 'w', newline="") as f:
        writer = csv.writer(f)
        for k, v in tag_list.items():
            writer.writerow([k, v])

    wc = WordCloud(font_path="./NanumSquareR.ttf",
                   background_color='white',
                   width=512,height=512,
                   max_font_size=500,
                   max_words=num)
    wc.generate_from_frequencies(dict(tags))
    wc.to_file(directory + '\\wordcloud.png')

    print("#" + str(pid) + " is finish")







