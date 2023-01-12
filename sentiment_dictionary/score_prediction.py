# -*-coding:utf-8-*-

import json
from konlpy.tag import Okt
import numpy as np
import scipy as sp # 통계 함수 사용
import scipy.stats # 통계 함수 사용

class KMUDIC():

    def data_list(wordname):

        with open('./SentiWord.json', encoding='utf-8-sig', mode='r') as f:
            data = json.load(f)
        result = ["None", 0]
        for i in range(0, len(data.get("data"))):
            if data.get("data")[i]['text'] == wordname:
                result.pop()
                result.pop()
                result.append(data.get("data")[i]['text'])
                result.append(data.get("data")[i]['score'])

        r_word = result[0]
        s_word = result[1]

        if s_word == "None":
            print("아직 사전에 없는 단어가 포함되어있습니다.")
        else:
            print('어근 : ' + r_word)
            print('극성 : ' + str(s_word))
            return s_word

    def f_z_score(data): # z-score 함수 생성
        mean = np.mean(data) #평균
        std = np.std(data)   #표준편차
        z_scores = [(y-mean)/std for y in data] #z-score
        return z_scores



if __name__ == "__main__":

    ksl = KMUDIC
    okt = Okt()
    print("사전에 단어가 없는 경우 결과가 None으로 나타납니다!!!")
    print("종료하시려면 #을 입력해주세요!!!")
    print("-2:매우 부정, -1:부정, 0:중립 , 1:긍정, 2:매우 긍정")
    print("\n")
    dic = {"-2":0,"-1":0,"0":0,"1":0,"2":0}
    while (True):
        total_score = 0

        wordname = input("리뷰를 입력하세요 : ")
        total_text = []
        wordname = wordname.strip()
        line = okt.pos(wordname, stem=True, join=True)
        print(line)
        new_text = []
        for i in line:
            text_tag = i.split("/")  # '편리하다/Adjective'
            if text_tag[1] == "Adjective":
                new_text.append(text_tag[0])
        print(new_text)
        if wordname != "#":
            cnt = 0
            for i in new_text:
                cnt +=1
                total_score += ksl.data_list(i)
            star = total_score / cnt
            print("total_score : ",total_score)
            print("평균: ",star)
            if star <= 2 and star >= 1.2:
                print("예측한 별점은 5점입니다.")
            elif star < 1.2 and star >0.4:
                print("예측한 별점은 4점입니다.")
            elif star <= 0.4 and star > -0.4:
                print("예측한 별점은 3점입니다.")
            elif star < -0.4 and star >= -1.2:
                print("예측한 별점은 2점입니다.")
            elif star < -1.2 and star >= -2:
                print("예측한 별점은 1점입니다.")

            print("\n")

        elif wordname == "#":
            print("\n이용해주셔서 감사합니다~ :)")
            break



# 1점 ~5점 짜리를 우리가 갖고있는 사전에 대입을 했을 때 , 점수가 나옴
# 토탈점수




