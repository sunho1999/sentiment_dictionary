import time
import sys
import argparse
import pandas as pd
import requests
from bs4 import BeautifulSoup
import json

headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"}

def parse_arg(args):
    parser = argparse.ArgumentParser(description = 'search keyword in coupang website')
    parser.add_argument('--keyword', default = '', type = str)
    parser.add_argument('--email', default = '', type = str)

    return parser.parse_args(args)

def getProducts(ul,keyword): #상품 url,이름,가격
    lis = ul.findAll("li", {"class":"search-product"}) #각 아이템 추출
    
    result = [] #결과 리스트 
    result_inside = [] #상품 상세 결과 리스트
    
    for (idx, item) in enumerate(lis):
        #url
        a = item.find("a", {"class": "search-product-link"})
        url = a.get('href')
        if 'sourceType=srp_product_ads' in url:
            continue
        #name
        div_name = item.find("div", {"class":"name"})
        name = div_name.getText()
        
        #image
        dt_image = item.find("dt", {"class":"image"})
        image = dt_image.find("img").get('src')
        data_image = dt_image.find("img").get('data-img-src')
    
        #price
        # <strong class="price-value">34,310</strong>
        price = item.find("strong", {"class":"price-value"})
        if price is None:
            prices = item.find("div", {"class":"used-product-info"})
            if prices is not None:
                prices = prices.findAll("strong")
                if prices is not None and len(prices)>0:
                    price = prices[len(prices)-1].getText() #strong 개수 나타나는게 있음
        else:
            price = price.getText()
        
        
        #판매자, 상세이미지 정보
        url = 'https://www.coupang.com' + url
#         print(url)
        data = requests.get(url, headers=headers).content
        bs = BeautifulSoup(data, "html.parser") #여기서 따오면 돼   
        parsed1 = str(bs).split('exports.sdp = ')        
        if len(parsed1) > 1:
            inside_info = ['','','','','', '','','','','','','','','','','','','','']
            parsed2 = parsed1[1].split('};')
            json_parsed = json.loads(parsed2[0] + '}')
            
            ## 판매자 : 첫번째 컬럼
            seller = json_parsed['vendor']
            if seller is not None:
                seller = str(seller)
                seller = seller.split(':')
                seller = seller[1].split(',')
                seller = seller[0]
                inside_info[0] = seller
    
            #상세 이미지 : 2-9 컬럼 
            for (idx, image) in enumerate(json_parsed['images']):
                if idx >= 8:
                    break
                inside_info[idx+1] = image['detailImage']
        else:
            inside_info = ['','','','','','','', '','','','','','','','', '','','','']            
        
        ##상품평 가져오기 : 10-19 컬럼
        non = str(url).split('products/')
        non = non[1].split('?itemId=')
        item1 = non[0] # productId

        # 리뷰 페이지에서 리뷰 있는지 찾기 
        new_url = f'https://www.coupang.com/vp/product/reviews?productId={item1}&page=1size=5&sortBy=ORDER_SCORE_ASC&ratings=&q=&viRoleCode=3&ratingSummary=true'
        data = requests.get(new_url, headers=headers).content
        bs = BeautifulSoup(data, "html.parser") 
        find_comment = bs.findAll("div", {"class":"sdp-review__article__list__review__content js_reviewArticleContent"}) #애가 있어야 된다고 좀 
        #상품평이 있으면 
        if  find_comment != []: #find_comment is not None 
            ## summary page - 페이지 불러오기 
            summary = f'https://www.coupang.com/vp/product/reviews/summaries?productId={item1}&viRoleCode=3'
            data = requests.get(summary, headers=headers).content
            bs = BeautifulSoup(data, "html.parser") #여기서 따오면 돼
            ##  summary page - 상품평 전체 수 
            if bs is not None :
                num_comment = bs.find("div", {"class":"sdp-review__average__total-star__info-count"})
                num_comment = num_comment.getText() #있으면 몇개까지 있는지 알아내
                num_comment = num_comment.replace(',','')
                num_page = 1 + ((int(num_comment)-1) // 5) #페이지 계산

                ## 상품평 text 불러오기 -
                # url 만들기 
                for j in range(num_page):
                    # 리뷰 페이지 - text 긁어오는 곳 
                    new_url = f'https://www.coupang.com/vp/product/reviews?productId={item1}&page={j}&size=5&sortBy=ORDER_SCORE_ASC&ratings=&q=&viRoleCode=3&ratingSummary=true'
                    data = requests.get(new_url, headers=headers).content
                    bs = BeautifulSoup(data, "html.parser") 
                    table = bs.findAll("div", {"class":"sdp-review__article__list__review__content js_reviewArticleContent"})#싹 찾아 
                    comments = []
                    for t in (table):
                        comment = t.getText()
                        comment = comment.strip()
                        comment = comment.replace('\n',' ') #엔터만 고치면 됨 
                        comments.append(comment)
                for c in range(len(comments)):
                    if c >= 10:
                        break
                    inside_info[c+9] = comments[c]
                     
        new_url_result = using_new_url(url) #배송정보, 판매자 정보, 이미지 등등 
        
#         # to return 
        if f'{keyword}' in name.lower() :             
            result.append([url, name, image, data_image, price]+inside_info) #url, name, image, data_image, price, (seller, detail image 8, 리뷰 10)#19개 
            result_inside.append(new_url_result) #shipping, ceo, email, phone, address, bizNum, ecommReportNum + 설명이미지4개

    return result, result_inside

#배송정보, 판매자 정보, 이미지 등등 
def using_new_url(url) : 
    #url 만들기 
    non = str(url).split('products/')
    non = non[1].split('?itemId=')
    item1 = non[0]
    non = str(non[1]).split('&vendorItemId=')
    item2 = non[0]
    item3 = str(non[1]).split('&')
    item3 = item3[0]
    new_url = f'https://www.coupang.com/vp/products/{item1}/items/{item2}/vendoritems/{item3}'
#     print(new_url)
    data = requests.get(new_url, headers=headers).content
    bs = BeautifulSoup(data, "html.parser")
    #배송정보
    shipping = str(bs).split('"deliveryMethod":')
    shipping = shipping[1].split(',"deliveryCompany":')
    shipping = shipping[0]        
    
    #판매자 정보
    ceo = str(bs).split('"repPersonName":') #대표자
    ceo = ceo[1].split(',"repEmail"')
    ceo = ceo[0]

    email = str(bs).split('"repEmail":') #이메일
    email = email[1].split(',"repAddress2"')
    email = email[0]

    PhoneNum = str(bs).split('"repPhoneNum":') #연락처
    PhoneNum = PhoneNum[1].split(',"repPersonName"')
    PhoneNum = PhoneNum[0]
    
    address = str(bs).split('"repAddress":') #사업장 소재지
    address = address[1].split(',"ecommReportNum"')
    address = address[0]

    bizNum = str(bs).split('"bizNum":') #사업자번호
    bizNum = bizNum[1].split('}},')
    bizNum = bizNum[0]

    ecommReportNum = str(bs).split('"ecommReportNum":') #통신판매업 신고번호
    ecommReportNum = ecommReportNum[1].split(',"bizNum"')
    ecommReportNum = ecommReportNum[0]
    
    #상품 상세 - 설명 이미지 - ing
    image_column = ['','','','','']
    
    parsed3 = str(bs).split('"details":[')
    parsed3 = parsed3[1].split('],"forceHide3pWarningBanner"')
    parsed3 = parsed3[0]
    parsed3 = parsed3.split('},{')
    for (idx, image) in enumerate(parsed3):
        if idx > 4:
            break
        if idx != (len(parsed3)-1): 
            image = image +'}'
        if idx != 0 : 
            image = '{' + image
        try:
            json.loads(image)
            image = json.loads(image)
            image  = image['vendorItemContentDescriptions']
            image1 = str(image).split('[')
            image1 = str(image1[1]).split(']')
            image1 = str(image1[0])
            if "'detailType': 'IMAGE'" in image1:
                imaged = str(image1).split("'content': '")
                imaged = str(imaged[1]).split("'}")
                imaged = imaged[0]
                image_column[idx] = imaged
        except  :
            image = image.split(".jpg")
            for i in range(len(image)-1):
                if i > 4:
                    break
                imaged = image[i]
                imaged = imaged.split("src=")
                imaged = imaged[1]
                imaged = imaged[3:]+".jpg"
                image_column[i] = imaged
    
    
    ### 상품 문의
    inquiries_url = f'https://www.coupang.com/vp/products/{item1}/inquiries?pageNo=1&isPreview=false'
    qq = requests.get(inquiries_url, headers=headers).content
    ss = BeautifulSoup(qq, "html.parser") 
    lis = ss.findAll("div", {"class":"prod-inquiry-item"}) #각 질문  #질문 5개, 답 5개 
    qnas = ['','','','','','','','','','']
    num = 0
    for i in lis:
        if num > 9 : 
            break
        question = i.find("div", {"class":"prod-inquiry-item__content"}) #질문
        question = question.getText()
        try: #답변이 많은경우 가장 최근거 
            answer = i.findAll("div", {"class":"prod-inquiry-item__reply__content"}) #답
            answer = answer[(len(answer)-1)]
            answer = answer.getText()
        except : #답변 없으면 no answer
            answer = "답변 없음"
        qnas[num] = question
        qnas[num+1] = answer
        num += 2

    new_url_result = [shipping, ceo, email, PhoneNum, address, bizNum, ecommReportNum] + image_column + qnas
    
    return new_url_result
    ####
    
def getPageString(url):
    data = requests.get(url, headers = headers) 
    return data.content #바이너리 원문 
    
# main
if __name__ == '__main__':
# keyword = ['샤x'] #,'루이x통','루x비통','x이비통','구x','x찌','샤x','x넬']
# keyword = [' '.join(parse_arg(sys.argv[1:]).keyword.replace("'","").split('_'))]
    keyword = str(' '.join(parse_arg(sys.argv[1:]).keyword.replace("'","").split('_')))
    email = parse_arg(sys.argv[1:]).email


    #df 만들기 
    #url, name, image, data_image, price, (seller, detail image 8, 리뷰 10)#19개 
    df = pd.DataFrame({'url': pd.Series([], dtype='str'), 'name': pd.Series([], dtype='str'), 'image': pd.Series([], dtype='str'), 'data_image': pd.Series([], dtype='str'), 'price': pd.Series([], dtype='str'), 'seller': pd.Series([], dtype='str'),
                    'detailImage1': pd.Series([], dtype='str'), 
                    'detailImage2': pd.Series([], dtype='str'), 
                    'detailImage3': pd.Series([], dtype='str'), 
                    'detailImage4': pd.Series([], dtype='str'), 
                    'detailImage5': pd.Series([], dtype='str'), 
                    'detailImage6': pd.Series([], dtype='str'), 
                    'detailImage7': pd.Series([], dtype='str'), 
                    'detailImage8': pd.Series([], dtype='str'),
                    'comment1': pd.Series([], dtype='str'), 
                    'comment2': pd.Series([], dtype='str'), 
                    'comment3': pd.Series([], dtype='str'), 
                    'comment4': pd.Series([], dtype='str'), 
                    'comment5': pd.Series([], dtype='str'), 
                    'comment6': pd.Series([], dtype='str'), 
                    'comment7': pd.Series([], dtype='str'), 
                    'comment8': pd.Series([], dtype='str'),
                    'comment9': pd.Series([], dtype='str'), 
                    'comment10': pd.Series([], dtype='str')}) 
    
    #shipping, ceo, email, phone, address, bizNum, ecommReportNum + 설명이미지4개 + 상품문의 각 5개
    df2 = pd.DataFrame({ 'shipping_method' :  pd.Series([], dtype='str'),
                    'ceo': pd.Series([], dtype='str'), 'email': pd.Series([], dtype='str'), 'phone': pd.Series([], dtype='str'), 'address': pd.Series([], dtype='str'), 'business_number': pd.Series([], dtype='str'), 'ecommReportNum': pd.Series([], dtype='str'),
                    'PrudctdetailImage1': pd.Series([], dtype='str'), 
                    'PrudctdetailImage2': pd.Series([], dtype='str'), 
                    'PrudctdetailImage3': pd.Series([], dtype='str'), 
                    'PrudctdetailImage4': pd.Series([], dtype='str'),
                    'PrudctdetailImage5': pd.Series([], dtype='str'),
                    'question1': pd.Series([], dtype='str'), 
                    'answer1': pd.Series([], dtype='str'), 
                    'question2': pd.Series([], dtype='str'), 
                    'answer2': pd.Series([], dtype='str'), 
                    'question3': pd.Series([], dtype='str'), 
                    'answer3': pd.Series([], dtype='str'), 
                    'question4': pd.Series([], dtype='str'), 
                    'answer4': pd.Series([], dtype='str'),
                    'question5': pd.Series([], dtype='str'), 
                    'answer5': pd.Series([], dtype='str')  
                    } ) #df 만들기 
    
    
    for i in range(1, 4):  #1-3페이지 크롤링
        print("trying %d" % i) #페이지 프린트 
        time.sleep(3) 
        url = f'https://www.coupang.com/np/search?component=&q={keyword}&channel=user&page=%d' % i  #url 만들기. 하지만 string일 뿐 
        data = getPageString(url) #url 불러오기
        bsObj = BeautifulSoup(data, "html.parser") #HTML 해석기
        ul = bsObj.find("ul", {"id":"productList"})  #아이템 리스트부분 추출
        if ul is None:
            break
            
        parsed_list,pruduct_urls = getProducts(ul,keyword)
        
        if parsed_list is not None:
            df = df.append(pd.DataFrame(parsed_list, columns=df.columns), ignore_index=True)
            df2 = df2.append(pd.DataFrame(pruduct_urls, columns=df2.columns), ignore_index=True)
            
            df_result = pd.concat([df, df2], axis=1)
            
    # if df.empty is False:
    #     df_result.to_csv(f'{j}.csv')
    df_result.to_csv('.\\coupang_%s_%s.csv' % (keyword, email))
