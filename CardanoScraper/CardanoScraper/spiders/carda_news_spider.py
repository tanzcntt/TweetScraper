import pymongo
import scrapy
import time
import json
import chompjs
from time import sleep
from .. import utils
from scrapy import Request, Spider
from scrapy.selector import Selector
from scrapy.http import HtmlResponse, Request

color = utils.colors_mark()
mongoClient = pymongo.MongoClient("mongodb://root:password@localhost:27017/")
myDatabase = mongoClient["cardanoNews"]
englishNews = myDatabase['englishNews']
postContents = myDatabase['postContents']


class CardanoSpider(Spider):
	name = "latestCarda"
	start_urls = [
		'https://forum.cardano.org/c/english/announcements/13?page=0'
	]

	def start_requests(self):
		url = 'https://forum.cardano.org/c/english/announcements/13?page='
		total_pages = 1
		for i in range(total_pages):
			yield Request(url=url + str(i), callback=self.parse)
			time.sleep(1)

	def parse(self, response, **kwargs):
		# page = "all", save all page in 1 html file
		# utils.save_to_html(page, content=response.body)
		page = response.url
		# get data through HTML form
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
				'latest': 1,
				'approve': 1
			}
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
			'latest': 1,
		}
		yield data
		time.sleep(2)


class CardanoNewsContent(Spider):
	name = "allCarda"
	start_urls = [
		'https://forum.cardano.org/c/english/announcements/13?page=0'
	]

	def start_requests(self):
		url = 'https://forum.cardano.org/c/english/announcements/13'
		yield Request(url=url, callback=self.parse)

	def parse(self, response, **kwargs):
		# page = response.url
		# page = "all", save all page in 1 html file
		# utils.save_to_html(page, content=response.body)
		page = response.url
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
			print(f"{color['warning']}{next_page.get()}{color['endc']}")
			yield response.follow(next_page, callback=self.parse)
			time.sleep(1)

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
		time.sleep(1)


class IohkContent(Spider):
	name = "allIohk"

	def start_requests(self):
		# start_urls = [
		# 	'https://iohk.io/page-data/en/blog/posts/page-1/page-data.json',
		# ]
		url = "https://iohk.io/page-data/en/blog/posts/page-{}/page-data.json"
		total_page = 44
		headers = {
			"sec-ch-ua": "\"Google Chrome\";v=\"89\", \"Chromium\";v=\"89\", \";Not A Brand\";v=\"99\"",
			"sec-ch-ua-mobile": "?0",
			"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36",
		}
		for i in range(total_page):
			yield Request(url=url.format(i), callback=self.parse_item, headers=headers)

	def parse_item(self, response):
		# page = response.url
		# utils.save_to_html("all", response.body)
		content = json.loads(response.body)
		content['source'] = 'iohk'
		yield content
		time.sleep(6)


class IohkLatest(Spider):
	name = 'latestIohk'

	def start_requests(self):
		start_url = 'https://iohk.io/page-data/en/blog/posts/page-{}/page-data.json'
		total_page = 4
		headers = {
			"sec-ch-ua": "\"Google Chrome\";v=\"89\", \"Chromium\";v=\"89\", \";Not A Brand\";v=\"99\"",
			"sec-ch-ua-mobile": "?0",
			"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36",
		}
		for i in range(total_page):
			yield Request(url=start_url.format(i), callback=self.parse, headers=headers)

	def parse(self, response, **kwargs):
		content = json.loads(response.body)
		content['source'] = 'iohk'
		yield content
		time.sleep(6)


# class CardanoMedium(scrapy.Spider):
# 	name = 'mediumCarda'
#
# 	def start_requests(self):
# 		start_urls = ['']


class CoindeskAll(Spider):
	name = "allCoindesk"

	def __init__(self):
		self.headers = {
				"accept-encoding": "gzip, deflate, br",
				"accept-language": "en-US,en;q=0.9",
				"origin": "https://www.coindesk.com",
				"referer": "https://www.coindesk.com/",
				"sec-ch-ua": "\"Google Chrome\";v=\"89\", \"Chromium\";v=\"89\", \";Not A Brand\";v=\"99\"",
				"sec-ch-ua-mobile": "?0",
				"sec-fetch-dest": "empty",
				"sec-fetch-mode": "cors",
				"sec-fetch-site": "cross-site",
				"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36",
			}

	def start_requests(self):
		url = 'https://www.coindesk.com/'
		yield Request(url=url, callback=self.parse, headers=self.headers)

	def parse(self, response, **kwargs):
		# posts = response.css('div.top-right-bar section.article-card-fh')
		# ================================================
		# Data in top-section
		# ================================================
		coindesk_url = 'https://www.coindesk.com'
		top_section_posts = response.css('section.article-card-fh')
		for post in top_section_posts:
			author = post.css('div.card-desc span.card-author a::text').getall()
			link_content = post.css('div.card-text-block h2.heading a::attr(href)').get()
			data = {
				'tag': post.css('div.card-img-block a.button span.eyebrow-button-text::text').get(),
				'link_tag': post.css('div.card-img-block a.eyebrow-button::attr(href)').get(),
				'title': post.css('div.card-text-block h2.heading a::text').get(),
				'subtitle': post.css('div.text-group p.card-text::text').get(),
				'link_content': link_content,
				'author': '' if len(author) == 0 else author[1],
				'link_author': post.css('div.card-desc span.card-author a::attr(href)').get(),
				'date': post.css('span.card-date::text').get(),
				'source': 'coindesk',
				'latest': 0,
				'approve': 1,
			}
			yield response.follow(url=link_content, callback=self.parse_content, headers=self.headers)
			yield data
			sleep(.75)
		# ================================================
		# data on story-stack-chinese-wrapper
		# ================================================
		recent_posts = response.css('section.page-area-dotted-content div.story-stack section.list-body div.list-item-wrapper')
		for post in recent_posts:
			link_content = post.css('div.text-content a::attr(href)').getall()[-1]
			data = {
				'title': post.css('a h4.heading::text').get(),
				'subtitle': post.css('a p.card-text::text').get(),
				'link_content': link_content,
				'author': post.css('div.card-desc-block span.credit a::text').get(),
				'link_author': post.css('div.card-desc-block span.credit a::attr(href)').get(),
				'date': '',
				'tag': post.css('a.button span.eyebrow-button-text::text').get(),
				'link_tag': post.css('div.text-content a.button::attr(href)').get(),
				'source': 'coindesk',
				'latest': 0,
				'approve': 1,
			}
			yield response.follow(url=link_content, callback=self.parse_content)
			yield data
			sleep(0.75)

	def parse_content(self, response):
		print(f"{color['warning']}Crawling detail page{color['endc']}")
		data_json = response.css('head')
		for content in data_json:
			data = {
				'raw_data': json.loads(content.css('script[type="application/ld+json"]::text').extract_first()),
				'source': 'coindesk',
			}
			yield data
			sleep(.75)


# https://www.coindesk.com/video/crypto-derivatives-platform-dydx-raises-65m-in-paradigm-led-series-c
# https://coindesk.com/video/crypto-derivatives-platform-dydx-raises-65m-in-paradigm-led-series-c
# https://www.coindesk.com/video/mclaren-to-build-nft-platform-on-tezos
