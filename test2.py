import requests
from bs4 import BeautifulSoup, Tag
import os
import asyncio
from telegram import Bot


TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Twój token i chat_id
TOKEN = '8082349732:AAFAYY8Y95yGUel8Ymnl84MpCEgpTUQ9L8k'
CHAT_ID = '7728443508'

# Tworzymy instancję bota
bot = Bot(token=TOKEN)

# Funkcja asynchroniczna do wysyłania wiadomości
async def wyslij_telegrama(text):
    await bot.send_message(chat_id=CHAT_ID, text=text)

# Funkcja główna
async def main():
    # Adres URL
    url = 'https://www.tarnowiak.pl/szukaj/?ctg=31&p=1&q=&pf=&pt='
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
                    if href not in Ogłoszenia_stare:
                        # Wyślij wiadomość asynchronicznie
                        await wyslij_telegrama(f"Znaleziono nowy link: {href}")
                        nowe_linki.append(href)
                        Ogłoszenia_stare.add(href)
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
