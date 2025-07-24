import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os

# Pobierz token i chat_id z zmiennych środowiskowych
TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {
        "chat_id": CHAT_ID,
        "text": message
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print("❌ Błąd wysyłania wiadomości:", response.text)

def check_announcements():
    url = 'https://www.tarnowiak.pl/szukaj/?ctg=31&p=1&q=&pf=&pt='
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    ogloszenia = soup.find_all('div', class_='box_content_plain') + soup.find_all('div', class_='box_content_featured')

    teraz = datetime.now()

    for ogloszenie in ogloszenia: