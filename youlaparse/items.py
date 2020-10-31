# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class YoulaparseItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class YoulaAutoItem(scrapy.Item):
    _id = scrapy.Field()
    title = scrapy.Field()
    img = scrapy.Field()
    url = scrapy.Field()
    tech_data = scrapy.Field()
    description = scrapy.Field()
    owner = scrapy.Field()
    phone_num = scrapy.Field()


class HeadHunterRemoteJobsItem(scrapy.Item):
    _id = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    salary = scrapy.Field()
    description = scrapy.Field()
    skills = scrapy.Field()
    owner_url = scrapy.Field()


class HeadHunterJobsCompanyItem(scrapy.Item):
    _id = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    company_url = scrapy.Field()
    field_of_work = scrapy.Field()
    description = scrapy.Field()
