
from collections import Counter
import time
import json
from konlpy.tag import Okt
from soynlp.vectorizer import sent_to_word_contexts_matrix
from soynlp import DoublespaceLineCorpus
from soynlp.word import WordExtractor
from soynlp.normalizer import *
from soynlp.word import pmi as pmi_func
from soynlp.tokenizer import RegexTokenizer
from pprint import pprint
import pandas as pd
import numpy as np
#from hanspell import spell_checker # 맞춤법 & 띄어쓰기 교정  //// 교정된 문장 = spell_checker.check(교정 전 문장).checked
#from soynlp.normalizer import * # 의미없게 반복되는 글자 교정 ////  교정된 문장 = emoticon_normalize(교정 전 문장', num_repeats=2) & 교정된 문장 = repeat_normalize(교정 전 문장, num_repeats=2)


class KnuSL():

    def data_list(wordname):
        with open('data/SentiWord_info.json', encoding='utf-8-sig', mode='r') as f:
            data = json.load(f)
        result = ['None', 'None']
        for i in range(0, len(data)):
            if data[i]['word'] == wordname:
                result.pop()
                result.pop()
                result.append(data[i]['word_root'])
                result.append(data[i]['polarity'])

        r_word = result[0]
        s_word = result[1]

        print('어근 : ' + r_word)
        print('극성 : ' + s_word)

        return r_word, s_word


# if __name__ == "__main__":
#
#     ksl = KnuSL
#
#     print("\nKNU 한국어 감성사전입니다~ :)")
#     print("사전에 단어가 없는 경우 결과가 None으로 나타납니다!!!")
#     print("종료하시려면 #을 입력해주세요!!!")
#     print("-2:매우 부정, -1:부정, 0:중립 or Unkwon, 1:긍정, 2:매우 긍정")
#     print("\n")
#
#     while (True):
#         wordname = input("word : ")
#         wordname = wordname.strip(" ")
#         if wordname != "#":
#             print(ksl.data_list(wordname))
#             print("\n")
#
#
#         elif wordname == "#":
#             print("\n이용해주셔서 감사합니다~ :)")
#             break


def setiment_Score(): # 감성어휘의 극성 값 계산
    high_review = ["맛있","저렴","착한"]
    total_SentimentScore = []
    ksl = KnuSL
    total_sum =0
    for ist in high_review:
        for word in ist:
            polarity_score_Ti = word.strip(" ")
            polarity_score = ksl.data_list(polarity_score_Ti)
            total_sum  += polarity_score
        SentimentScore = total_sum/len(ist) # 각 리뷰에 출현하는 감성 어휘의 극성 값
        total_SentimentScore.append(SentimentScore)
    return  total_SentimentScore



def fileread(): # 리뷰 데이터파일 읽고 긍정 부정 분류후 데이터 전처리

    file_path = "/Users/sunho99/PycharmProjects/python_Project/setiment_dictionary_project/text1.txt"
    positive_reviews = []
    negative_reviews = []
    total_reviews = []
    # o = open('/Users/sunho99/PycharmProjects/python_Project/setiment_dictionary_project/text1.txt', 'w')

    # with open(file_path) as t:
    #     lines = t.readlines()
    # for i in lines:
    #     i = i.replace("	",",")
    #     o.write(i)
    # o.close()
    with open(file_path) as f:
        lines = f.readlines()

    for i in lines:
        if i[0] == "5" or i[0] == "4":
            positive_reviews.append(i[2:].strip("\n"))
        else:
            negative_reviews.append(i[2:].strip("\n"))
        total_reviews.append(i[2:].strip("\n"))
    okt = Okt()
    normalization_positive_review = [] # 평점 1~3점
    normalization_negative_review = [] # 평점 4~5점
    # 문장 이상한거 수정 및 정규화 진행 전처리
    for review in positive_reviews:  # 긍정리뷰
        clean_review = emoticon_normalize(review,num_repeats=3) #반복되는 이모티콘 정리 최대 3회
        clean_review = repeat_normalize(clean_review,num_repeats=3) # 반복되는 문구 정리 최대 3회
        clean_review = only_hangle(clean_review) # 리뷰중 영어 제외
        clean_review = okt.normalize(clean_review) # 정리
        normalization_positive_review.append(clean_review)
    for review in negative_reviews: # 부정리뷰
        clean_review = emoticon_normalize(review, num_repeats=3)  # 반복되는 이모티콘 정리 최대 3회
        clean_review = repeat_normalize(clean_review, num_repeats=3)  # 반복되는 문구 정리 최대 3회
        clean_review = only_hangle(clean_review)  # 리뷰중 영어 제외
        clean_review = okt.normalize(clean_review)  # 정리
        normalization_negative_review.append(clean_review)
    with open("/Users/sunho99/PycharmProjects/python_Project/setiment_dictionary_project/positive_review.txt", "w") as positive_file_path:
        for i in positive_reviews:
            positive_file_path.write(i+"\n")
    with open("/Users/sunho99/PycharmProjects/python_Project/setiment_dictionary_project/negative_review.txt", "w") as negative_file_path:
        for i in negative_reviews:
            negative_file_path.write(i+"\n")

    return normalization_positive_review,normalization_negative_review

def total_review_toknizer():
    file_path = "/Users/sunho99/PycharmProjects/python_Project/setiment_dictionary_project/text1.txt"
    okt = Okt()
    total_reviews = []
    with open(file_path) as f:
        lines = f.readlines()
    with open(file_path) as f:
        lines = f.readlines()

    for i in lines:
        total_reviews.append(i[2:].strip("\n"))

    okt = Okt()
    normalization_total_review = [] # 평점 1~3점

    # 문장 이상한거 수정 및 정규화 진행 전처리
    for review in total_reviews:  # 긍정리뷰
        clean_review = emoticon_normalize(review,num_repeats=3) #반복되는 이모티콘 정리 최대 3회
        clean_review = repeat_normalize(clean_review,num_repeats=3) # 반복되는 문구 정리 최대 3회
        clean_review = only_hangle(clean_review) # 리뷰중 영어 제외
        clean_review = okt.normalize(clean_review) # 정리
        normalization_total_review.append(clean_review)

    with open("/Users/sunho99/PycharmProjects/python_Project/setiment_dictionary_project/total_review.txt", "w") as positive_file_path:
        for i in total_reviews:
            positive_file_path.write(i+"\n")

    return normalization_total_review

def text_TAG(normalization_review):
    okt = Okt()

    pos_reviews = []
    for review in normalization_review: # 형태소 분석
        clean_review = okt.pos(review[2:], stem=True,join=True)

        pos_reviews.append(clean_review)
    # {'Adjective': '형용사',
    #  'Adverb': '부사',
    #  'Alpha': '알파벳',
    #  'Conjunction': '접속사',
    #  'Determiner': '관형사',
    #  'Eomi': '어미',
    #  'Exclamation': '감탄사',
    #  'Foreign': '외국어, 한자 및 기타기호',
    #  'Hashtag': '트위터 해쉬태그',
    #  'Josa': '조사',
    #  'KoreanParticle': '(ex: ㅋㅋ)',
    #  'Noun': '명사',
    #  'Number': '숫자',
    #  'PreEomi': '선어말어미',
    #  'Punctuation': '구두점',
    #  'ScreenName': '트위터 아이디',
    #  'Suffix': '접미사',
    #  'Unknown': '미등록어',
    #  'Verb': '동사'}
    tag_reviews = []
    for i in pos_reviews: #Adjective 동사, 형용사 가져오기
        for j in i:
            text_tag = j.split("/") #'편리하다/Adjective'
            if text_tag[1] == "Adjective" :
                tag_reviews.append(text_tag[0])
    total_tag_reviews =[]
    #
    count_tag_reviews = Counter(tag_reviews)
    return count_tag_reviews
def text_tokenizer(): #리뷰 데이터 토크나이저 진행
    okt = Okt()
    f = open("/Users/sunho99/PycharmProjects/python_Project/setiment_dictionary_project/negative_review.txt", 'r') # 기본 긍,부정 txt
    lines = f.readlines()
    total_text = []
    for line in lines:
        line = line.strip()  # 줄 끝의 줄 바꿈 문자를 제거한다.
        line = okt.pos(line, stem=True, join=True)
        new_text = []
        for i in line:
            text_tag = i.split("/")  # '편리하다/Adjective'
            new_text.append(text_tag[0])
        total_text.append(new_text)
    f.close()
    with open("/Users/sunho99/PycharmProjects/python_Project/setiment_dictionary_project/negative_tokenizer_review.txt", "w") as file_path: # 긍,부정 리뷰 토큰화 진행
        for i in total_text:
            text = ""
            for j in i:
                text = text + j + " "
            file_path.write(text + "\n")
def word_tokenizer(count_reviews,state):
    okt = Okt()
    most_relateds = []
    pmi_dict = {}
    corpus_path = "/Users/sunho99/PycharmProjects/python_Project/setiment_dictionary_project/"+state+"_tokenizer_review.txt"
    corpus = DoublespaceLineCorpus(corpus_path,iter_sent=True) #corpus의 길이를 계산할 때, 문장 단위로 계산이 됨
    word_extractor = WordExtractor() #단어 추출기
    word_extractor.train(corpus)
    tokenizer = RegexTokenizer()

    x, idx2vocab = sent_to_word_contexts_matrix(
        corpus,
        windows=4,
        min_tf=10,
        tokenizer=tokenizer,  # (default) lambda x:x.split(),
        dynamic_weight=False,
        verbose=True)
    pmi, px, py = pmi_func(
        x,
        min_pmi=0,
        alpha=0.0001,
        beta=0.75,
    )
    vocab2idx = {vocab: idx for idx, vocab in enumerate(idx2vocab)}
    for text,cnt in count_reviews:

        query = vocab2idx[text]

        submatrix = pmi[query, :].tocsr()  # get the row of query
        contexts = submatrix.nonzero()[1]  # nonzero() return (rows, columns)
        pmi_i = submatrix.data

        most_relateds = [(idx, pmi_ij) for idx, pmi_ij in zip(contexts, pmi_i)]
        most_relateds = sorted(most_relateds, key=lambda x: -x[0])
        most_relateds = [(idx2vocab[idx], pmi_ij) for idx, pmi_ij in most_relateds]

        # pprint(most_relateds)
        for text,pmi_score in most_relateds: #pmi값중 text,pmi_score추출
            a = okt.pos(text)
            for pos_text, tag in a: #pmi계산 한 토큰 중 형용사만 추가.
                if tag == "Adjective":
                    if pos_text not in pmi_dict:
                        pmi_dict[pos_text] = pmi_score
                    pmi_dict[pos_text] += pmi_score
    # pmi_dict = sorted(pmi_dict.items(), key=lambda x:x[1], reverse= True)

    return pmi_dict

def calculateSOPMI(positive_pmi_dict, negative_pmi_dict):
    result = []
    for key, _ in positive_pmi_dict.items():
        if key in negative_pmi_dict:
            so_pmi = positive_pmi_dict[key] - negative_pmi_dict[key]
            result.append((key, so_pmi))

    return result

positive_normalization_review, negative_normalization_review = fileread() # 정제전 토탈 리뷰

total_review = total_review_toknizer() # 전처리

positive_count_reviews = text_TAG(positive_normalization_review)  # 정제후 품사태깅된 리뷰
negative_count_reviews = text_TAG(negative_normalization_review)

positive_count_reviews = positive_count_reviews - negative_count_reviews
negative_count_reviews = negative_count_reviews - positive_count_reviews
positive_count_reviews = positive_count_reviews.most_common(20)
negative_count_reviews = negative_count_reviews.most_common(20)
text_tokenizer()
print(positive_count_reviews)
print(negative_count_reviews)
positive_pmi_dict = word_tokenizer(positive_count_reviews,"total") # text_tokenizer() #리뷰 데이터 토크나이저 진행
negative_pmi_dict = word_tokenizer(negative_count_reviews,"total") # text_tokenizer() #리뷰 데이터 토크나이저 진행
# 않다, 같다
#
result = calculateSOPMI(positive_pmi_dict,negative_pmi_dict)

result = sorted(result,key=lambda x:x[1], reverse= True)
#
column_name = ['text', 'score']
df = pd.DataFrame(result,columns=column_name)

#      text     score
# 0      좋다  8.251249
# 1     빠르다  6.580951
# 2     가볍다  6.106031
# 3    튼튼하다  6.095806
# 4    만족하다  5.797576
df["score"] = (df["score"] - df["score"].mean())/df["score"].std()
# print(df)




data = np.array_split(df, 5) # -2,-1,0,1,2 점수화를 위해서 5단계로 분할.
# 좋지 않다. <=> 좋다.
# 편하게 뿌리는 스타일이 좋지않았습니다.
# 편하다 뿌리다 스타일 이  좋다 않다..  (2점) *-1
#좋다 않다 -> 좋다 -> good -> bad ->나쁘다.
# 않다. 못

for i in range(5): # pmi값 기준으로 점수화
    if i == 0:
        data[i]['score'] = 2
    elif i == 1:
        data[i]['score'] = 1
    elif i== 2:
        data[i]['score'] = 0
    elif i == 3:
        data[i]['score'] = -1
    elif i == 4:
        data[i]['score'] = -2

total_df = pd.concat([data[0],data[1],data[2],data[3],data[4]])
total_df.to_json("/Users/sunho99/PycharmProjects/python_Project/setiment_dictionary_project/SentiWord.json", orient = 'table',force_ascii=False,indent=4)