import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import time

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
        data_div = ogloszenie.find('div', class_='box_content_date')
        if data_div and 'dzisiaj' in data_div.text.lower():
            try:
                godzina_str = data_div.text.split(",")[1].strip()
                godzina_obj = datetime.strptime(godzina_str, "%H:%M")

                ogloszenie_datetime = teraz.replace(
                    hour=godzina_obj.hour,
                    minute=godzina_obj.minute,
                    second=0,
                    microsecond=0
                )

                roznica = teraz - ogloszenie_datetime

                # Sprawdź, czy ogłoszenie jest nie starsze niż 35 minut
                if timedelta(minutes=0) <= roznica <= timedelta(minutes=35):
                    message = f"🆕 Nowe ogłoszenie z {godzina_str}:\nhttps://www.tarnowiak.pl/szukaj/?ctg=31"
                    send_telegram_message(message)

            except Exception as e:
                print("⚠️ Błąd przy przetwarzaniu ogłoszenia:", e)

def main():
    while True:
        print(f"🔄 Sprawdzanie ogłoszeń: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        try:
            check_announcements()
        except Exception as e:
            print("❌ Błąd w głównej pętli:", e)

        # Odczekaj 30 minut (1800 sekund)
        time.sleep(1800)

if __name__ == "__main__":
    main()