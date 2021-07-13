import urllib.request
from bs4 import BeautifulSoup
import requests
import os
def main():
    page = urllib.request.urlopen("https://www.cbr.ru/")
    soup = BeautifulSoup(page, features="lxml")
    h = soup.find('div', {'class': 'col-md-2 col-xs-9 _right mono-num'}).text
    return send_message(h)
def send_message(message):
    title = 'Dollar: '
    os.system('notify-send "{}" "{}"'.format(title, message))
main()