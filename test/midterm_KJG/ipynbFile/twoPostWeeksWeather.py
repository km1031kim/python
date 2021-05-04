#!/usr/bin/env python
# coding: utf-8

# In[4]:


################ 서울의 현재 날짜로부터 2주동안의 날씨 정보를 크롤링 해보자 ################ 

##### 1.셀레니움 활용 웹브라우져 자동화

### 1-1. 라이브러리 선언
from selenium import webdriver
import pandas as pd
from selenium.webdriver.common.by import By ## 커서 이동을 위해 라이브러리 추가.

### 1-2. 웹브라우저 설정
options = webdriver.ChromeOptions() ## 버전 맞춰서 다운로드.
options.add_argument("start-maximized") # 창이 작았을 경우 오류를 대비해 창 최대로 띄우기.
#options.add_argument("--headless") ## headless로 실행.
driverLoc = "../addon/chromedriver/chromedriver.exe" # 상대경로 지정.
driver = webdriver.Chrome(executable_path=driverLoc, options=options) 
driver.implicitly_wait(3) ### 웹페이지 파싱 될때까지 최대 3초 기다림

### 1-3. 브라우저 열기
targetUrl = "https://www.timeanddate.com/"

## get 함수를 사용 url정보를 던져줘서 이동시키기.
driver.get(targetUrl)

## 마우스 커서를 가져다 대야 원하는 창 선택이 가능하다. 해당 메뉴로 커서를 이동시키자.
weatherMenu = driver.find_element(By.XPATH, '//*[@id="site-nav"]/li[5]/a')
webdriver.ActionChains(driver).move_to_element(weatherMenu).perform()

## 여기서 다시 2-Week Forecast 클릭 실행
twoWeekForecastXpath = '//*[@id="site-nav"]/li[5]/ul/li[4]/a'
twoWeekForecastXpathBtn = driver.find_element_by_xpath(twoWeekForecastXpath)
twoWeekForecastXpathBtn.click() ## 클릭으로 창 이동.

## 현재 창에서 크롤링 진행, 셀레니움의 역활은 여기까지
targetUrl = driver.current_url

##### 2. 크롤링하기. 오늘부터 2주동안의 서울 날씨를 크롤링해보자.

### 2-1 라이브러리 선언
from bs4 import BeautifulSoup # 태그 이쁘게 뜨기
import requests # 웹페이지 접속 요청
resp = requests.get(url=targetUrl) ## response 200 = 정상, 확인완료
resp.encoding = "utf-8" ## 인코딩
html = resp.text
htmlObj = BeautifulSoup(html, "html.parser") ## beautifulSoup 사용

## 목표 테이블 추출.
Allinfomation = htmlObj.find(name="tbody") 

## 목표 테이블의 tr 추출.
Alltrs = Allinfomation.findAll("tr")



## 최종 데이터를 넣을 rowList. 각각의 데이터를 일시적으로 담을 columnList.
rowList = []
columnList = []

## 데이터 추출.
for j in range(0,len(Alltrs)):
    
    eachTr = Alltrs[j]

    ## tr에서 요일/월일 추출
    date = eachTr.find("th").text
    eachDate = date.replace("요일","요일 ")

    ## 요일, 월, 일 추출 완료
    columnList.append(eachDate)

    ## td에서 추출 세부 데이터 추출
    Alltd = eachTr.findAll(name="td")

    ##  0번째 td는 필요 없는 데이터이기에 제거하고 새로운 리스트에 필요한 데이터만 넣어보자
    ## 필요한 데이터만 넣을 reinedAlltds 생성
    refinedAlltds = []
    
    ## 데이터 정제.
    for i in range(1, len(Alltd)): ## 1부터 시작, 0번째 제외시키기.
        refinedAlltds.append(Alltd[i])

    ## 데이터 추출.
    for i in range(0, len(refinedAlltds)):

        tds = refinedAlltds[i]
        eachTd = tds.text
        ## 불필요한 문자 replace를 위한 변수 refinedTd
        refineTd = eachTd.endswith("°C")
        ## 불필요한 문자가 있을 시 제거 후 text 추출 후 append.
        if refineTd == True:

            eachTd = eachTd.replace("\xa0","")
        ## 그렇지 않은 경우는 text추출 후 append.
        else: 
            eachTd = tds.text

        columnList.append(eachTd)

    rowList.append(columnList)
    columnList = []


df1 = pd.DataFrame(rowList)
columnNameList = ["월/일","최고/최저기온", "날씨", "체감온도", "풍속", "풍향", "습도", "강우확률", "강수량", "자외선량", "일출시간", "일출시간"]    

df1.columns = columnNameList

twoPostWeeksWeather = df1

## 현재 위치에 csv 파일 생성
twoPostWeeksWeather.to_csv("./twoPostWeeksWeather.csv", index=False, encoding="ms949")

##### 3.메일전송 자동화

## 라이브러리 선언
#import getpass ##비밀번호 에코 방지를 위한 라이브러리 getpass.
#import getpass ## 앱 비밀번호 암호화 
userpw = "eswblpxekeqqtxqe" ## 구글 앱 비밀번호.
#userpw = getpass.getpass()  # 암호화 

#라이브러리 선언
import pickle ## 비밀번호 암호화

with open('pw.pickle', 'wb') as handle:
    pickle.dump(userpw, handle, pickle.HIGHEST_PROTOCOL)

with open('pw.pickle', 'rb') as handle:
    pwpickle = pickle.load(handle)

## 라이브러리 선언
import smtplib ##메일 보내기
from email.message import EmailMessage

smtp_gmail = smtplib.SMTP('smtp.gmail.com', 587)
smtp_gmail.ehlo()
smtp_gmail.starttls()

userid = "km1031kim@gmail.com"
smtp_gmail.login(userid,pwpickle) ## 암호화 된 비밀번호



## 이메일 리스트 불러와서 데이터프레임화.
emailData = pd.read_csv("../emailList/emailList.csv")

to = emailData["이메일"].tolist() ## 저장된 csv피일로 보낼 대상 입력.

## 제목 및 메일내용 작성
msg=EmailMessage()
msg['Subject']="2주치 날씨정보"
msg.set_content("2주간의 날씨정보입니다.")
msg['From']='km1031kim@gmail.com'
msg['To'] = to

## sv 파일첨부
file='twoPostWeeksWeather.csv' # 현재 위치에 있는 twoPostWeeksWeather.csv 파일을
fp = open(file,'rb')  # 오픈해서 fp에 집어넣고
file_data=fp.read() 
msg.add_attachment(file_data, ## msg에 첨부파일 추가, 밑엔 메타정보 속성들
                  maintype='text',
                  subtype='plain',
                  filename=file) ## 이름과 같이

## mail 발송
smtp_gmail.send_message(msg)
smtp_gmail.close()


# In[ ]:




