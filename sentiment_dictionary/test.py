import json
from konlpy.tag import Okt

f = open("/Users/sunho99/PycharmProjects/python_Project/setiment_dictionary_project/text1.txt", 'r') # 기본 긍,부정 txt
lines = f.readlines()
total_sum = 0
total_text = []
dict = {"very_negative":0,"negative":0,"neutral":0,"positive":0,"very_positive":0}
for line in lines:
    score = line[0]  # 줄 끝의 줄 바꿈 문자를 제거한다.
    review = line[2:]
    if score == "5":
        dict["very_positive"] +=1
    elif score == "4":
        dict["positive"] += 1
    elif score == "3":
        dict["neutral"] += 1
    elif score == "2":
        dict["negative"] += 1
    elif score == "1":
        dict["very_negative"] += 1
    total_sum += 1
f.close()

per_very_positive = dict["very_positive"]/total_sum * 100
per_positive = dict["positive"]/total_sum * 100
per_neutral = dict["neutral"]/total_sum * 100
per_negative = dict["negative"]/total_sum * 100
per_very_negative = dict["very_negative"]/total_sum * 100

per_positive_total = per_positive + per_very_positive
per_negative_total = per_negative + per_neutral + per_very_negative

print(per_positive_total)
print(per_negative_total)


