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
    headers = {"User-Agent": "Mozilla/5.0 (compatible; Bot/1.0)"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    raw_ogloszenia = soup.find_all('div', class_='box_content_plain') + soup.find_all('div', class_='box_content_featured')

    teraz = datetime.now(POLAND_TZ)
    print(f"🕒 Teraz: {teraz.strftime('%Y-%m-%d %H:%M:%S %Z')}")

    limit = timedelta(minutes=30)
    max_age = timedelta(hours=1)
    sent_links = set()
    ogloszenia = []

    for ogloszenie in raw_ogloszenia:
        data_div = ogloszenie.find('div', class_='box_content_date')
        link_tag = ogloszenie.find('a', href=True)

        if data_div and link_tag and 'dzisiaj' in data_div.text.lower():
            parts = data_div.text.lower().split(",")
            if len(parts) > 1:
                godzina_str = parts[1].strip()
                try:
                    godzina_obj = datetime.strptime(godzina_str, "%H:%M")
                    # Poprawne ustawienie strefy czasowej przez replace:
                    ogloszenie_datetime = datetime.combine(teraz.date(), godzina_obj.time()).replace(tzinfo=POLAND_TZ)

                    link = link_tag['href'].strip()
                    if not link.startswith("http"):
                        link = "https://www.tarnowiak.pl" + link

                    ogloszenia.append((ogloszenie_datetime, godzina_str, link))
                except Exception as e:
                    print("⚠️ Błąd parsowania godziny:", e)

    ogloszenia.sort()

    for ogloszenie_datetime, godzina_str, link in ogloszenia:
        roznica = teraz - ogloszenie_datetime

        # DEBUG: wypisz szczegóły czasu i różnicę
        print(f"DEBUG -> teraz: {teraz} ({teraz.tzinfo}), ogloszenie_datetime: {ogloszenie_datetime} ({ogloszenie_datetime.tzinfo}), roznica: {roznica}")

        if timedelta(seconds=0) <= roznica <= max_age:
            if roznica <= limit:
                if link not in sent_links:
                    print("✅ Wysyłamy nowe ogłoszenie.")
                    message = f"🆕 Nowe ogłoszenie z {godzina_str}:\n{link}"
                    send_telegram_message(message)
                    sent_links.add(link)
                else:
                    print("ℹ️ Już wysłane w tej sesji.")
            else:
                print("⛔ Zbyt stare (>30 minut), pomijam.")
        else:
            print("⛔ Zbyt stare (>1h) lub z przyszłości — pomijam.")

def main():
    teraz = datetime.now(POLAND_TZ)
    print(f"📡 Start o {teraz.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    try:
        check_announcements()
    except Exception as e:
        print("❌ Błąd:", e)

if __name__ == "__main__":
    main()