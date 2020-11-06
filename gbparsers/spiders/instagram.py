import scrapy
import json
from datetime import datetime
from ..items import InstagramTagsItem, InstagramPostsItem


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']
    pagination_url = 'https://www.instagram.com/graphql/query/'
    query_hash = '9b498c08113f1e09617a1703c22b2f32'
    __login_url = 'https://www.instagram.com/accounts/login/ajax/'

    def __init__(self, login, enc_password, *args, **kwargs):
        self.tags = ['python', 'pythonprogramming']
        self.__login = login
        self.__enc_password = enc_password
        super().__init__(*args, **kwargs)

    def parse(self, response, **kwargs):
        try:
            js_data = self.js_data_extract(response)
            yield scrapy.FormRequest(
                self.__login_url,
                method='POST',
                callback=self.parse,
                formdata={
                    'username': self.__login,
                    'enc_password': self.__enc_password,
                },
                headers={'X-CSRFToken': js_data['config']['csrf_token']},
            )
        except AttributeError as e:
            if response.json().get('authenticated'):
                for tag in self.tags:
                    yield response.follow(f'/explore/tags/{tag}/', callback=self.tag_parse, cb_kwargs={'param': tag})

    def tag_parse(self, response, **kwargs):
        hashtag = self.js_data_extract(response)['entry_data']['TagPage'][0]['graphql']['hashtag']
        yield InstagramTagsItem(date_parse=datetime.now(),
                                data={'id': hashtag['id'], 'name': hashtag['name']},
                                img=[hashtag['profile_pic_url']],
                                )
        # for post in self.load_posts(response, hashtag):
        #     yield post
        yield from self.load_posts(response, hashtag)

    def load_posts(self, response, hashtag):
        # pagination (lazy loading)
        if hashtag['edge_hashtag_to_media']['page_info']['has_next_page']:
            query_variables = {"tag_name": hashtag['name'],
                               "first": 100,
                               "after": hashtag['edge_hashtag_to_media']['page_info']['end_cursor']}
            url = f'{self.pagination_url}?query_hash={self.query_hash}&variables={json.dumps(query_variables)}'
            yield response.follow(url, callback=self.pagination_parse)

        # for post in self.post_parse(hashtag):
        #     yield post
        yield from self.post_parse(hashtag)

    def pagination_parse(self, response):
        # for edge in self.load_posts(response, response.json()['data']['hashtag']):
        #     yield edge
        yield from self.load_posts(response, response.json()['data']['hashtag'])

    @staticmethod
    def post_parse(edges):
        for edge in edges['edge_hashtag_to_media']['edges']:
            yield InstagramPostsItem(date_parse=datetime.now(),
                                     data=edge['node'],
                                     img=[edge['node']['display_url']],
                                     )

    @staticmethod
    def js_data_extract(response):
        script = response.xpath('//script[contains(text(), "window._sharedData =")]/text()').get()
        return json.loads(script.replace('window._sharedData =', '')[:-1])
