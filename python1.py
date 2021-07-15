import urllib.request
from bs4 import BeautifulSoup
import os

def main():
    page = urllib.request.urlopen("https://web.whatsapp.com/")
    soup = BeautifulSoup(page, features="lxml")

    h = soup.find('span', {'class': '_ccCW FqYAR i0jNr'}).get('title')
    
    return send_message(h)

def send_message(message):
    title = 'Aian: '
    os.system('notify-send "{}" "{}"'.format(title, message))

main()