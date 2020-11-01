from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from gbparsers import settings
from gbparsers.spiders.youla import YoulaSpider
from gbparsers.spiders.hh import HeadHunterSpider

if __name__ == '__main__':
    crawl_settings = Settings()
    crawl_settings.setmodule(settings)
    crawl_process = CrawlerProcess(settings=crawl_settings)
    # crawl_process.crawl(YoulaSpider)
    crawl_process.crawl(HeadHunterSpider)
    crawl_process.start()
