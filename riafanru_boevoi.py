#https://riafan.ru/news
import ibm_db_dbi as db
import requests
import re
from bs4 import BeautifulSoup
import psycopg2
from datetime import date
import datetime

def telegram_bot_sendtext(bot_message):
    bot_token = '1700296384:AAGoaq3o2WD7BbUthmU9dEYQD5IMEKBIgxU'
    bot_chatID = '771779345'
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
    response = requests.get(send_text)
    return response.json()

def converter(url):
    url = re.sub(r'[\W+\_]','',url)
    object_id = ''
    for u in url:
        object_id += str(ord(u) - 96)
    object_id = object_id.replace('-','')[:250]
    return object_id

telegram_bot_sendtext('starts riafanru')

try:
    url1 = 'https://riafan.ru/news'
    page = requests.get(url1)
    page.status_code
    soup = BeautifulSoup(page.text, 'html.parser')
    url_statyi = soup.find_all(class_ = 'cat-news-item')
    urls = []
    vi = []
    
    for i in range(len(url_statyi)):
        url2 = soup.find_all(class_ = 'cat-news-item')[i]
        url1 = url2.findAll('a')[0]["href"]
        
        v = url2.find(class_ = 'cat-item__views tile-list-news__views')
        view = v.get_text()
        vi.append(view)
        
        urls.append(url1)
        q = 0
        
    for i in range(len(urls)):
        URL = urls[i]
        url = urls[i][0:]
        object_id = converter(url)
        
        views = vi[i]
        
        page = requests.get(URL)
        page.status_code
        soup =  BeautifulSoup(page.text, 'html.parser')
        
        text1 = soup.find(class_ = 'content-wrap')
        text = text1.get_text()
        
        date = soup.find(class_ = 'post-published').get('datetime')
        d = re.findall('\d+', date)
        date_time = d[0] + '-' + d[1] + '-' + d[2] + ' ' + d[3] + ':' + d[4] + ':' + '00.0'
        
        time1 = d[3] + ':' + d[4] + ':' + '00'
        tlist = [time1, '3:00:00']
        mysum = datetime.timedelta()

        for i in tlist:
            (h, m, s) = i.split(':')
            dt = datetime.timedelta(hours = int(h), minutes = int(m), seconds = int(s))
            mysum += dt
            date = d[0] + '-' + d[1] + '-' + d[2] + ' ' + str(mysum) + '.0'
            
        try:
            img = soup.find('div', {'class': 'main-image-container'})
            url_attachment = img.find('img').get('data-src')
        except:
            url_attachment = None
        
        connection_text = """DATABASE=PRODDB;HOSTNAME=192.168.252.11;PORT=50000;
        PROTOCOL=TCPIP;UID=db2inst1;PWD=Qjuehnghj1;"""
        sql_1_test = "SELECT url_channel FROM TL_MEDIA_DATA_NEWS_TEST"
        con = db.connect(connection_text, "", "")
        cursor = con.cursor()
        cursor.execute(sql_1_test)
        t = cursor.fetchall()
        con.commit()
        cursor.close()
        con.close()
        
        t0 = []
        for y in range(len(t)):
            t0.append(t[y][0])
            
        if not URL in t0:
            connection_text = """DATABASE=PRODDB;HOSTNAME=192.168.252.11;
            PORT=50000;PROTOCOL=TCPIP;UID=db2inst1;PWD=Qjuehnghj1;"""
            con = db.connect(connection_text, "", "")
            cursor = con.cursor()
            insert_query = """insert into TL_MEDIA_DATA_NEWS_TEST (object_id, published_date, channel_id, 
            likes, comments, views, reposts, caption, text, url_attachment, url_channel, source_id) 
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
            cursor.execute(insert_query, (object_id, date, None, None, None, views, None, None, text, url_attachment, URL, 700))
            con.commit()
            cursor.close()
            con.close()
            q = q + 1
    #"Парсинг riafan.ru прошел успешно.(time.kz)" 
    send_text = "Парсинг сайта riafan.ru прошел успешно, добавлено " + str(q) + " публикации. Благодарю."
    telegram_bot_sendtext(send_text)   #Сообщение отправлено в телеграмм бот
    #print(send_text)
except (Exception, psycopg2.Error) as error:
    send_text = "Ошибка при парсинге сайта riafan.ru " + "\n" + str(error)
    telegram_bot_sendtext(send_text)   #Сообщение отправлено в телеграмм бот
    #print(send_text)
