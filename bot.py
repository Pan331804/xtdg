import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo  # wymaga Python 3.9+
import os

# Pobierz token i chat_id z zmiennych środowiskowych
TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# Ustawiamy strefę czasową Polski
POLAND_TZ = ZoneInfo("Europe/Warsaw")

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

    teraz = datetime.now(POLAND_TZ)  # teraz w polskiej strefie

    for ogloszenie in ogloszenia:
        data_div = ogloszenie.find('div', class_='box_content_date')
        if data_div and 'dzisiaj' in data_div.text.lower():
            try:
                godzina_str = data_div.text.split(",")[1].strip()
                godzina_obj = datetime.strptime(godzina_str, "%H:%M")

                # tworzymy datetime ogłoszenia z polską strefą
                ogloszenie_datetime = teraz.replace(
                    hour=godzina_obj.hour,
                    minute=godzina_obj.minute,
                    second=0,
                    microsecond=0
                )

                roznica = teraz - ogloszenie_datetime

                if timedelta(minutes=0) <= roznica <= timedelta(minutes=35):
                    message = f"🆕 Nowe ogłoszenie z {godzina_str}:\nhttps://www.tarnowiak.pl/szukaj/?ctg=31"
                    send_telegram_message(message)

            except Exception as e:
                print("⚠️ Błąd przy przetwarzaniu ogłoszenia:", e)

def main():
    teraz = datetime.now(POLAND_TZ)
    print(f"🔄 Sprawdzanie ogłoszeń: {teraz.strftime('%Y-%m-%d %H:%M:%S')}")
    try:
        check_announcements()
    except Exception as e:
        print("❌ Błąd w głównej funkcji:", e)

if __name__ == "__main__":
    main()