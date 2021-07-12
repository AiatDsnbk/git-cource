import ibm_db_dbi as db
import requests
import re
from bs4 import BeautifulSoup
import requests
import urllib

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

try:
    url1 = 'https://riafan.ru/news'
    page = requests.get(url1)
    page.status_code
    soup = BeautifulSoup(page.text, 'html.parser')
    url_statyi = soup.find_all(class_ = 'cat-news-item')
    url_public = soup.find_all(class_ = 'cat-item__title ')
    urls = []
    for i in range(len(url_statyi)):
        url1 = ""
        url1 = soup.find_all(class_='cat-item__title ')[i].findAll('a')[0]["href"]
        urls.append(url1)
    q = 0
    for i in range(len(urls)):
        URL = "https://riafan.ru" + urls[i]
        url = urls[i][1:]
        object_id = converter(url)
        page = requests.get(URL)
        page.status_code
        soup =  BeautifulSoup(page.text, 'html.parser')
        text = soup.find(class_ = 'col-md-12 col-lg-8 post__text user-content')
        text1 = text.get_text()[:-46]
        dat = soup.find(class_ = 'article__date')
        vi = soup.find(class_ = 'article__views')
        views = vi.get_text()
        da = dat.get_text()
        daa = da.replace(" ","")
        dat = ""
        for t in range(len(daa)):
            if daa[t] != "\n" :
                dat = dat + daa[t]
        clock = dat[-5:]
        day = dat[0:2]
        for d in range(len(dat)):
            if dat[d] ==",":
                m = d
                break

        data = ""
        if  dat[2:m] == "мая":
            mouth = "05"

        if  dat[2:m] == "июня":
            mouth = "06"

        if  dat[2:m] == "июля":
            mouth = "07"

        if  dat[2:m] == "августа":
            mouth = "08"

        if  dat[2:m] == "сентября":
            mouth = "09"

        if  dat[2:m] == "октября":
            mouth = "10"

        if  dat[2:m] == "ноября":
            mouth = "11"

        if  dat[2:m] == "декабря":
            mouth = "12"

        if  dat[2:m] == "января":
            mouth = "01"

        if  dat[2:m] == "февраля":
            mouth = "02"

        if  dat[2:m] == "марта":
            mouth = "03"

        if  dat[2:m] == "апреля":
            mouth = "04"
        data = "2019-" + mouth + "-" + day + " " + clock + ":00"

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
            sql_1_test = """insert into TL_MEDIA_DATA_NEWS_TEST (object_id, published_date, channel_id, likes, 
            comments, views, reposts, 
            caption, text, url_attachment, url_channel, source_id) 
            values (?,?,?,?,?,?,?,?,?,?,?,?)"""
            cursor.execute(sql_1_test,  (object_id, data, 1, None, None, views, None, None, text1, None, URL, 922))
            con.commit()
            cursor.close()
            con.close()
            q = q + 1
            
    # #Select data from table here
    # connection_text = """DATABASE=PRODDB;HOSTNAME=192.168.252.11;PORT=50000;
    #     PROTOCOL=TCPIP;UID=db2inst1;PWD=Qjuehnghj1;"""
    # con = db.connect(connection_text, "", "")
    # cursor = con.cursor()
    # cursor.execute("""
    # SELECT url_channel
    # FROM TL_MEDIA_DATA_NEWS_TEST
    # ORDER BY published_date""")
    # result = cursor.fetchall()
    # con.commit()
    # cursor.close()
    # con.close()
    # for x in result:
    #     print(x)
        
    send_text = "Парсинг сайта riafan.ru  успешно прошло, добавлено " + str(q) + " публикации. Благодарю."
    telegram_bot_sendtext(send_text)
    print(send_text)
except :
    send_text = "Ошибка при парсинге(riafan.ru)"
    telegram_bot_sendtext(send_text)
    print(send_text, error)