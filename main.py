# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import math
import re
import csv

import requests
from bs4 import BeautifulSoup

CARDS = [
    # '27122',    # Ajani's Chosen
    # '55851',    # Archon of Sun's Grace
    # '73061',    # Brotherhood Outcast
    # '49249',    # Danitha Capashen, Paragon
    # '27944',    # Darksteel Mutation
    # '69764',    # Ghoulish Impetus
    # '59500',    # Killian, Ink Duelist
    # '894',      # Kor Spiritdancer
    # '70255',    # Lord Skitter's Blessing
    # '3203',     # Mesa Enchantress
    # '55945',    # Minion's Return
    # '7197',     # Nomad Mythmaker
    # '70321',    # Not Dead After All
    # '28649',    # Oppressive Rays
    # '75621',    # Redress Fate
    # '60216',    # Resurgent Belief
    # '3190',     # Retether
    # '55835',    # Rise to Glory
    # '6258',     # Second Sunrise
    # '28297',    # Silent Sentinel
    # '11840',    # Spirit Link
    # '54185',    # Starfield Mystic
    # '57980',    # Timely Ward
    # '55973',    # Transcendent Envoy
    # '915',      # Umbra Mystic
    # '10418',    # Winds of Rath
    '5821',     # Nature's Will
    '69124',    # Shelob, Child of Ungoliant
    '69216',    # Shelob, Dread Weaver
    '69046',    # Shelob's Ambush 
]

LOJAS = [
    'baraogeekhouse',
    'blackwizards',
    'cardtutor',
    'magicdomain',
    'epicgame',
    'meruru',
    'montshop',
    'nergeek',
    'power9',
    'totemmtg',
    'playeasycards'
]

BASE_URLS = [f'https://www.{loja}.com.br/' for loja in LOJAS]

QUALITIES = ['NM', 'SP', 'MP', 'HP', 'D']

WANTED_QUALITIES = ['NM', 'SP', 'MP', 'HP']

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0'}

QUALITY_INDEX = 5
STOCK_INDEX = 9
PRICE_INDEX = 11


def beautify_stock(tag):
    regex = re.compile(r'\d+')
    return int(regex.findall(tag.contents[2])[0])


def beautify_price(tag):
    regex = re.compile(r'[-+]?(?:\d*\,*\d+)')

    preco_com_desconto = tag.find(class_='preco_com_desconto')
    if preco_com_desconto:
        preco = preco_com_desconto.find('font', color='red')
        number_as_string = regex.findall(preco.contents[0])[0]
    else:
        number_as_string = regex.findall(tag.contents[2])[0]
    number = float(number_as_string.replace(',', '.'))
    return number


def beautify_quality(tag):
    quality = tag.find(string=re.compile("|".join(QUALITIES)))
    return quality.strip()


def scrape_on_url(url):
    response = requests.get(url, headers=HEADERS)
    html = response.text

    soup = BeautifulSoup(html, 'html.parser')

    table = soup.find(class_='table-cards-body')
    table_rows = table.find_all(class_='table-cards-row')

    min_price = math.inf
    best_card = {}
    for index, row in enumerate(table_rows):
        stock = beautify_stock(row.contents[STOCK_INDEX])
        if stock > 0:
            price = beautify_price(row.contents[PRICE_INDEX])
            quality = beautify_quality(row.contents[QUALITY_INDEX])
            if quality in WANTED_QUALITIES:
                if price < min_price:
                    min_price = price
                    best_card = {
                        'quality': quality,
                        'price': price,
                        'stock': stock,
                        'index': index
                    }
    return best_card

def get_cards_on_all_url(query_card_id):
    print(f'Searching for card: "{query_card_id}"')
    cards = []
    min_price = math.inf
    selected_card = {}
    for base_url in BASE_URLS:
        print(f'\tin base url: "{base_url}"')
        url = f'{base_url}?view=ecom/item&tcg=1&card={query_card_id}'
        if base_url == 'https://www.ligapokemon.com.br/':
            url = url + '&id=61957'
        card = scrape_on_url(url)
        cards.append(card)
        if card and card.get('price') < min_price:
            min_price = card.get('price')
            selected_card = {
                'card': card,
                'url': url,
            }
    return cards, selected_card


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    all_cards_csv = ['Card ID'] + LOJAS
    selected_cards_csv = ['Card ID', 'Qualidade', 'Preco', 'Estoque', 'Linha', 'URL']
    with open('todas_cartas.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(all_cards_csv)
    with open('melhor_carta.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(selected_cards_csv)
    for card in CARDS:
        cards, selected_card = get_cards_on_all_url(card)
        all_cards = [x_card.get('price') or '-' for x_card in cards]
        all_cards_csv_row = [card] + all_cards
        selected_card_card = selected_card.get('card')
        selected_card_csv_row = [
            card,
            selected_card_card.get('quality'),
            selected_card_card.get('price'),
            selected_card_card.get('stock'),
            selected_card_card.get('index') + 1,
            selected_card.get('url')
        ]
        with open('todas_cartas.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(all_cards_csv_row)
        with open('melhor_carta.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(selected_card_csv_row)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
