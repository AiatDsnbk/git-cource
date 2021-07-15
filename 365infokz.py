#this script adds new news into the table in DB
#the initial condition for FIRST run of this script is to run firsrt corresponding initializer, 
#if the initializer was not run, this script will raise exception and send correspomding massage on telegram
#if the script break, it also will send the massage on telegram

#скрипт можно запускать каждые 2 часа, в основном используется selenium

#________________libraries____________________
from bs4 import BeautifulSoup 
import urllib.request
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import ibm_db_dbi
import requests
import datetime
import os

#________________functions____________________
#get url and return corresponding driver
def Webdriver ():
    options = Options()
    options.headless = True
    path = os.getcwd()
    driver = webdriver.Firefox(options = options, executable_path=path + '/geckodriver')
    return driver

#take url and make it of type soup
def beautifier(url):
    req = urllib.request.Request(url)
    resp = urllib.request.urlopen(req)
    respData = resp.read()
    soup = BeautifulSoup(respData, 'html.parser')
    return soup

#gather data and push it as one list into the stack
def grabInfo(driver, url_channel, last_ID, dataStack, AllObject_ids):
    source_id = 945  #id of 365info.kz

#get the id of the current news, if the id is equal to the id of latest added one return False     
    object_ID = driver.find_element_by_name('post_id')
    object_ID = object_ID.get_attribute('content')
    if object_ID == last_ID:
        print('latest article')
        return False
        
    if object_ID in AllObject_ids:
        print('old article')
        return True
    AllObject_ids.append(object_ID) 

    date = driver.find_element_by_class_name('updated')
    day = date.get_attribute('datetime')
    day = day[:10]
    time = date.text
    start = len(time) - 6
    if time[start] == ',':
        time = time.replace(', ', ' 0')
    time = time[start:]
    date = day + time + ':00'
    
    title = driver.find_element_by_class_name('row.single__title')
    title = title.text   
    text = driver.find_element_by_class_name('row.single__content.js-mediator-article')   
    paragraph_list = text.find_elements_by_tag_name('p')
    paragraphs_list = []
    for paragraph in paragraph_list:
        paragraphs_list.append(paragraph.text)
    paragraphs = ' '.join(paragraphs_list)
    paragraphs = title + ' ' + paragraphs
    
    image_list = text.find_elements_by_tag_name('img')
    if image_list == []:
        image = ''
    else:
        images_list = []
        for image in image_list:
            images_list.append(image.get_attribute('src'))
        image = ', '.join(images_list)
   
    video_list = text.find_elements_by_tag_name('iframe')
    if video_list == []:
        url_attachment = image
    else:
        videos_list = []
        for video in video_list:
            videos_list.append(video.get_attribute('src'))
        video = ', '.join(videos_list)
        url_attachment = image + ', ' + video
        
        
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    views = soup.find(class_='meta__details')
    if views == None:
        views = None
    else:
        views = " ".join(views.get_text().split())
        views = int(views)
    
    print('new article')
    datalist = [object_ID, date, views, paragraphs, url_attachment, url_channel, source_id]
    dataStack.append(datalist)
    return True

#returns the lattest added article
def getLatestArticle(cursor):
    cursor.execute("select * from tl_media_data_news_test WHERE source_id = 945")
    table = cursor.fetchall()
    if table == []:
        raise Exception('Not Initialized::No article in the table from 365info.kz')
    latest_article = table[-1][1]
    return latest_article

 #return the list of all object_ids of website
def getAllObject_ids(cursor):
    select_Query = "SELECT object_id FROM tl_media_data_news_test WHERE source_id = 945"
    cursor.execute(select_Query)
    rows = cursor.fetchall()
    all_object_id = []
    for row in rows:
        all_object_id.append(row[0])
    return all_object_id
    
#pop all elements of the stack and write the data to the dataBase in reverse order, 
#so that the latest news is on the last row of the table in DB
def Write_To_DB (cursor, dataStack):
    while (dataStack != []):
        cursor.execute("""insert into tl_media_data_news_test
        (object_id, published_date, views, text, url_attachment, url_channel, source_id) 
        values(?,?,?,?,?,?,?)""", dataStack.pop())

#_____updateOlds doesn not work____
#def updateOlds (cursor):
#    cursor.execute("select * from tl_media_data_news")
#    table = cursor.fetchall()
#    i = len(table)
#    while i != 0:
#        i -= 1
#        if table[i][12] == 945:
#            object_ID = table[i][1]
#            soup = beautifier(table[i][11])
#            views = soup.find(class_='meta__details')
#            if views == None:
#                views = 0
#            else:
#                views = " ".join(views.get_text().split())
#                views = int(views)
#            cursor.execute("update tl_media_data_news set views = ? where object_id = ? and sourse_id = 945",(views, object_ID))
            
def telegram_bot_sendtext(bot_message):
    bot_token = '1700296384:AAGoaq3o2WD7BbUthmU9dEYQD5IMEKBIgxU'
    bot_chatID = '771779345'
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
    response = requests.get(send_text) 
    return response.json()

try:
    telegram_bot_sendtext(str(datetime.datetime.now())[:19] + '\n' + 'COMBAT 365infokz STARTED!' + '\n' + '\U0001F642')
    
    #connect to dataBase
    connection_text = """DATABASE=PRODDB;HOSTNAME=192.168.252.11;
    PORT=50000;PROTOCOL=TCPIP;UID=db2inst1;PWD=Qjuehnghj1;"""
    conn = ibm_db_dbi.connect(connection_text, "", "")
    cursor = conn.cursor()
    
    #add new news to DB
    #Variables
    maxpage = 3            #here the maxpage page is overbig in order to increase the range of news and break when the lattest added news is found
    url = 'https://365info.kz/category/poslednie-novosti'
    dataStack = []              #stack which store all the media data
    last_first_article = ''     #the latest added news's object_id
    AllObject_ids = []
    WArticle = True             #WArticle is false when riches the lattest added news
    
    last_first_article = getLatestArticle(cursor)
    AllObject_ids = getAllObject_ids(cursor)
    driver = Webdriver()
    
    soup = beautifier(url)
    news_pages_row_list = soup.find_all(class_= 'items')
    
    #1st page of news
    for news_page in news_pages_row_list:
        if WArticle == False:
            break
        news_page_list = news_page.find_all(class_='item')
        for news_page_url in news_page_list:
            news_page_url = news_page_url.find('a')
            link = news_page_url.get('href')
            print(link)
            driver.get(link)
            WArticle = grabInfo(driver, link, last_first_article, dataStack, AllObject_ids)
            if WArticle == False:
                 break         
            
    #2nd and more pages 
    for i in range(2, maxpage):
        if i == 1000:
            raise Exception('Too many:: Something wrong! Check website') 
        if WArticle == False:
            break
        url = 'https://365info.kz/category/poslednie-novosti/page/' + str(i)
        soup = beautifier(url)
        news_pages_row_list = soup.find_all(class_= 'items')
        for news_page in news_pages_row_list:
            if WArticle == False:
                break
            news_page_list = news_page.find_all(class_='item')
            for news_page_url in news_page_list:
                news_page_url = news_page_url.find('a')
                link = news_page_url.get('href')
                print(link)
                driver.get(link)
                WArticle = grabInfo(driver, link, last_first_article, dataStack, AllObject_ids)
                if WArticle == False:
                    break
                
    Write_To_DB(cursor, dataStack)
    print('finish')
    driver.quit()         
    conn.commit()
    telegram_bot_sendtext(str(datetime.datetime.now())[:19] + '\n' + 'COMBAT 365infokz RUN SUCCESSFULLY!' + '\n' + '\U0001F604')
#    cursor.execute("SELECT * FROM tl_media_data_news")
#    data = cursor.fetchall()
#    print(data)

except Exception as e:
    # Запись в лог
    text = '\U0001F914' + '\n' + 'Error occured in COMBAT 365Info.kz' +  '\n' +  str(e)+ '\n'
    # Отправить сообщение в телеграмм
    telegram_bot_sendtext(text)    
 
    

             