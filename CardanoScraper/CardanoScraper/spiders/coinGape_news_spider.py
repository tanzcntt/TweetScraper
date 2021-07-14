import json
from time import sleep
from .. import utils
from scrapy import Spider
from scrapy.http import Request, FormRequest, HtmlResponse
from .. import config as cfg


class Coingape(Spider):
    name = 'coinGape'

    def __int__(self, mode, **kwargs):
        super.__init__(**kwargs)
        self.mode = mode

    def start_requests(self):
        start_url = cfg.COINPAGE_URL

        if self.mode == 'latest':
            utils.show_message('Crawling:', 'okgreen', self.mode.upper())
            for i in range(cfg.LATEST_PAGE+1):
                yield Request(url=start_url.format(i), callback=self.parse, headers=cfg.IOHK_HEADERS)
        elif self.mode == 'all':
            utils.show_message('Crawling', 'okgreen', self.mode.upper())
            for i in range(cfg.COINPAGE_TOTAL_PAGE):
                yield Request(url=start_url.format(i), callback=self.parse)
        else:
            utils.show_message('', 'fail', 'Please retype mode: `latest` or `all`')
            exit()

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
                'source': 'coingape.com',
                'latest': 1 if self.mode == 'latest' else 0,
                'approve': 1,
                'data_from': 'script',
            }
            yield item
        html_data = response.css('article')
        utils.show_message('', 'okgreen', response.url)
        for post in html_data:
            item1 = {
                'title': utils.decode_html_content(extraction_with_css(post, 'h3[class="entry-title mh-posts-list-title"] a::text')),
                'subtitle': utils.decode_html_content(extraction_with_css(post, 'div div.mh-excerpt p::text')),
                'link_content': extraction_with_css(post, 'h3 a::attr(href)'),
                # 'link_img': extraction_with_css(post, 'figure a img::attr(data-lazy-src)'),
                'link_img': extraction_with_css(post, 'noscript img::attr(src)'),
                'tag': extraction_with_css(post, 'div[class="mh-image-caption mh-posts-list-caption"]::text').split(' ')[0].lower(),
                'source': 'coingape.com',
                'data_from': 'article',
            }
            yield response.follow(url=item1['link_content'], callback=self.parse_content, headers=cfg.IOHK_HEADERS)
            yield item1
        sleep(.75)

    def parse_content(self, response):
        def extraction_with_css(post, query):
            return post.css(query).get(default='').strip()
        json_data = response.css('head')
        json_data = json.loads(json_data.css('script[type="application/ld+json"]::text').extract_first())
        clean_content = json_data[1]['articleBody']

        # dirty raw content but type is Selector
        raw_ = response.css('div[class="main c-content"]')

        # dirty raw content, type is String
        raw_data = extraction_with_css(response, 'div[class="main c-content"]')
        ads = extraction_with_css(raw_, 'div.ads')
        ads_m = extraction_with_css(raw_, 'div.ads-m')
        quads_location1 = extraction_with_css(raw_, 'div[id="quads-ad86062"]')
        quads_location2 = extraction_with_css(raw_, 'div[id="quads-ad86313"]')
        social_section = extraction_with_css(raw_, 'div[id="social-section-new"]')
        mh_social_bottom = extraction_with_css(raw_, 'div[class="mh-social-bottom"]')
        disclam = extraction_with_css(raw_, 'div[class="disclam"]')
        authorclam = extraction_with_css(raw_, 'div[class="authorclam"]')
        newNewsletter = extraction_with_css(raw_, 'div[class="newNewsletter"]')
        mobile_handpic = extraction_with_css(raw_, 'div[class="mobile-handpic"]')
        tranding_handlight = extraction_with_css(raw_, 'div[class="tranding-handlight dektophandpic"]')

        item = {
            'dirty_raw_content': raw_data,
            'link_content': response.url,
            'clean_content': utils.decode_html_content(clean_content),
            'remove_tag': [ads, ads_m, quads_location1, quads_location2, social_section, mh_social_bottom, disclam, authorclam, newNewsletter, mobile_handpic, tranding_handlight],
            'source': 'coingape.com',
        }
        # remove the unwanted tag to get only raw content
        for value in item['remove_tag']:
            raw_data = raw_data.replace(value, '')
        item['raw_content'] = utils.decode_html_content(raw_data)
        yield item
