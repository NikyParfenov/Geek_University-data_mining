import os
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from pymongo import MongoClient
from gbparsers import settings
from dotenv import load_dotenv
from gbparsers.spiders.youla import YoulaSpider
from gbparsers.spiders.hh import HeadHunterSpider
from gbparsers.spiders.instagram import InstagramSpider

load_dotenv('.env')

if __name__ == '__main__':
    crawl_settings = Settings()
    crawl_settings.setmodule(settings)
    crawl_process = CrawlerProcess(settings=crawl_settings)
    # crawl_process.crawl(YoulaSpider)
    # crawl_process.crawl(HeadHunterSpider)
    # users = ['adamnee']
    # crawl_process.crawl(InstagramSpider,
    #                     users=users,
    #                     login=os.getenv('LOGIN'),
    #                     enc_password=os.getenv('ENC_PASSWORD'))
    # crawl_process.start()

    def get_from_mongodb(database: str, table: str, elements: dict, multiple=False) -> list:
        """
        Method gets grouped by element documents from mongoDB
        :param table: str
        :param database: str
        :param elements: dict
        :param multiple: one doc or multiple
        :return: list
        """
        db_client = MongoClient('mongodb://localhost:27017')
        db = db_client[database]
        collection = db[table]
        if multiple:
            products = collection.find(elements)
            docs = [_ for _ in products]
            print(f'{len(docs)} документов получено из DB "{database}" с параметрами {elements}')
            return docs
        else:
            print(f'Один документ получен из DB "{database}" с параметрами {elements}')
            return collection.find_one(elements)


    def determine_friends(database: str, table: str, user: str):
        user_followers = get_from_mongodb(database, table, {'user_name': user}, multiple=True)
        user_followings = get_from_mongodb(database, table, {'follow_name': user}, multiple=True)
        user_friends = []
        for item_followings in user_followings:
            for item_followers in user_followers:
                if item_followings['user_name'] == item_followers['follow_name']:
                    user_friends.append(item_followings['user_name'])
                    break
        return user_friends


    def handshake(user1, user2):
        users = user1
        finder = False
        while not finder:
            users_parse_list = []
            for user in users:
                crawl_process.crawl(InstagramSpider,
                                    users=user,
                                    login=os.getenv('LOGIN'),
                                    enc_password=os.getenv('ENC_PASSWORD'))
                crawl_process.start()
                user1_friends = determine_friends('db_parse_10-2020', 'InstagramUserFollowItems', user)
                if user1_friends.count(user2):
                    finder = True
                else:
                    users_parse_list.extend(user1_friends)
            users = users_parse_list


    handshake('ks_parfenova15', '_dinara_safronova')
