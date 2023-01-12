from selenium import webdriver
from selenium.webdriver.common.by import By # 요소 찾기
from selenium.webdriver.common.keys import Keys # 특수 문자 입력
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC # 명시적 대기
from selenium.webdriver.support.ui import WebDriverWait # 명시적 대기
#from hanspell import spell_checker # 맞춤법 & 띄어쓰기 교정  //// 교정된 문장 = spell_checker.check(교정 전 문장).checked
#from soynlp.normalizer import * # 의미없게 반복되는 글자 교정 ////  교정된 문장 = emoticon_normalize(교정 전 문장', num_repeats=2) & 교정된 문장 = repeat_normalize(교정 전 문장, num_repeats=2)
from PyKomoran import *
from collections import Counter
import csv
import time

def get_product_review(product_list, num_of_review, sector_name):
    result = {5: [], 4: [], 3: [], 2: [], 1: []}

    options = webdriver.ChromeOptions()
    options.add_argument('window-size=1920,1080')

    driver = webdriver.Chrome('./chromedriver', options=options)
    action = ActionChains(driver)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": """ Object.defineProperty(navigator, 'webdriver', { get: () => undefined }) """}) # 쿠팡 크롤링 방지 우회
    driver.implicitly_wait(3) # 로딩될 때까지 기다릴 시간

    f = open(sector_name + " review.csv", "w", encoding='UTF-8')

    for k in range(len(product_list)):
        driver.get(url='https://www.coupang.com/')

        search_box = driver.find_element(By.XPATH, '//*[@id="headerSearchKeyword"]')
        search_box.send_keys(product_list[k])
        search_box.send_keys(Keys.RETURN) # 검색 물품 입력

        products = driver.find_elements(By.CSS_SELECTOR, '#productList > li.search-product') 
        products[1].click() # 상품 클릭 # try-catch문 적용

        # body = driver.find_element(By.TAG_NAME, 'body')
        # for _ in range(5):
        #     body.send_keys(Keys.PAGE_DOWN)
        #     body.send_keys(Keys.PAGE_DOWN)
        #     body.send_keys(Keys.PAGE_DOWN)
        #     time.sleep(1)

        # footer = driver.find_element(By.XPATH, '//*[@id="footer"]')
        # action.move_to_element(footer)

        #driver.execute_script('window.scrollTo(0, document.body.scrollHeight);') # 화면 맨 밑으로 이동시켜 리뷰 로드

        # review_button = driver.find_element(By.NAME, 'detail')
        # review_button.click()

        driver.switch_to.window(driver.window_handles[-1]) # 새 탭으로 이동

        body = driver.find_element(By.TAG_NAME, 'body')
        for _ in range(5):
            # if(EC.visibility_of_element_located((By.XPATH, '//div[@id="learn-items"]//a[@href="/guides"]'))):
            #     break
            body.send_keys(Keys.PAGE_DOWN)
            body.send_keys(Keys.PAGE_DOWN)
            body.send_keys(Keys.PAGE_DOWN)
            time.sleep(1) # 화면 스크롤

        time.sleep(2)

        for _ in range(num_of_review//50):
            for i in range(2, 12):

                pg_button = driver.find_element(By.XPATH, '//*[@id="btfTab"]/ul[2]/li[2]/div/div[6]/section[4]/div[3]/button['+ str(i) +']')

                action.move_to_element(pg_button).perform() # 페이지 버튼 누를 수 있게 페이지 버튼으로 화면 이동

                # WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="btfTab"]/ul[2]/li[2]/div/div[6]/section[4]/div[3]/button['+ str(i) +']')))

                pg_button.click()

                time.sleep(1) # StaleElementReferenceException 방지용, 리뷰 element들을 지정하는 동안 클릭으로 인해 페이지가 올라가면 element들의 화면상 위치가 변경되면서 exception 발생 

                reviews = driver.find_elements(By.CLASS_NAME, 'sdp-review__article__list__review__content') # 리뷰 추출
                rates = driver.find_elements(By.CLASS_NAME, 'sdp-review__article__list__info__product-info__star-orange') # 평점 추출

                for idx in range(len(reviews)):
                    rate = rates[idx].get_attribute('data-rating')
                    result[int(rate)].append(reviews[idx].text) # TODO 수정

            next_button = driver.find_element(By.XPATH, '//*[@id="btfTab"]/ul[2]/li[2]/div/div[6]/section[4]/div[3]/button[12]')
            next_button.click()
            time.sleep(1) # StaleElementReferenceException 방지용

        for i in range(1,6):
            for j in range(len(result[i])):
                replaced_review = result[i][j].replace(",", "")
                replaced_review = replaced_review.replace("\n", " ")
                f.write(str(i) + ',' + replaced_review + '\n')

    f.close()





def get_standard_words(sector_name, num_of_review):
    positive_word_file = open(sector_name + " positive word.csv", "w", encoding='UTF-8')
    negative_word_file = open(sector_name + " negative word.csv", "w", encoding='UTF-8')
    result = {5: [], 4: [], 3: [], 2: [], 1: []}

    f = open(sector_name + ' review.csv', 'r', encoding='utf-8')
    review = csv.reader(f)
    for line in review:
        result[int(line[0])].append(line[1])

    f.close()

    high_reviews = []
    low_reviews = []

    for i in range(num_of_review//10): # 상위/하위 10% 리뷰
        if len(result[5]) > i:
            high_reviews.append(result[5][i])
        elif (i - len(result[5])) < len(result[4]):
            high_reviews.append(result[4][i - len(result[5])])
        else:
            break

        if len(result[1]) > i:
            low_reviews.append(result[1][i])
        elif (i - len(result[1])) < len(result[2]):
            low_reviews.append(result[2][i - len(result[1])])
        elif (i - (len(result[1]) + len(result[2]))) < len(result[3]):
            low_reviews.append(result[3][i - (len(result[1]) + len(result[2]))])
        else:
            break

    # for i in range(num_of_review//10): # 하위 10% 리뷰
    #     if len(result[1]) > i:
    #         low_reviews.append(result[1][i])
    #     elif (i - len(result[1])) < len(result[2]):
    #         low_reviews.append(result[2][i - len(result[1])])
    #     else:
    #         break

    print("num of high review:", len(high_reviews))
    print("num of low review:", len(low_reviews))

    komoran = Komoran("EXP")
    high_words = []
    low_words = []

    for high_review in high_reviews:
        temp = komoran.get_morphes_by_tags(high_review, tag_list=['VA', 'MAG', 'VV'])
        #print(temp)
        high_words += temp

    for low_review in low_reviews:
        temp = komoran.get_morphes_by_tags(low_review, tag_list=['VA', 'MAG', 'VV'])
        #print(temp)
        low_words += temp

    #print(len(high_words))
    #print(len(low_words))

    count_high_words = Counter(high_words)
    count_low_words = Counter(low_words)

    high_words = (count_high_words- count_low_words).most_common(15)
    for i in range(len(high_words)):
        positive_word_file.write(high_words[i][0] + ',' + str(high_words[i][1]) + '\n')

    low_words = (count_low_words-count_high_words).most_common(15)
    for i in range(len(low_words)):
        negative_word_file.write(low_words[i][0] + ',' + str(low_words[i][1]) + '\n')

    positive_word_file.close()
    negative_word_file.close()

    return result

get_product_review(["신라면"], 1500, "식품") # num_of_review 50배수로
result = get_standard_words("식품", 50)
for i in range(len(result)):
    print(result[i])
    print("------------------------")

# print("5점 리뷰 :", len(result[5]))
# print("4점 리뷰 :", len(result[4]))
# print("3점 리뷰 :", len(result[3]))
# print("2점 리뷰 :", len(result[2]))
# print("1점 리뷰 :", len(result[1]))

# 평점 높은 상품 + 평점 낮은 상품을 섞어서 리뷰 크롤링 해야 될듯
# 상품 페이지 url을 리스트에 넣어서 넘겨주면 해당 페이지의 리뷰 1000개씩 크롤링해서 기준 단어 선정해야할 듯
# 기준 단어 품사는 극성이 잘 나타나는 형용사, 동사로

# 리뷰 내용 뿐만 아니라 제목도 크롤링되게 추가 필요 -> 할 필요 없을 듯
# TODO try-catch로 예외 처리 필요 (리뷰가 더 없다거나 등등..)
# 한 페이지에 모두 리뷰 내용이 없는 경우 멈추는 버그 수정 필요 -> implicitly_wait 시간 줄임
# TODO 평점별 보기 눌러서 해당하는 1점 / 5점 평점 크롤링하기