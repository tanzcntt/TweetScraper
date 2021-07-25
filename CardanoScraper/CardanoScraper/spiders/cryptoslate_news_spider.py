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
        start_crypto_news_url = cfg.CRYPTOSLATE_CRYPTO_NEWS_URL
        start_cate_news_url = cfg.CRYPTOSLATE_CATE_NEWS_URL
        if self.mode == 'latest':
            utils.show_message('Crawling:', 'okgreen', self.mode.upper())
            # get data in Crypto news category
            category_sources = cfg.CRYPTOSLATE_SOURCES
            for category in category_sources:
                for source in category_sources[category]:
                    utils.show_message('source: ', 'fail', source)
                    for i in range(1, cfg.LATEST_PAGE+1):
                        utils.show_message('Crawling one source: ', 'fail', source)
                        yield Request(url=start_crypto_news_url.format(source, i), callback=self.parse, headers=cfg.CRYPTOSLATE_HEADERS)
                        yield Request(url=start_cate_news_url.format(source, i), callback=self.parse, headers=cfg.CRYPTOSLATE_HEADERS)
                        utils.show_message('page: ', 'warning', Request(url=start_crypto_news_url.format(source, i), callback=self.parse, headers=cfg.CRYPTOSLATE_HEADERS))
        elif self.mode == 'all':
            utils.show_message('Crawling:', 'okgreen', self.mode.upper())
            # get data in Crypto news category
            category_sources = cfg.CRYPTOSLATE_SOURCES
            for category in category_sources:
                for source in category_sources[category]:
                    utils.show_message('source: ', 'fail', source)
                    for i in range(1, cfg.CRYPTOSLATE_TOTAL_PAGE):
                        utils.show_message('Crawling one source: ', 'fail', source)
                        yield Request(url=start_crypto_news_url.format(source, i), callback=self.parse, headers=cfg.CRYPTOSLATE_HEADERS)
                        yield Request(url=start_cate_news_url.format(source, i), callback=self.parse, headers=cfg.CRYPTOSLATE_HEADERS)
                        utils.show_message('page: ', 'warning', Request(url=start_crypto_news_url.format(source, i), callback=self.parse, headers=cfg.CRYPTOSLATE_HEADERS))
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
                'slug_category': response.url.split('.com/')[1],
                # 'subtitle': utils.decode_html_content(utils.extraction_with_css(post, 'a div.content div.title p::text')),
                'link_img': utils.extraction_with_css(post, 'a div.cover img::attr(data-src)'),
                # 'link_img2': utils.extraction_with_css(post, 'a div.cover noscript img::attr(src)'),
                # 'slug_content': utils.extraction_with_css(post, 'a[class="img-link"]::attr(href)').split('.com')[1],
                'author': utils.extraction_with_css(post, 'a div.content div.title span strong::text'),
                'source': 'cryptoslate.com',
                'latest': 1 if self.mode == 'latest' else 0,
                'approve': 1,
            }
            yield response.follow(url=item['link_content'], callback=self.parse_content, headers=cfg.CRYPTOSLATE_HEADERS)
            yield item
        sleep(1)

    def parse_content(self, response, **kwargs):
        json_data = response.css('head')
        json_data = json.loads(json_data.css('script[type="application/ld+json"]::text').extract_first())
        json_data = json_data['@graph'][3]
        data = {
            'link_content': response.url,
            'datePublished': json_data['datePublished'] if 'datePublished' in json_data else '',
            'dateModified': json_data['dateModified'] if 'dateModified' in json_data else '',
            'subtitle': utils.decode_html_content(json_data['description']) if 'description' in json_data else utils.decode_html_content(json_data['name']),
        }
        # dirty raw content includes: edge-cta, posted-in,...
        raw_ = response.css('div[class="post-box clearfix"] article')
        raw_data = utils.extraction_with_css(response, 'div[class="post-box clearfix"] article')
        link_page = utils.extraction_with_css(raw_, 'div.link-page')
        edge_cta = utils.extraction_with_css(raw_, 'div.edge-cta')
        posted_in = utils.extraction_with_css(raw_, 'div.posted-in')
        post_cta = utils.extraction_with_css(raw_, 'div.post-cta')
        related_articles = utils.extraction_with_css(raw_, 'div[class="related-articles clearfix"]')
        cpa_signup = utils.extraction_with_css(raw_, 'div[class="cpa-signup cryptocom placement ad-top clearfix"]')
        top = utils.extraction_with_css(raw_, 'div[class="top footer-disclaimer"]')
        footer_disclaimer = utils.extraction_with_css(raw_, 'div[class="footer-disclaimer"]')
        data2 = {
            'dirty_raw_content': raw_data,
            'keywords': response.css('div.posted-in a::text').getall(),
            'remove_tag': [link_page, posted_in, edge_cta, post_cta, related_articles, cpa_signup, top, footer_disclaimer],
            'source': 'cryptoslate.com',
        }
        for value in data2['remove_tag']:
            raw_data = raw_data.replace(value, '')
        data['raw_content'] = utils.decode_html_content(raw_data)
        data2.pop('remove_tag')
        data2.update(data)
        utils.show_message('description: ', 'fail', {response.url: data2['subtitle']})
        yield data2
        sleep(1)

# https://www.cnbc.com/search/?query=cardano&qsearchterm=cardano
# scrapy shell 'https://www.cnbc.com/search/?query=cardano&qsearchterm=cardano' --nolog
