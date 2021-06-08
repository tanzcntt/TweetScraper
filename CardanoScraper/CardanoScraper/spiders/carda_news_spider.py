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
	name = "cardaSpider"
	start_urls = [
		'https://forum.cardano.org/c/english/announcements/13?page=0'
	]

	def start_requests(self):
		url = 'https://forum.cardano.org/c/english/announcements/13?page='
		total_pages = 30
		for i in range(total_pages):
			yield Request(url=url + str(i), callback=self.parse)

	def parse(self, response, **kwargs):
		# page = response.url.split('page=')[1]
		# page = "all", save all page in 1 html file
		# utils.save_to_html(page, content=response.body)
		page = response.url
		# print(f'page: {page}')
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
			}
			data['avatars'] = self.handle_link_avatars(data['avatars'])
			if englishNews.find_one({'link_post': data['link_post']}):
				print("Updating__________________")
				self.update_english_news(data)
			else:
				self.insert_into_english_news(data)
				print("import success!!!__________________________________")
			yield data

	def insert_into_english_news(self, data):
		return englishNews.insert_one(data)

	def update_english_news(self, data):
		post_collection = englishNews
		query = {
			"link_post": data['link_post']
		}
		return post_collection.update_one(query, {'$set': data})

	def handle_link_avatars(self, links):
		new_links = []
		parent = "https://sjc3.discourse-cdn.com/business4"
		for link in links:
			if "https:" not in link:
				new_links.append(parent + link)
			else:
				pass
		return new_links


class CardaNewsContent(scrapy.Spider):
	func = CardanoSpider()
	name = "cardaContent"
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
		print(f'pagination_links {color["header"]} {pagination_links} {color["endc"]}')
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
			}
			data['avatars'] = self.handle_link_avatars(data['avatars'])
			if postContents.find_one({'link_post': data['link_post']}):
				print(color["okcyan"] + 'Updating: title, tags, posts link,...' + color["endc"])
				self.update_post_content(data)
			else:
				self.insert_into_post_content(data)
				print(color["okgreen"] + "Import success!!!" + color["endc"])
			yield data

	def parse_content(self, response, **kwargs):
		def extraction_with_css(query):
			return response.css(query).get(default='').strip()

		data = {
			'raw_content': extraction_with_css('div.post'),
			'link_content': extraction_with_css('div.crawler-post-meta span + link::attr(href)'),
			'post_time': extraction_with_css('time.post-time::text'),
		}
		query = {
			"link_post": data['link_content']
		}
		if postContents.update_one(query, {'$set': data}):
			print(f'{color["header"]} Updating Raw Contents...{color["endc"]}')
		yield data
		time.sleep(5)

	def insert_into_post_content(self, data):
		return postContents.insert_one(data)

	def update_post_content(self, data):
		query = {
			"link_post": data['link_post']
		}
		return postContents.update_one(query, {'$set': data})

	def handle_link_avatars(self, links):
		new_links = []
		parent = "https://sjc3.discourse-cdn.com/business4"
		for link in links:
			if "https:" not in link:
				new_links.append(parent + link)
			else:
				pass
		return new_links
