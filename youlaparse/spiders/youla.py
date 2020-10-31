import scrapy
from ..loaders import YoulaAutoLoader, HeadHunterRemoteJobsLoader, HeadHunterJobsCompanyLoader


class YoulaSpider(scrapy.Spider):
    name = 'youla'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['https://auto.youla.ru/']

    xpath = {
        'brands': '//div[@class="TransportMainFilters_brandsList__2tIkv"]//a[@class="blackLink"]/@href',
        'ads': '//div[@id="serp"]//article//a[@data-target="serp-snippet-title"]/@href',
        'pagination': '//div[contains(@class, "Paginator_block")]/a/@href',
    }

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

    # parsing advertisements
    def ads_parse(self, response, **kwargs):
        loader = YoulaAutoLoader(response=response)
        loader.add_xpath('title', '//div[contains(@class, "AdvertCard_advertTitle")]/text()')
        loader.add_xpath('img', '//div[contains(@class, "PhotoGallery_block")]//img/@src')
        loader.add_xpath('owner', '//script[contains(text(), "window.transitState =")]/text()')
        loader.add_xpath('phone_num', '//script[contains(text(), "window.transitState =")]/text()')
        loader.add_value('url', response.url)
        loader.add_value('tech_data', '//div[contains(@class, "AdvertCard_specs")]'
                                      '//div[contains(@class, "AdvertSpecs")]')
        loader.add_xpath('description', '//div[contains(@class, "AdvertCard_descriptionInner")]/text()')
        yield loader.load_item()


class HeadHunterSpider(scrapy.Spider):
    name = 'hh'
    allowed_domains = ['spb.hh.ru']
    start_urls = ['https://spb.hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113']

    xpath = {
        'vacancies': '//div[@class="vacancy-serp"]//a[contains(@class, "HH-LinkModifier")]/@href',
        'pagination': '//div[contains(@class, "bloko-gap")]//a[contains(@class, "HH-Pager-Controls-Next")]/@href',
        'company': '//div[@class="vacancy-company-name-wrapper"]/a/@href',
        'company_vacancies': '//div[@class="employer-sidebar-content"]/div[@class="employer-sidebar-block"]/a/@href',
    }

    # parsing basic page with remote vacancies
    def parse(self, response, **kwargs):
        # follow to a next page
        for url in response.xpath(self.xpath['pagination']):
            yield response.follow(url, callback=self.parse)
        # follow to a vacancy page
        for url in response.xpath(self.xpath['vacancies']):
            yield response.follow(url, callback=self.vacancy_parse)

    # parsing vacancies
    def vacancy_parse(self, response, **kwargs):
        loader = HeadHunterRemoteJobsLoader(response=response)
        loader.add_value('url', response.url)
        loader.add_xpath('title', '//div[@class="vacancy-title"]//h1/text()')
        loader.add_xpath('salary', '//div[@class="vacancy-title"]//p[@class="vacancy-salary"]//text()')
        loader.add_xpath('description', '//div[@class="vacancy-section"]/div[@class="g-user-content"]//text()')
        loader.add_xpath('skills', '//div[@class="bloko-tag-list"]/div//span/text()')
        loader.add_xpath('owner_url', self.xpath['company'])
        yield loader.load_item()

        # follow to a vacancy of a company
        for url in response.xpath(self.xpath['company']):
            yield response.follow(url, callback=self.company_parse)

    # parse a company page
    def company_parse(self, response, **kwargs):
        loader = HeadHunterJobsCompanyLoader(response=response)
        loader.add_value('url', response.url)
        loader.add_xpath('title', '//div[@class="employer-sidebar-header"]//span//text()')
        loader.add_xpath('company_url', '//div[@class="employer-sidebar-content"]/a/@href')
        loader.add_xpath('field_of_work', '//div[@class="employer-sidebar-block"]/p/text()')
        loader.add_xpath('description', '//div[@class="company-description"]/div[@class="g-user-content"]//text()')
        yield loader.load_item()

        # follow to an company's vacancies
        for url in response.xpath(self.xpath['company_vacancies']):
            yield response.follow(url, callback=self.parse)
