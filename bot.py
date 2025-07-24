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
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; Bot/1.0; +https://github.com/your-repo)"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    ogloszenia = soup.find_all('div', class_='box_content_plain') + soup.find_all('div', class_='box_content_featured')

    teraz = datetime.now(POLAND_TZ)

    for ogloszenie in ogloszenia:
        data_div = ogloszenie.find('div', class_='box_content_date')
        if data_div and 'dzisiaj' in data_div.text.lower():
            parts = data_div.text.lower().split(",")
            if len(parts) > 1:
                godzina_str = parts[1].strip()
                try:
                    godzina_obj = datetime.strptime(godzina_str, "%H:%M")

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