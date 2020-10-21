import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from urllib.parse import urlparse
import time
from datetime import datetime


# russian month translator for datetime
month = {
    'января': 1,
    'февраля': 2,
    'марта': 3,
    'апреля': 4,
    'мая': 5,
    'июня': 6,
    'июля': 7,
    'августа': 8,
    'сентября': 9,
    'октября': 10,
    'ноября': 11,
    'декабря': 12,
}


class MagnitParser:
    _headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0",
    }
    _params = {
        'geo': 'sankt-peterbur',
    }

    def __init__(self, start_url):
        self.start_url = start_url
        self._url = urlparse(start_url)
        mongo_client = MongoClient('mongodb://localhost:27017')
        self.db = mongo_client['db_parse_10-2020']

    def _get_soup(self, url: str):
        response = requests.get(url, headers=self._headers, params=self._params)
        return BeautifulSoup(response.text, 'lxml')

    def parse(self):
        soup = self._get_soup(self.start_url)
        catalog = soup.find('div', attrs={'class': 'сatalogue__main'})
        products = catalog.findChildren('a', attrs={'class': 'card-sale'})

        counter = 0
        for product in products:
            if len(product.attrs.get('class')) > 2 or product.attrs.get('href')[0] != '/':
                continue
            time.sleep(0.1)
            product_url = f'{self._url.scheme}://{self._url.hostname}{product.attrs.get("href")}'
            product_soup = self._get_soup(product_url)
            product_data = self.get_product_structure(product_soup, product_url)
            self.save_to(product_data)
            counter += 1
            # добавим счетчик, чтобы видеть прогресс (в массиве 2 элемента, не относящихся к товарам)
            print(f'Обработан {counter}-й товар из {len(products)-2}')

    def get_product_structure(self, product_soup, url):
        product_template = {
            'promo_name': ('p', 'action__name-text', 'text'),
            'product_name': ('div', 'action__title', 'text'),
            'old_price': ('div', 'label__price label__price_old', 'text'),
            'new_price': ('div', 'label__price label__price_new', 'text'),
            'image_url': ('img', 'action__image lazy', 'get'),
            'date_from': ('div', 'action__date-label', 'text'),
            'date_to': ('div', 'action__date-label', 'text'),
        }
        product = {'url': url}
        for key, value in product_template.items():
            try:
                # на странице несколько одинаковых классов new/old, поэтому подключаем findChild
                if key.count('price'):
                    prod = product_soup.findChild('div', attrs={'class': 'action__footer'})
                    prod = '.'.join(getattr(prod.find(value[0], attrs={'class': value[1]}), value[2]).split())
                    product[key] = float(prod)
                # image-url собираем из нескольких кусочков
                elif key == 'image_url':
                    prod = getattr(product_soup.find(value[0], attrs={'class': value[1]}), value[2])('data-src')
                    product[key] = f'{urlparse(url).scheme}://{urlparse(url).hostname}{prod}'
                # есть 2 формата дат: "c DD month по DD month" и "только DD month"
                elif key == 'date_from':
                    prod = getattr(product_soup.find(value[0], attrs={'class': value[1]}), value[2]).split(' ')
                    product[key] = datetime.strptime(f'{prod[1]} '
                                                     f'{month[prod[2]]} '
                                                     f'{datetime.now().year}', "%d %m %Y")
                elif key == 'date_to':
                    prod = getattr(product_soup.find(value[0], attrs={'class': value[1]}), value[2]).split(' ')
                    product[key] = datetime.strptime(f'{prod[-2]} '
                                                     f'{month[prod[-1]]} '
                                                     f'{datetime.now().year}', "%d %m %Y")
                else:
                    product[key] = getattr(product_soup.find(value[0], attrs={'class': value[1]}), value[2])
            except Exception:
                product[key] = None
        return product

    def save_to(self, product_data: dict):
        collection = self.db['magnit']
        collection.insert_one(product_data)

    def get_from_mongodb(self, database: str, elements: dict, multiple=False) -> list:
        """
        Method gets grouped by element documents from mongoDB
        :param database: str
        :param elements: dict
        :param multiple: one doc or multiple
        :return: list
        """
        collection = self.db[database]
        if multiple:
            products = collection.find(elements)
            docs = [_ for _ in products]
            print(f'{len(docs)} документов получено из DB "{database}" с параметрами {elements}')
            return docs
        else:
            print(f'Один документ получен из DB "{database}" с параметрами {elements}')
            return collection.find_one(elements)


if __name__ == '__main__':
    url = 'https://magnit.ru/promo/'
    parser = MagnitParser(url)
    parser.parse()

    products_mongodb = parser.get_from_mongodb('magnit', {'promo_name': '1+1'}, multiple=True)
