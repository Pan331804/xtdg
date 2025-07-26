import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz  # dodaj to

TELEGRAM_TOKEN = os.environ['TOKEN']
CHAT_ID = os.environ['CHAT_ID']

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    response = requests.post(url, data=payload)
    if response.status_code != 200:
        print("Błąd wysyłania wiadomości:", response.text)

strona = requests.get('https://www.tarnowiak.pl/szukaj/?ctg=31&p=1&q=&pf=&pt=')
strona.raise_for_status()

soup = BeautifulSoup(strona.text, 'html.parser')
ogloszenia_div = soup.find_all('div', class_='box_content_plain')
ogloszenia_div_premium = soup.find_all('div', class_='box_content_featured')
wszystkie_ogloszenia = ogloszenia_div_premium + ogloszenia_div

# 🕒 Dodajemy strefę czasową Europe/Warsaw
warsaw = pytz.timezone("Europe/Warsaw")
teraz = datetime.now(warsaw)

for ogloszenie in wszystkie_ogloszenia:
    data_div = ogloszenie.find('div', class_='box_content_date')
    if data_div:
        text = data_div.text.lower()
        if "dzisiaj" in text:
            try:
                godzina_str = text.split(",")[1].strip()
                godzina_obj = datetime.strptime(godzina_str, "%H:%M")
                godzina_obj = warsaw.localize(godzina_obj.replace(year=teraz.year, month=teraz.month, day=teraz.day))

                roznica = teraz - godzina_obj
                roznica_minut = roznica.total_seconds() / 50

                if 0 <= roznica_minut <= 60:
                    msg = f"Nowe ogłoszenie z dzisiaj o {godzina_str} — jest maksymalnie 60 minut starsze."
                    print(msg)
                    send_telegram_message(msg)
                else:
                    print(f"Ogłoszenie z {godzina_str} jest starsze niż 60 minut lub z przyszłości.")

            except (IndexError, ValueError):
                print("Błąd parsowania godziny w tekście:", text)