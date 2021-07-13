import json
from time import sleep
from .. import utils
from scrapy import Spider
from scrapy.http import Request, FormRequest, HtmlResponse
from .. import config as cfg


class CardanoSpider(Spider):
    name = "forumCardano"

    def __init__(self, mode, **kwargs):
        super().__init__(**kwargs)
        self.mode = mode

    def start_requests(self):
        if self.mode == 'latest':
            utils.show_message('Crawling:', 'okgreen', self.mode)
            for i in range(cfg.LATEST_PAGE):
                yield Request(url=cfg.FCARDANO_URL + str(i), callback=self.parse)
                sleep(1)
        elif self.mode == 'all':
            utils.show_message('Crawling:', 'okgreen', self.mode)
            for i in range(cfg.FCARDANO_TOTAL_PAGE):
                yield Request(url=cfg.FCARDANO_URL + str(i), callback=self.parse)
                sleep(1)
        else:
            utils.show_message('', 'fail', 'Please retype mode: `latest` or `all`')
            exit()

    def parse(self, response, **kwargs):
        utils.show_message('', 'fail', f'{self.mode.upper()} Forum.Cardano Thread')
        page = response.url
        # get data through HTML form
        utils.show_message('Type response', 'fail', type(response))
        posts = response.css('tr.topic-list-item')
        for post in posts:
            data = {
                'title': post.css('td.main-link span.link-top-line a.raw-topic-link::text').get(),
                'tags': post.css('td.main-link div.link-bottom-line div.discourse-tags a::text').getall(),
                'link_tags': post.css('td.main-link div.link-bottom-line div.discourse-tags a::attr(href)').getall(),
                'link_post': post.css('td.main-link span.link-top-line a::attr(href)').get(),
                'posters': post.css('td.posters a::attr(href)').getall(),
                'avatars': post.css('td.posters a img::attr(src)').getall(),
                'replies': post.css('td.replies span.posts::text').get(),
                'views': post.css('td.views span.views::text').get(),
                'date': post.css('td::text').getall()[-1].strip(),
                'source': 'cardano',
                'latest': 1 if self.mode == 'latest' else 0,
                'approve': 1
            }
            # print(f"{color['fail']}{data['link_post']}{color['endc']}")
            yield response.follow(data['link_post'], callback=self.parse_content)
            yield data

    def parse_content(self, response):
        def extraction_with_css(query):
            return response.css(query).get(default='').strip()

        data = {
            'raw_content': extraction_with_css('div.post'),
            'link_content': extraction_with_css('div.crawler-post-meta span + link::attr(href)'),
            'post_time': extraction_with_css('time.post-time::text'),
            'source': 'cardano',
            'latest': 1 if self.mode == 'latest' else 0,
        }
        yield data
        sleep(2)
