#https://riafan.ru/
import urllib.request
from bs4 import BeautifulSoup
import re
import requests
from datetime import date, timedelta

date_while = date.today()
xx = date_while.strftime('%d.%m.%Y')

page = urllib.request.urlopen("https://riafan.ru/")
soup = BeautifulSoup(page, 'lxml')

h = soup.find_all('span', {'class': 'i0jNr selectable-text copyable-text'})
for h1 in h:
    mess = h1.find('span').text()
    print(mess)
#     date = h1.find('div', {'class': 'cat-item__date tile-list-news__date'}).text
#     d = re.findall('\d+', date)
#     date_time = d[0]+'.'+d[1]+' '+d[2]+':'+d[3]
# # #     if re.search(xx, date):
#     href = h1.get('href')
#     post = "https://riafan.ru" + href
#     page = urllib.request.urlopen(post)
#     soup = BeautifulSoup(page)

#     t = soup.find('div', {'class': 'content-wrap'})
#     text = soup.find('h1', {'class': 'post-main-title'}).text + "\n"
#     t1 = t.find_all('p', {'class': ''})
#     for t2 in t1:
#         text = text + t2.text
#     print(date_time + "\n" + text + "\n")