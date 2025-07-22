import requests
from bs4 import BeautifulSoup, Tag
import os
import asyncio
from telegram import Bot

TOKEN = os.getenv('TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

bot = Bot(token=TOKEN)

async def wyslij_telegrama(text):
    await bot.send_message(chat_id=CHAT_ID, text=text)

async def main():
    url = 'https://www.tarnowiak.pl/szukaj/?ctg=31&p=1&q=&pf=&pt='
    BASE_URL = 'https://www.tarnowiak.pl'

    response = requests.get(url)

    if response.status_code == 200:
        print("Strona pobrana pomyślnie")
    else:
        print("Błąd", response.status_code)
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    Ogłoszenia_stare_file = 'Ogłoszenia_linki_stare.txt'
    if os.path.exists(Ogłoszenia_stare_file):
        with open(Ogłoszenia_stare_file, 'r') as f:
            Ogłoszenia_stare = set(f.read().splitlines())
    else:
        Ogłoszenia_stare = set()

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
                        nowe_linki.append(full_url)
                        Ogłoszenia_stare.add(full_url)
    else:
        print("Nie znaleziono elementu 'content'.")

    if nowe_linki:
        # Budujemy wiadomość ze wszystkimi linkami
        message = "Znaleziono nowe linki:\n" + "\n".join(nowe_linki)
        await wyslij_telegrama(message)

        # Dopisujemy nowe linki do pliku
        with open(Ogłoszenia_stare_file, 'a') as f:
            for link in nowe_linki:
                f.write(link + '\n')

if __name__ == '__main__':
    asyncio.run(main())