import scrapy
from datetime import datetime
from time import sleep
from .. import utils
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request

colors = utils.colors_mark()
current_datetime = datetime.now().timestamp()

class BlockchaininfluencersSpider(CrawlSpider):
	name = 'influencers'
	allowed_domains = ['www.upfolio.com/blockchain-influencers']
	start_urls = ['https://www.upfolio.com/blockchain-influencers/']

	def start_requests(self):
		url = 'https://www.upfolio.com/blockchain-influencers/'
		request_headers = {
			":authority": "assets1.lottiefiles.com",
			":method": "GET",
			":path": "/datafiles/VtCIGqDsiVwFPNM/data.json",
			":scheme": "https",
			"accept": "*/*",
			"accept-encoding": "gzip, deflate, br",
			"accept-language": "en-US,en;q=0.9",
			"origin": "https://lottiefiles.com",
			"referer": "https://lottiefiles.com/",
			'sec-ch-ua': "'Google Chrome';v='89', 'Chromium';v='89', ';Not A Brand';v='99'",
			"sec-ch-ua-mobile": "?0",
			"sec-fetch-dest": "empty",
			"sec-fetch-mode": "cors",
			"sec-fetch-site": "same-site",
			"user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36"
		}
		yield Request(url=url, callback=self.parse_item, headers=request_headers)

	def parse_item(self, response):
		items = response.css('div.influencerrow')
		for item in items:
			yield {
				'name': item.css('.influencerbox h2.influencername::text').get(),
				'position': item.css('.influencerbox h3.influencerh3::text').get(),
				'link_avatar': item.css('.influencerbox img::attr(src)').get(),
				'short_intro': item.css('.influencerbox p.influencertext::text').get(),
				'link_profile': item.css('.influencerbox a::attr(href)').get(),
				'source': 'upfolio.com',
			}


class AllCardanoNews(CrawlSpider):
	name = 'allCardanoNews'

	def start_requests(self):
		url = 'https://forum.cardano.org/c/english/announcements/13'
		yield Request(url=url, callback=self.parse)

	def parse(self, response, **kwargs):
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
				'latest': 0,
				'approve': 1
			}
			detail_page_link = post.css('td.main-link span.link-top-line a::attr(href)').get()
			yield response.follow(detail_page_link, callback=self.parse_content)
			yield data
		for next_page in response.css('span b a'):
			print(f"{colors['warning']}{next_page.get()}{colors['endc']}")
			yield Request(url=next_page, callback=self.parse)

	def parse_content(self, response):
		def extraction_with_css(query):
			return response.css(query).get(default='').strip()
		data = {
			'raw_content': extraction_with_css('div.post'),
			'link_content': extraction_with_css('div.crawler-post-meta span + link::attr(href)'),
			'post_time': extraction_with_css('time.post-time::text'),
			'source': 'cardano',
			'latest': 0,
		}
		yield data
		sleep(1)


class LatestCardanoNews(CrawlSpider):
	name = 'latestCardanoNews'

	def start_requests(self):
		url = 'https://forum.cardano.org/c/english/announcements/13?page={}'
		total_pages = 6
		for i in range(total_pages):
			yield Request(url=url.format(i), callback=self.parse)

	def parse(self, response, **kwargs):
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
				'date_crawled': current_datetime,
				'source': 'news.cardano',
				'latest': 1,
				'approve': 1
			}
			detail_page = post.css('td.main-link span.link-top-line a::attr(href)').get()
			yield response.follow(url=detail_page, callback=self.parse_content)
			yield data

	def parse_content(self, response):
		def extraction_with_css(query):
			return response.css(query).get(default='').strip()
		data = {
			'raw_content': extraction_with_css('div.post'),
			'link_content': extraction_with_css('div.crawler-post-meta span + link::attr(href)'),
			'post_time': extraction_with_css('time.post-time::text'),
			'source': 'news.cardano',
			'latest': 1,
		}
		yield data
		sleep(1)


class AllCardanoTrading(CrawlSpider):
	name = 'allCardanoTrading'

	def start_requests(self):
		url = 'https://forum.cardano.org/c/english/trading/12'

	def parse(self, response, **kwargs):
		pass


class LatestCardanoTrading(CrawlSpider):
	name = 'latestCardanoTrading'
	# scrapy crawl latestCardanoTrading
	# scrapy crawl latestCardanoNews

	def start_requests(self):
		url = 'https://forum.cardano.org/c/english/trading/12?page={}'
		total_pages = 6
		for i in range(total_pages):
			yield Request(url=url.format(i), callback=self.parse)
			sleep(1)

	def parse(self, response, **kwargs):
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
				'date_crawled': current_datetime,
				'source': 'trading.cardano',
				'latest': 1,
				'approve': 1
			}
			detail_page = post.css('td.main-link span.link-top-line a::attr(href)').get()
			yield response.follow(url=detail_page, callback=self.parse_content)
			yield data

	def parse_content(self, response):
		def extraction_with_css(query):
			return response.css(query).get(default='').strip()
		data = {
			'raw_content': extraction_with_css('div.post'),
			'link_content': extraction_with_css('div.crawler-post-meta span + link::attr(href)'),
			'post_time': extraction_with_css('time.post-time::text'),
			'source': 'trading.cardano',
			'latest': 1,
		}
		yield data
		sleep(1)


class AllIohk(CrawlSpider):
	name = 'allIohk'

	def start_requests(self):
		url = ''

	def parse(self, response, **kwargs):
		pass


class LatestIohk(CrawlSpider):
	name = 'latestIohk'

	def start_requests(self):
		url = ''

	def parse(self, response, **kwargs):
		pass
