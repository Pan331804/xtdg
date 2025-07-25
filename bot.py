import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import os
import sys

TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

if not TOKEN or not CHAT_ID:
    print("❌ Brak TOKEN lub CHAT_ID w zmiennych środowiskowych!")
    sys.exit(1)

POLAND_TZ = ZoneInfo("Europe/Warsaw")
# Usuwamy plik do zapisywania wysłanych ogłoszeń (bo nie działał)

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {
        "chat_id": CHAT_ID,
        "text": message
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"❌ Błąd wysyłania wiadomości: {response.status_code} - {response.text}")
    else:
        print("✅ Wiadomość wysłana poprawnie.")

def check_announcements():
    url = 'https://www.tarnowiak.pl/szukaj/?ctg=31&p=1&q=&pf=&pt='
    headers = {"User-Agent": "Mozilla/5.0 (compatible; Bot/1.0)"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    raw_ogloszenia = soup.find_all('div', class_='box_content_plain') + soup.find_all('div', class_='box_content_featured')

    teraz = datetime.now(POLAND_TZ)
    print(f"🔄 Teraz: {teraz} (typ: {type(teraz)})")

    limit = timedelta(minutes=30)
    ogloszenia = []

    for ogloszenie in raw_ogloszenia:
        data_div = ogloszenie.find('div', class_='box_content_date')
        if data_div and 'dzisiaj' in data_div.text.lower():
            parts = data_div.text.lower().split(",")
            if len(parts) > 1:
                godzina_str = parts[1].strip()
                try:
                    godzina_obj = datetime.strptime(godzina_str, "%