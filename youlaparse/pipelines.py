# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient


class YoulaparsePipeline:
    def __init__(self):
        db_client = MongoClient('mongodb://localhost:27017')
        self.db = db_client['db_parse_10-2020']

    def process_item(self, item, spider):
        collection = self.db[spider.name]
        collection.insert_one(item)
        return item


class HeadHunterPipeline:
    def __init__(self):
        db_client = MongoClient('mongodb://localhost:27017')
        self.db = db_client['db_parse_10-2020']

    def process_item(self, item, spider):
        collection = self.db[spider.name]
        collection.insert_one(item)
        return item
