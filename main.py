# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import math
import re
import csv

import requests
from bs4 import BeautifulSoup

CARDS = [
    '58830',
    '69089',
    '28455',
    '3505',
    '370',
    '1920',
    '52813',
    '4901',
    '61963',
    '708',
    '25866',
    '6439',
    '12286',
    '55946',
    '74225',
    '30650',
    '51748',
    '6048',
    '51791',
    '4865',
    '3415',
    '30605',
    '3295',
]

LOJAS = [
    'baraogeekhouse',
    'blackwizards',
    'cardtutor',
    'magicdomain',
    'epicgame',
    'meruru',
    'montshop',
    'ligapokemon',
    'power9',
]

BASE_URLS = [f'https://www.{loja}.com.br/' for loja in LOJAS]

QUALITIES = ['NM', 'SP', 'MP', 'HP', 'D']

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0'}

quality_index = 5
stock_index = 9
price_index = 11


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
        stock = beautify_stock(row.contents[stock_index])
        if stock > 0:
            price = beautify_price(row.contents[price_index])
            quality = beautify_quality(row.contents[quality_index])
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
