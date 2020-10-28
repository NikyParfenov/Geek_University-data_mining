import scrapy
from pymongo import MongoClient


class YoulaSpider(scrapy.Spider):
    name = 'youla'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['https://auto.youla.ru/']

    xpath = {
        'brands': '//div[@class="TransportMainFilters_brandsList__2tIkv"]//a[@class="blackLink"]/@href',
        'ads': '//div[@id="serp"]//article//a[@data-target="serp-snippet-title"]/@href',
        'pagination': '//div[contains(@class, "Paginator_block")]/a/@href',
    }
    db_client = MongoClient('mongodb://localhost:27017')

    # parsing start urls
    def parse(self, response, **kwargs):
        for url in response.xpath(self.xpath['brands']):
            yield response.follow(url, callback=self.brand_parse)

    # parsing brands of auto
    def brand_parse(self, response, **kwargs):
        for url in response.xpath(self.xpath['pagination']):
            yield response.follow(url, callback=self.brand_parse)
        print(1)
        for url in response.xpath(self.xpath['ads']):
            yield response.follow(url, callback=self.ads_parse)

    # parsing advertisements
    def ads_parse(self, response, **kwargs):
        name = response.xpath('//div[contains(@class, "AdvertCard_advertTitle")]/text()').extract_first()
        images = response.xpath('//div[contains(@class, "PhotoGallery_block")]//img/@src').extract()
        tech_key = response.xpath('//div[contains(@class, "AdvertSpecs_label")]/text()').extract()
        tech_value = response.xpath('//div[contains(@class, "AdvertSpecs_data")]//text()').extract()
        tech_data = list(zip(tech_key, tech_value))
        description = response.xpath('//div[contains(@class, "AdvertCard_descriptionInner")]/text()').extract_first()
        owner = None
        phone_num = None
        collection = self.db_client['db_parse_10-2020'][self.name]
        collection.insert_one({'title': name,
                               'img': images,
                               'tech_data': tech_data,
                               'description': description,
                               'owner': owner,
                               'phone_num': phone_num,
                               })
        # print(1)
