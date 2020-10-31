from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from youlaparse import settings
from youlaparse.spiders.youla import YoulaSpider, HeadHunterSpider

if __name__ == '__main__':
    crawl_settings = Settings()
    crawl_settings.setmodule(settings)
    crawl_process = CrawlerProcess(settings=crawl_settings)
    # crawl_process.crawl(YoulaSpider)
    crawl_process.crawl(HeadHunterSpider)
    crawl_process.start()
