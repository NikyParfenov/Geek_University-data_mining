import scrapy
import re
import base64
from pymongo import MongoClient
from urllib.parse import unquote


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

        for url in response.xpath(self.xpath['ads']):
            yield response.follow(url, callback=self.ads_parse)

    # javascript decoder
    def js_decoder(self, response, **kwargs):
        find_script = response.xpath('//script[contains(text(), "window.transitState =")]/text()').get()
        find_owner_id = re.compile(r"youlaId%22%2C%22([0-9a-zA-Z]+)%22%2C%22avatar")
        find_dealer_id = re.compile("page%22%2C%22(https%3A%2F%2Fam.ru%2Fcardealers%2F[0-9a-zA-Z\S]+%2F%23info)"
                                    "%22%2C%22salePointLogo")
        person = re.findall(find_owner_id, find_script)
        dealer = re.findall(find_dealer_id, find_script)
        owner = f'https://youla.ru/user/{person[0]}' if person else unquote(dealer[0])

        find_owner_phone = re.compile(r"phone%22%2C%22([0-9a-zA-Z]{33}w%3D%3D)%22%2C%22time")
        phone_num_encoded = re.findall(find_owner_phone, find_script)
        phone_num_decoded_1stage = base64.b64decode(unquote(phone_num_encoded[0]).encode('utf-8'))
        phone_num_decoded_2stage = base64.b64decode(phone_num_decoded_1stage)
        phone_num = phone_num_decoded_2stage.decode('utf-8')

        return owner, phone_num

    # parsing advertisements
    def ads_parse(self, response, **kwargs):
        name = response.xpath('//div[contains(@class, "AdvertCard_advertTitle")]/text()').extract_first()
        images = response.xpath('//div[contains(@class, "PhotoGallery_block")]//img/@src').extract()

        tech_key = response.xpath('//div[contains(@class, "AdvertSpecs_label")]/text()').extract()
        tech_value = response.xpath('//div[contains(@class, "AdvertSpecs_data")]//text()').extract()
        tech_data = dict(zip(tech_key, tech_value))

        description = response.xpath('//div[contains(@class, "AdvertCard_descriptionInner")]/text()').extract_first()

        owner, phone_num = self.js_decoder(response)

        collection = self.db_client['db_parse_10-2020'][self.name]
        collection.insert_one({'title': name,
                               'img': images,
                               'tech_data': tech_data,
                               'description': description,
                               'owner': owner,
                               'phone_num': phone_num,
                               })
