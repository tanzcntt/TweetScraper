import json
from time import sleep
from .. import utils
from scrapy import Spider
from scrapy.http import Request, FormRequest, HtmlResponse
from .. import config as cfg


class CoindeskNewsSpiderSpider(Spider):
    name = 'coinDesk'

    def __init__(self, mode):
        super(CoindeskNewsSpiderSpider, self).__init__()
        self.mode = mode

    def start_requests(self):
        start_url = cfg.COINDESK_API_DATA
        if self.mode == 'latest':
            utils.show_message('Crawling:', 'okgreen', self.mode.upper())
            i = 1
            while True:
                yield Request(url=start_url.format(i), callback=self.parse, headers=cfg.COINDESK_HEADERS)
                utils.show_message('', 'warning', Request(url=start_url.format(i), callback=self.parse,
                                                          headers=cfg.COINDESK_HEADERS))
                i += 1
                if i > cfg.LATEST_PAGE+1:
                    break
        elif self.mode == 'all':
            utils.show_message('Crawling:', 'okgreen', self.mode.upper())
            i = 1
            while True:
                yield Request(url=start_url.format(i), callback=self.parse, headers=cfg.COINDESK_HEADERS)
                utils.show_message('', 'warning', Request(url=start_url.format(i), callback=self.parse,
                                                          headers=cfg.COINDESK_HEADERS))
                i += 1
                if i > cfg.COINDESK_TOTAL_PAGE:
                    break
        else:
            utils.show_message('', 'fail', 'Please retype mode: `latest` or `all`')
            exit()

    def parse(self, response, **kwargs):
        utils.show_message('', 'fail', f'{self.mode.upper()} Coindesk Thread')
        data = json.loads(response.body)
        for post in data['posts']:
            link_content = cfg.COINDESK_URL.format('/' + str(post['slug']))
            # utils.show_message('', 'okgreen', link_content)
            yield response.follow(url=link_content, callback=self.parse_content, headers=cfg.COINDESK_HEADERS)
        data['source'] = 'coindeskLatestNews'
        yield data
        sleep(1)

    def parse_content(self, response):
        data_json = response.css('body')
        for content in data_json:
            raw_data = json.loads(content.css('script[type="application/json"]::text').extract_first())
            data = raw_data['props']['pageProps']['data']
            item = {
                'slug_content': data['slug'],
                'raw_content': data['amp'],
                'link_content': response.url,
                'source': 'coindeskLatestNews',
                'raw_data': raw_data,
            }
            yield item
            sleep(.1)
