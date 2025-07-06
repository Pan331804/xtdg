import requests
from bs4 import BeautifulSoup, Tag
import os
import asyncio
from telegram import Bot

# Zmienne środowiskowe (ustaw w GitHub Secrets: TOKEN i CHAT_ID)
TOKEN = os.getenv('8082349732:AAFAYY8Y95yGUel8Ymnl84MpCEgpTUQ9L8k')
CHAT_ID = os.getenv('7728443508')

# Tworzymy instancję bota
bot = Bot(token=TOKEN)

# Funkcja asynchroniczna do wysyłania wiadomości
async def wyslij_telegrama(text):
    await bot.send_message(chat_id=CHAT_ID, text=text)

# Funkcja główna
async def main():
    # Adres URL
    url = 'https://www.tarnowiak.pl/szukaj/?ctg=31&p=1&q=&pf=&pt='
    BASE_URL = 'https://www.tarnowiak.pl'

    response = requests.get(url)

    # Sprawdzenie statusu
    if response.status_code == 200:
        print("Strona pobrana pomyślnie")
    else:
        print("Błąd", response.status_code)
        return

    # Tworzenie soup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Wczytanie stare linki
    Ogłoszenia_stare_file = 'Ogłoszenia_linki_stare.txt'
    if os.path.exists(Ogłoszenia_stare_file):
        with open(Ogłoszenia_stare_file, 'r') as f:
            Ogłoszenia_stare = set(f.read().splitlines())
    else:
        Ogłoszenia_stare = set()

    # Szukanie linków
    ogłoszenia_div = soup.find('div', id='content')
    nowe_linki = []

    if ogłoszenia_div and isinstance(ogłoszenia_div, Tag):
        links = ogłoszenia_div.find_all('a')
        for link in links:
            if isinstance(link, Tag):
                href = link.get('href')
                if href and isinstance(href, str):
                    full_url = href if href.startswith('http') else BASE_URL + href
                    if full_url not in Ogłoszenia_stare:
                        await wyslij_telegrama(f"Znaleziono nowy link: {full_url}")
                        nowe_linki.append(full_url)
                        Ogłoszenia_stare.add(full_url)
    else:
        print("Nie znaleziono elementu 'content'.")

    # Zapisz nowe linki do pliku
    if nowe_linki:
        with open(Ogłoszenia_stare_file, 'a') as f:
            for link in nowe_linki:
                f.write(link + '\n')

# Uruchomienie funkcji głównej
if __name__ == '__main__':
    asyncio.run(main())
