import urllib.request
from bs4 import BeautifulSoup
import re
from datetime import date

date_while = date.today()
xx = date_while.strftime('%d.%m.%Y')

page = urllib.request.urlopen("https://lenta.inform.kz/ru")
soup = BeautifulSoup(page, features="lxml")

h = soup.find_all('div', {'class': 'lenta_news_block'})
for h1 in h:
    href = h1.find('a', {'class': 'lenta_news_title'}).get('href')
    post = "https://lenta.inform.kz" + href
    page = urllib.request.urlopen(post)
    soup = BeautifulSoup(page, features="lxml")
    
    date = soup.find('div', {'class': 'date_article'}).text
    d = re.findall('\d+', date)
    date_time = d[0] + '.' + d[1] + ' ' + d[2] + ':' + d[3]
#     if 
    dater = date.replace("\n", "").replace("                            ", "")
    
#     t = soup.find('div', {'class': 'article_news_body'})
#     text = soup.find('div', {'class': 'article_title'}).text + "\n"
#     t1 = t.find_all('p', {'class': ''})
#     for t2 in t1:
#         text = text + t2.text
    print(date_time, dater)