import json
from time import sleep
from .. import utils
from scrapy import Spider
from scrapy.http import Request, FormRequest, HtmlResponse
from .. import config as cfg


class IohkNewsSpider(Spider):
    name = 'iohk'

    def __init__(self, mode):
        super(IohkNewsSpider, self).__init__()
        self.mode = mode

    def start_requests(self):
        total_page = 0
        start_url = cfg.IOHK_API_DATA
        if self.mode == 'all':
            utils.show_message('Crawling:', 'okgreen', self.mode.upper())
            while True:
                yield Request(url=start_url.format(total_page), callback=self.parse, headers=cfg.IOHK_HEADERS)
                total_page += 1
                if total_page > cfg.IOHK_TOTAL_PAGE:
                    break
        elif self.mode == 'latest':
            utils.show_message('Crawling:', 'okgreen', self.mode.upper())
            for i in range(cfg.LATEST_PAGE+1):
                yield Request(url=cfg.IOHK_API_DATA.format(i), callback=self.parse, headers=cfg.IOHK_HEADERS)
        else:
            utils.show_message('', 'fail', 'Please retype mode: `latest` or `all`')
            exit()

    def parse(self, response, **kwargs):
        utils.show_message('', 'fail', f"{self.mode.upper()} IOHK Thread")
        content = json.loads(response.body)
        content['source'] = 'iohk'
        yield content
        sleep(2)
