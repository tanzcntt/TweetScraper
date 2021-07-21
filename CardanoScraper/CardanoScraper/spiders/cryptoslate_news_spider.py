import json
from time import sleep
from .. import utils
from scrapy import Spider
from scrapy.http import Request, FormRequest, HtmlResponse
from .. import config as cfg


class CryptoslateNewsSpider(Spider):
    name = 'cryptoSlate'

    def __init__(self, mode):
        super(CryptoslateNewsSpider, self).__init__()
        self.mode = mode

    def start_requests(self):
        start_url = cfg.CRYPTOSLATE_CRYPTO_NEWS_URL
        if self.mode == 'latest':
            utils.show_message('Crawling:', 'okgreen', self.mode.upper())
            for i in range(cfg.LATEST_PAGE+1):
                yield Request(url=start_url.format(cfg.CRYPTOSLATE_CRYPTO_NEWS[0], i), callback=self.parse, headers=cfg.CRYPTOSLATE_HEADERS)
        elif self.mode == 'all':
            utils.show_message('Crawling:', 'okgreen', self.mode.upper())
            utils.show_message('', 'okgreen', 'crawling ALL')
            exit()
        else:
            utils.show_message('', 'fail', 'Please retype mode: `latest` or `all`')
            exit()

    def parse(self, response, **kwargs):
        utils.show_message('response.url: ', 'okcyan', response.url)
        data = response.css('article')
        for post in data:
            item = {
                'title': utils.decode_html_content(utils.extraction_with_css(post, 'article a::attr(title)')),
                # 'title2': utils.decode_html_content(utils.extraction_with_css(post, 'article[class="img-link"] a::attr(title)')),
                'link_content': utils.extraction_with_css(post, 'a[class="img-link"]::attr(href)'),
                'subtitle': utils.decode_html_content(utils.extraction_with_css(post, 'div[class="title"] p::text')),
                'link_img': utils.extraction_with_css(post, 'a div.cover img::attr(data-src)'),
                # 'link_img2': utils.extraction_with_css(post, 'a div.cover noscript img::attr(src)'),
                'slug_content': utils.extraction_with_css(post, 'a[class="img-link"]::attr(href)').split('.com')[1],
                'author': utils.extraction_with_css(post, 'div[class="title"] span strong::text'),
                'source': 'cryptoslate.com',
                'latest': 1 if self.mode == 'latest' else 0,
                'approve': 1,
            }
            utils.show_message('data: ', 'okcyan', item)
            yield response.follow(url=item['link_content'], callback=self.parse_content, headers=cfg.CRYPTOSLATE_HEADERS)
        sleep(.75)

    def parse_content(self, response, **kwargs):
        json_data = response.css('head')
        json_data = json.loads(json_data.css('script[type="application/ld+json"]::text').extract_first())
        json_data = json_data['@graph'][3]
        data = {
            'link_content': response.url,
            'datePublished': json_data['datePublished'] if 'datePublished' in json_data else '',
            'dateModified': json_data['dateModified'] if 'dateModified' in json_data else '',
        }
        # utils.show_message('data', 'okblue', data)
        # dirty raw content includes: edge-cta, posted-in,...
        raw_ = response.css('div[class="post-box clearfix"] article')
        raw_data = utils.extraction_with_css(response, 'div[class="post-box clearfix"] article')
        # utils.show_message('raw_data: ', 'warning', raw_data)
        link_page = utils.extraction_with_css(raw_, 'div.link-page')
        edge_cta = utils.extraction_with_css(raw_, 'div.edge-cta')
        tag = response.css('div.posted-in a::text').getall()
        posted_in = utils.extraction_with_css(raw_, 'div.posted-in')
        post_cta = utils.extraction_with_css(raw_, 'div.post-cta')
        related_articles = utils.extraction_with_css(raw_, 'div[class="related-articles clearfix"]')
        cpa_signup = utils.extraction_with_css(raw_, 'div[class="cpa-signup cryptocom placement ad-top clearfix"]')
        top = utils.extraction_with_css(raw_, 'div[class="top footer-disclaimer"]')
        footer_disclaimer = utils.extraction_with_css(raw_, 'div[class="footer-disclaimer"]')
        data2 = {
            'dirty_raw_content': raw_data,
            'tag': response.css('div.posted-in a::text').getall(),
            'remove_tag': [link_page, posted_in, edge_cta, post_cta, related_articles, cpa_signup, top, footer_disclaimer],
            'source': 'cryptoslate.com',
        }
        for value in data2['remove_tag']:
            raw_data = raw_data.replace(value, '')
        data['raw_content'] = utils.decode_html_content(raw_data)
        utils.show_message('parse_content: ', 'okgreen', data)
        sleep(.75)
