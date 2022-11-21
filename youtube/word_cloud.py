import time
import csv
import pandas as pd
import os
import natsort
from konlpy.tag import Okt
import nltk
from nltk.tokenize import word_tokenize
from collections import Counter
from wordcloud import WordCloud
import fasttext


def csv_to_excel(src_dir,save_dir):
    src = pd.read_csv(src_dir, encoding='cp949')
    src.to_excel(save_dir,index=None,header=None,engine='xlsxwriter')


def wordcloud(directory, src_file):
    # nltk.download('punkt')
    # nltk.download('averaged_perceptron_tagger')
    # nltk.download('stopwords')

    model = fasttext.load_model('lid.176.ftz')
    num = 100
    directory = directory
    src_path = src_file
    okt = Okt()
    kr_list = []
    en_list = []
    count = 0
    for cnt, chunk in enumerate(pd.read_csv(src_path, chunksize=1)):
        count += 1
        print(count)
        chunk_text = str(chunk['text'].values[0])
        chunk_text = chunk_text.replace('\n','')
        language = model.predict(chunk_text)[0][0]
        if language == '__label__ko':
            noun = okt.nouns(str(chunk_text))
            for n in noun:
                kr_list.append(n)
        elif language == '__label__en':
            wordlist = word_tokenize(str(chunk_text))
            tagged = nltk.pos_tag(wordlist)
            noun = [word for word, pos in tagged if pos in['NN', 'NNP']] #명사만 추출
            noun = [w.lower() for w in noun] #대소문자 통일
            for n in noun:
                en_list.append(n)
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
    csv_to_excel(directory+'\\words_list.csv',directory+'\\words_list.xlsx')
    wc = WordCloud(font_path="./NanumSquareR.ttf",
                   background_color='white',
                   width=512,height=512,
                   max_font_size=500,
                   max_words=num)
    wc.generate_from_frequencies(dict(tags))
    wc.to_file(directory + '\\wordcloud.png')


def read_directory(directory):
    file_list = os.listdir(directory)
    file_list = natsort.natsorted(file_list)
    return file_list


if __name__ == '__main__':
    start = time.time()

    path = input("path: ")
    file_name = input("src_file_name: ")
    file_list = read_directory(path)

    for i in file_list:
        wordcloud(path + "\\" + i, path + "\\" + i + "\\" + file_name)

    print("time :", time.time() - start)

