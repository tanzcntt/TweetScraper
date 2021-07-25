import json
from w3lib.html import remove_tags
from time import sleep
from .. import utils
from scrapy import Spider
from scrapy.http import Request, FormRequest, HtmlResponse
from .. import config as cfg


class CointeleNewsSpider(Spider):
    name = 'cointele'

    def __init__(self, mode):
        super(CointeleNewsSpider, self).__init__()
        self.mode = mode

    def start_requests(self):
        start_url = cfg.COINTELEGRAPH_API_DATA
        latest_page = cfg.LATEST_PAGE
        all_page = cfg.COINTELEGRAPH_TOTAL_PAGE
        offset = 0
        length = 15
        if self.mode == 'latest':
            utils.show_message('Crawling:', 'okgreen', self.mode.upper())
            for source in cfg.COINTELEGRAPH_SOURCES:
                utils.show_message('source: ', 'fail', source)
                for i in range(latest_page):
                    body_ = '{"operationName": "TagPagePostsQuery","variables": {' + \
                            '"slug": "{}",'.format(source) + \
                            '"order": "postPublishedTime",' + \
                            '"offset": {},'.format(offset) + \
                            '"length": {},'.format(length) + \
                            '"short": "en","cacheTimeInMS": 300000},"query": ' \
                            '"query TagPagePostsQuery($short: String, $slug: String\u0021, $order: String, $offset: Int\u0021, $length: Int\u0021) ' \
                            '{\\n  locale(short: $short) {\\n    tag(slug: $slug) {\\n      cacheKey\\n      id\\n      ' \
                            'posts(order: $order, offset: $offset, length: $length) {\\n        data {\\n          cacheKey\\n          id\\n          slug\\n          views\\n          postTranslate {\\n            cacheKey\\n            id\\n            title\\n            avatar\\n            published\\n            publishedHumanFormat\\n            leadText\\n            __typename\\n          }\\n          category {\\n            cacheKey\\n            id\\n            __typename\\n          }\\n          author {\\n            cacheKey\\n            id\\n            slug\\n            authorTranslates {\\n              cacheKey\\n              id\\n              name\\n              __typename\\n            }\\n            __typename\\n          }\\n          postBadge {\\n            cacheKey\\n            id\\n            label\\n            postBadgeTranslates {\\n              cacheKey\\n              id\\n              title\\n              __typename\\n            }\\n            __typename\\n          }\\n          showShares\\n          showStats\\n          __typename\\n        }\\n        postsCount\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n"}'
                    yield FormRequest(url=start_url, callback=self.parse,
                                      dont_filter=True, method="POST",
                                      body=body_, headers=cfg.COINTELEGRAPH_HEADERS)
                    offset += 15
                    if offset > (latest_page-1)*15:
                        offset = 0  # reset offset for new source
        elif self.mode == 'all':
            utils.show_message('Crawling:', 'okgreen', self.mode.upper())
            for source in cfg.COINTELEGRAPH_SOURCES:
                utils.show_message('source: ', 'fail', source)
                for i in range(all_page):
                    body_ = '{"operationName": "TagPagePostsQuery","variables": {' + \
                            '"slug": "{}",'.format(source) + \
                            '"order": "postPublishedTime",' + \
                            '"offset": {},'.format(offset) + \
                            '"length": {},'.format(length) + \
                            '"short": "en","cacheTimeInMS": 300000},"query": ' \
                            '"query TagPagePostsQuery($short: String, $slug: String\u0021, $order: String, $offset: Int\u0021, $length: Int\u0021) ' \
                            '{\\n  locale(short: $short) {\\n    tag(slug: $slug) {\\n      cacheKey\\n      id\\n      ' \
                            'posts(order: $order, offset: $offset, length: $length) {\\n        data {\\n          cacheKey\\n          id\\n          slug\\n          views\\n          postTranslate {\\n            cacheKey\\n            id\\n            title\\n            avatar\\n            published\\n            publishedHumanFormat\\n            leadText\\n            __typename\\n          }\\n          category {\\n            cacheKey\\n            id\\n            __typename\\n          }\\n          author {\\n            cacheKey\\n            id\\n            slug\\n            authorTranslates {\\n              cacheKey\\n              id\\n              name\\n              __typename\\n            }\\n            __typename\\n          }\\n          postBadge {\\n            cacheKey\\n            id\\n            label\\n            postBadgeTranslates {\\n              cacheKey\\n              id\\n              title\\n              __typename\\n            }\\n            __typename\\n          }\\n          showShares\\n          showStats\\n          __typename\\n        }\\n        postsCount\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n"}'
                    yield FormRequest(url=start_url, callback=self.parse,
                                  dont_filter=True, method="POST",
                                  body=body_, headers=cfg.COINTELEGRAPH_HEADERS)
                    offset += 15
                    if offset > (all_page-1)*15:
                        offset = 0  # reset offset for new source
            else:
                utils.show_message('', 'fail', 'Please retype mode: `latest` or `all`')
                exit()

    def parse(self, response, **kwargs):
        data = json.loads(response.body)
        utils.show_message('', 'fail', f'{self.mode.upper()} CoinTelegraph Thread')
        # get link content
        data_ = data['data']['locale']['tag']['posts']['data']
        tag = data['data']['locale']['tag']['id']
        for post in data_:
            post_badge_title = post['postBadge']['postBadgeTranslates'][0]['title'].lower()
            if post_badge_title == 'experts answer' or post_badge_title == 'explained':
                pass
            link_content = cfg.COINTELEGRAPH_URL.format('news/' + str(post['slug']))
            yield response.follow(url=link_content, callback=self.parse_content, headers=cfg.COINTELEGRAPH_HEADERS)
        item = {
            'title': '',
            'data': data_,
            'tag': tag,
            'source': 'coinTelegraph',
        }
        yield item
        sleep(3)

    def parse_content(self, response):
        item = {
            'raw_content': utils.decode_html_content(utils.extraction_with_css(response, 'div[class="post__content-wrapper"]')),
            'link_content': response.url,
            "source": "coinTelegraph",
        }
        yield item
        sleep(2)
