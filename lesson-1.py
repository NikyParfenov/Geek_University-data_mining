import requests
import json
import time


class Parser5ka:

    __params = {
        'records_per_page': 50,
    }
    __headers = {
        'User-Agent': 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0'
    }

    def __init__(self, start_url):
        self.start_url = start_url

    def parse(self, url=None):
        """
        Method parse all data with special offers to products folder
        """
        if not url:
            url = self.start_url

        params = self.__params

        # log file for queries
        log_file = open('products/query_log.txt', 'w', encoding='UTF-8')

        while url:
            time.sleep(0.1)  # parsing speed 0.1 sec
            response = requests.get(url, params=params, headers=self.__headers)
            log_file.write(f'{response.url}\n')
            if params:
                params = {}
            data: dict = response.json()
            url = data['next']
            for item in data['results']:
                self.save_to_json_file(item)

        log_file.close()

    def cat_parse(self, cat_url: str, url=None):
        """
        Method parse all data with special offers divided by categories to categories folder
        """
        # get categories
        cat_response = requests.get(cat_url)

        # log file for queries
        log_file = open('categories/query_log.txt', 'w', encoding='UTF-8')

        # run cicle for each category
        for category in cat_response.json():
            params = self.__params
            params['categories'] = category["parent_group_code"]
            if not url:
                url = self.start_url

            while url:
                time.sleep(0.1)  # parsing speed 0.1 sec
                response = requests.get(url, params=params, headers=self.__headers)
                log_file.write(f'{response.url}\n')
                if params:
                    params = {}
                data: dict = response.json()
                url = data['next']
                # merge the data in required format
                categories = {"name": category["parent_group_name"],
                              "code": category["parent_group_code"],
                              "products": data['results']}
                # file names can contain 'name' or 'code', as you wish
                self.save_to_json_file(categories, index='code', folder='categories')
        log_file.close()

    def save_to_json_file(self, product: dict, index='id', folder='products'):
        with open(f'{folder}/{product[index]}.json', 'w', encoding='UTF-8') as file:
            json.dump(product, file, ensure_ascii=False)


if __name__ == '__main__':
    parser = Parser5ka('https://5ka.ru/api/v2/special_offers/')
    # parser.parse()
    parser.cat_parse(cat_url='https://5ka.ru/api/v2/categories/')
