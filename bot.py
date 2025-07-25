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
SENT_FILE = "sent_announcements.txt"

def load_sent():
    if not os.path.exists(SENT_FILE):
        return set()
    with open(SENT_FILE, "r") as f:
        return set(line.strip() for line in f.readlines())

def save_sent(sent_set):
    with open(SENT_FILE, "w") as f:
        for item in sent_set:
            f.write(item + "\n")

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
    sent = load_sent()

    for ogloszenie in raw_ogloszenia:
        data_div = ogloszenie.find('div', class_='box_content_date')
        link_tag = ogloszenie.find('a', href=True)

        if data_div and link_tag and 'dzisiaj' in data_div.text.lower():
            parts = data_div.text.lower().split(",")
            if len(parts) > 1:
                godzina_str = parts[1].strip()
                try:
                    godzina_obj = datetime.strptime(godzina_str, "%H:%M")
                    ogloszenie_datetime = datetime.combine(teraz.date(), godzina_obj.time(), POLAND_TZ)
                    link = link_tag['href'].strip()
                    if not link.startswith("http"):
                        link = "https://www.tarnowiak.pl" + link
                    ogloszenia.append((ogloszenie_datetime, godzina_str, link))
                except Exception as e:
                    print("⚠️ Błąd parsowania godziny:", e)

    ogloszenia.sort()

    for ogloszenie_datetime, godzina_str, link in ogloszenia:
        roznica = teraz - ogloszenie_datetime
        print(f"🕒 Ogłoszenie: {ogloszenie_datetime} ➡️ Różnica: {roznica}, limit: {limit}")

        if timedelta(seconds=0) <= roznica < limit:
            if link not in sent:
                print("✅ Różnica < 30 minut i nowe ogłoszenie — wysyłamy.")
                message = f"🆕 Nowe ogłoszenie z {godzina_str}:\n{link}"
                send_telegram_message(message)
                sent.add(link)
            else:
                print(f"ℹ️ Ogłoszenie z linkiem {link} już wysłane — pomijam.")
        else:
            print("⛔ Różnica ≥ 30 min lub ujemna — pomijamy.")

    save_sent(sent)

def main():
    teraz = datetime.now(POLAND_TZ)
    print(f"🔄 Sprawdzanie ogłoszeń: {teraz.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    try:
        check_announcements()
    except Exception as e:
        print("❌ Błąd:", e)

if __name__ == "__main__":
    main()