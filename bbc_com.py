#https://www.bbc.com/russian
import ibm_db_dbi as db
import requests
import re
from bs4 import BeautifulSoup
import datetime
from datetime import date, timedelta, datetime

date_while = date.today()
xx = date_while.strftime('%Y-%m-%d')
current_time = datetime.now()

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

telegram_bot_sendtext('starts bbc')

try:
    url1 = 'https://www.bbc.com/russian'
    page = requests.get(url1)
    page.status_code
    soup = BeautifulSoup(page.text, 'html.parser')
    url_statyi = soup.find_all(class_ = 'bbc-1fxtbkn evnt13t0')
    urls = []
    for i in range(len(url_statyi)):
        url1 = 'https://www.bbc.com' + url_statyi[i].get('href')
        if not re.search('mhttp', url1):
            urls.append(url1)
        q = 0
        
    for i in range(len(urls)):
        URL = urls[i]
        url = urls[i][0:]
        object_id = converter(url)
        page = requests.get(URL)
        page.status_code
        soup =  BeautifulSoup(page.text, 'html.parser')
        
        date = soup.find('time', {'': ''}).get('datetime')
        if date is not None and re.search(xx, date):
            
            try:
                img = soup.find('img', {'class': 'bbc-fat2bc e1enwo3v0'}).get('src')
            except:
                img = None
                
            time = soup.find('time', {'': ''}).get_text()
            if re.search('час назад', time):
                hour = 1
                past_time = current_time - timedelta(hours=hour)
                past_time_str = past_time.strftime('%H:%M:%S') + '.0'
                
            elif re.search('минут', time):
                ho = re.findall('\d+', time)
                minut = int(ho[0])
                past_time = current_time - timedelta(minutes=minut)
                past_time_str = past_time.strftime('%H:%M:%S') + '.0'
                
            else:
                ho = re.findall('\d+', time)
                hour = int(ho[0])
                past_time = current_time - timedelta(hours=hour)
                past_time_str = past_time.strftime('%H:%M:%S') + '.0'
            datetime = date + ' '+ past_time_str
            
            try:
                t = soup.find('main', {'role': 'main'})
                text = soup.find('h1', {'class': 'bbc-7ota8y e1yj3cbb0'}).text + "\n"
                t1 = t.find_all('p', {'class': 'bbc-bm53ic e1cc2ql70'})
                for t2 in t1:
                    text = text + t2.text

            except:
                t = soup.find('main', {'role': 'main'})
                text = soup.find('strong', {'class': 'e8stly50 bbc-1luz917 e14hemmw1'}).text + "\n"
                t1 = t.find_all('p', {'class': 'bbc-bm53ic e1cc2ql70'})
                for t2 in t1:
                    text = text + t2.text
                    
            connection_text = """DATABASE=PRODDB;HOSTNAME=192.168.252.11;
            PORT=50000;PROTOCOL=TCPIP;UID=db2inst1;PWD=Qjuehnghj1;"""
            select_query = """SELECT url_channel FROM TL_MEDIA_DATA_NEWS WHERE source_id = '9371'"""
            con = db.connect(connection_text, "", "")
            cursor = con.cursor()
            cursor.execute(select_query)
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
                insert_query = """insert into TL_MEDIA_DATA_NEWS (object_id, published_date, channel_id, 
                likes, comments, views, reposts, caption, text, url_attachment, url_channel, source_id) 
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
                cursor.execute(insert_query, (object_id, datetime, None, None, None, None, None, None, text, img, URL, 9371))
                con.commit()
                cursor.close()
                con.close()
                q = q + 1
        #"Парсинг riafan.ru прошел успешно.(time.kz)" 
    send_text = "Парсинг сайта bbc.com успешно прошло, добавлено " + str(q) + " публикации. Благодарю."
    telegram_bot_sendtext(send_text)   #Сообщение отправлено в телеграмм бот
    
except Exception as error:
    send_text = "Ошибка при парсинге bbc.com " + "\n" + str(error)
    telegram_bot_sendtext(send_text)   #Сообщение отправлено в телеграмм бот