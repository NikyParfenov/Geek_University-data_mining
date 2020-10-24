import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time
from datetime import datetime
from lesson_3_db import SessionMaker
import lesson_3_models as models


class GeekBrainsParser:
    _headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0",
    }

    def __init__(self, start_url):
        self.start_url = start_url
        self._url = urlparse(start_url)

    def _get_soup(self, url: str, params=None):
        """
        Method for getting soup from html page
        """
        response = requests.get(url, params=params, headers=self._headers)
        return BeautifulSoup(response.text, 'lxml')

    def parse(self):
        """
        Main parser method
        """
        page = 1
        blog_pages = 1
        while page <= blog_pages:
            params = {
                'page': page,
            }
            soup = self._get_soup(self.start_url, params)
            pagination = soup.find('ul', attrs={'class': 'gb__pagination'}).findChildren('a')
            blog_pages = int(pagination[len(pagination)-2].text)  # estimate pages number
            blogs = soup.find('div', attrs={'class': 'post-items-wrapper'}).findChildren('a')

            for blog in blogs:
                if blog.attrs.get('href')[0] != '/':
                    continue
                time.sleep(0.1)
                blog_url = f'{self._url.scheme}://{self._url.hostname}{blog.attrs.get("href")}'
                blog_soup = self._get_soup(blog_url)
                blog_data = self.get_blog_structure(blog_soup, blog_url)
                # print(1)
                # self.save_to(blog_data)  # Is not ready! In process...
            # print(1)
            page += 1

    def comment_parse(self, comments_id: str) -> list:
        """
        Method for comments parsing in posts pages
        :param comments_id: str
        :return: list
        """
        params = {
            'commentable_type': 'Post',
            'commentable_id': comments_id,
            'order': 'desc'
        }
        headers = self._headers
        headers.update({'Range': '0-500'})
        comments_url = f'{urlparse(url).scheme}://{urlparse(url).hostname}/api/v2/comments'
        response = requests.get(comments_url, params=params, headers=headers)
        comments_data: list = response.json()

        def get_comments(data: list) -> list:
            """
            Recursion function uses for obtaining nested comments:
            [[writer, writer_url, comment, [answer_writer, answer_writer_url, answer_comment, [...]]], [...]]
            :param data: list
            :return: list
            """
            result = []
            for item in data:
                comment = [item['comment']['user']['full_name'],
                           item['comment']['user']['url'],
                           item['comment']['body'],
                           get_comments(item['comment']['children']),
                           ]
                result.append(comment)
            return result

        comments_list = get_comments(comments_data)
        return comments_list

    def get_blog_structure(self, blog_soup, url: str) -> dict:
        """
        Method combine the data into required structure
        :param url: str
        :return: dict
        """
        comments_parser = self.comment_parse(blog_soup.find('comments')['commentable-id'])
        blog_template = {
            'header': lambda soup: soup.find('h1', attrs={'class': 'blogpost-title'}).text,
            'img_url': lambda soup: soup.find('img')['src'],  # link
            'post_date': lambda soup: datetime.fromisoformat(soup.find('time')['datetime']),  # datetime
            'writer': lambda soup: soup.find('div', attrs={'itemprop': 'author'}).text,
            'writer_url': lambda soup: f'{urlparse(url).scheme}://{urlparse(url).hostname}'
                                       f'{soup.find("div", attrs={"itemprop": "author"}).find_parent("a")["href"]}',
            'comments': lambda _: comments_parser,  # [[writer, writer_url, comment, [answer_writer, ..., ..., [...]]
            'tags': lambda soup: [(tag.text, f'{urlparse(url).scheme}://{urlparse(url).hostname}{tag["href"]}')
                                  for tag in soup.find_all('a', attrs={'class': 'small'})],  # [(tag, tag_url), [...]]
        }
        blog = {'url': url}
        for key, value in blog_template.items():
            try:
                blog[key] = value(blog_soup)
            except Exception:
                blog[key] = None
        # print(1)
        return blog

    @staticmethod
    def save_to(blog_data: dict):
        # Is not ready! In process...
        """
        Method-saver
        """
        db = SessionMaker()

        writer = models.Writer(name=blog_data['writer'], url=blog_data['writer_url'])
        db_writer_check = db.query(models.Writer).filter(models.Writer.url == writer.url).first()
        if db_writer_check:
            writer = db_writer_check
        db.add(writer)

        # In process of error solving: TypeError('Incompatible collection type: Post is not list-like')
        post = models.Post(header=blog_data['header'], post_date=blog_data['post_date'],
                           url=blog_data['url'], img_url=blog_data['img_url'], writer=writer)
        db.add(post)

        tag = models.Tag(name=blog_data['tags'][0], url=blog_data['tags'][1], posts=post)  # add connection with post
        db.add(tag)
        post.tag.append(tag)

        target = blog_data['comments']
        while target:
            comment = models.Comment(text=target[2], writer=target[1])
            db.add(comment)
            target = target[3]
        print(1)
        db.commit()
        db.close()


if __name__ == '__main__':
    url = 'https://geekbrains.ru/posts'
    parser = GeekBrainsParser(url)
    parser.parse()


