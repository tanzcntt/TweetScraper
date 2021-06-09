import pymongo
import scrapy
import time
from scrapy import Request
from .. import utils

color = utils.colors_mark()
mongoClient = pymongo.MongoClient("mongodb://root:password@localhost:27017/")
myDatabase = mongoClient["cardanoNews"]
englishNews = myDatabase['englishNews']
postContents = myDatabase['postContents']


class CardanoSpider(scrapy.Spider):
	name = "crawlLatestCarda"
	start_urls = [
		'https://forum.cardano.org/c/english/announcements/13?page=0'
	]

	def start_requests(self):
		url = 'https://forum.cardano.org/c/english/announcements/13?page='
		total_pages = 1
		for i in range(total_pages):
			yield Request(url=url + str(i), callback=self.parse)

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
				'latest': 1
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
			'latest': 1,
		}
		yield data
		time.sleep(4)


class CardaNewsContent(scrapy.Spider):
	name = "crawlAllCarda"
	start_urls = [
		'https://forum.cardano.org/c/english/announcements/13',
	]

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.mongoClient = pymongo.MongoClient("mongodb://root:password@localhost:27017/")
		self.myDatabase = self.mongoClient['cardanoNews']

	def parse(self, response, **kwargs):
		post_links = response.css('.link-top-line a')
		print(f'post_links {color["header"]} {post_links} {color["endc"]}')
		yield from response.follow_all(post_links, self.parse_content)

		pagination_links = response.css('span b a')
		print(f'pagination_links {color["header"]} {response.url} {color["endc"]}')
		yield from response.follow_all(pagination_links, self.parse)
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
				'latest': 0
			}
			yield data

	def parse_content(self, response, **kwargs):
		def extraction_with_css(query):
			return response.css(query).get(default='').strip()

		data = {
			'raw_content': extraction_with_css('div.post'),
			'link_content': extraction_with_css('div.crawler-post-meta span + link::attr(href)'),
			'post_time': extraction_with_css('time.post-time::text'),
			'latest': 0,
		}
		yield data
		time.sleep(5)


class IohkContent(scrapy.Spider):
	name = "crawlIohkNews"

	def start_requests(self):
		start_urls = [
			'https://iohk.io/page-data/en/blog/posts/page-1/page-data.json',
		]
		yield Request(url=start_urls[0], callback=self.parse)

	def parse(self, response):
		page = response.url
		utils.save_to_html("all", response.body)
