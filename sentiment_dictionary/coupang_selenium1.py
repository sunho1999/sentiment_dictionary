from selenium import webdriver

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time

options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")

options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
options.add_experimental_option("prefs", {"prfile.managed_default_content_setting.images": 2})
driver = webdriver.Chrome(executable_path='/setiment_dictionary_project/chromedriver', options=options)


url = 'https://www.coupang.com/'
driver.get(url=url)
time.sleep(2)
search_input = driver.find_element(By.XPATH,'//*[@id="headerSearchKeyword"]')
search_input.send_keys("%s" % "신라면")

driver.find_element(By.XPATH,'/html/body/div[3]/div/header/section/div/div/form/fieldset/a').click()  # 검색창 클릭

driver.find_element(By.XPATH,'/html/body/div[3]/section/form/div[2]/div[2]/ul/li[1]/a/dl/dt/img').click()  # 이미지 클릭
time.sleep(2)
driver.switch_to.window(driver.window_handles[-1])  # 새 팝업창으로 스위칭
time.sleep(5)
for i in range(10):
    driver.find_element(By.TAG_NAME,value="body").send_keys(Keys.PAGE_DOWN)  # 내리기
    time.sleep(2)



def review_crawling():
    page_text = ""
    for i in range(5):
        text = driver.find_element(By.CLASS_NAME,
                                   value="sdp-review__article__list__review.js_reviewArticleContentContainer").text
        page_text += text + "\n"
        review = driver.find_element(By.CLASS_NAME, value = "sdp-review__article__list__survey").text
        time.sleep(2)
        page_text += review + "\n"
    time.sleep(2)
    return page_text

total_text = ""
for i in range(2,5):
    driver.find_element(By.XPATH,'/html/body/div[2]/section/div[2]/div[10]/ul[2]/li[2]/div/div[6]/section[4]/div[3]/button[{}]'.format(i)).click()  # 검색창 클릭
    time.sleep(2)
    text = review_crawling()
    time.sleep(2)
    total_text += text

f = open("./review.txt","w")
f.write(total_text)
f.close()
print(total_text)


