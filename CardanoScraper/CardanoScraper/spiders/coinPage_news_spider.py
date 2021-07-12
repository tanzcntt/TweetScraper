import json
from time import sleep
from .. import utils
from scrapy import Spider
from scrapy.http import Request, FormRequest, HtmlResponse
from .. import config as cfg


class Coinpage(Spider):
    name = 'coinPage'

    def __int__(self, mode, **kwargs):
        super.__init__(**kwargs)
        self.mode = mode

    def start_requests(self):
        start_url = cfg.COINPAGE_URL
        total_page = 0
        # yield Request(url=cfg.COINPAGE_URL.format(total_page), callback=self.parse, headers=cfg.IOHK_HEADERS)

        if self.mode == 'latest':
            utils.show_message('Crawling:', 'okgreen', self.mode)
            # while True:
            #     yield Request(url=cfg.COINPAGE_URL.format(total_page), callback=self.parse, headers=cfg.IOHK_HEADERS)
            #     utils.show_message('', 'warning', Request(url=cfg.IOHK_API_DATA.format(total_page), callback=self.parse, headers=cfg.IOHK_HEADERS))
            #     total_page += 1
            #     if total_page > cfg.LATEST_PAGE + 1:
            #         break
            # for i in range(cfg.LATEST_PAGE):
            for i in range(1):
                yield Request(url=start_url.format(i), callback=self.parse)
        elif self.mode == 'all':
            utils.show_message('', 'okcyan', 'crawling all pages')
            pass
        else:
            utils.show_message('', 'fail', 'Please retype mode: `latest` or `all`')

    def parse(self, response, **kwargs):
        def extraction_with_css(post, query):
            return post.css(query).get(default='').strip()

        utils.show_message('', 'fail', f'{self.mode.upper()} CoinPage Thread')
        json_data = response.css('head')
        json_data = json.loads(json_data.css('script[type="application/ld+json"]::text').extract_first())
        raw_data = json_data[0]['hasPart']
        for post in raw_data:
            item = {
                'title': utils.decode_html_content(post['headline']),  # decode text
                'link_content': post['url'],
                'author': post['author']['name'],
                'link_author': post['author']['url'],
                'link_author_img': post['author']['image']['url'],
                'datePublished': post['datePublished'],
                'dateModified': post['dateModified'],
                'source': 'coinpage.com',
                'latest': 1 if self.mode == 'latest' else 0,
                'approve': 1,
                'data_from': 'script',
            }
            yield item
            # item['title'] = utils.decode_html_content(post['headline'])  # decode text
            # item['link_content'] = post['url']
            # item['subtitle'] = ''
            # item['link_img'] = '',
            # item['slug_content'] = ''
            # item['author'] = post['author']['name']
            # item['link_author'] = post['author']['url']
            # item['link_author_img'] = post['author']['image']['url']
            # item['tag'] = ''
            # item['link_tag'] = ''
            # item['datePublished'] = post['datePublished']
            # item['dateModified'] = post['dateModified']
            # item['source'] = 'coinpage.com'
            # item['latest'] = 1 if self.mode == 'latest' else 0
            # item['approve'] = 1
            # utils.show_message('raw_data1', 'okgreen', item)
            # yield item

        html_data = response.css('article')
        utils.show_message('', 'okgreen', response.url)
        for post in html_data:
            item1 = {
                'title': utils.decode_html_content(extraction_with_css(post, 'h3[class="entry-title mh-posts-list-title"] a::text')),
                'subtitle': utils.decode_html_content(extraction_with_css(post, 'div div.mh-excerpt p::text')),
                'link_content': extraction_with_css(post, 'h3 a::attr(href)'),
                'link_img': extraction_with_css(post, 'a.mh-thumb-icon img::attr(src)'),
                'tag': extraction_with_css(post, 'div[class="mh-image-caption mh-posts-list-caption"]::text').split(' ')[0].lower(),
                'source': 'coinpage.com',
                'data_from': 'article',
            }
            # utils.show_message('data', 'okcyan', item1)
            yield item1
        sleep(.75)

    def parse_content(self, response):
        pass
