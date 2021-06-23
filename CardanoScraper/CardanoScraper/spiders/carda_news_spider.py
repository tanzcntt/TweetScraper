import pymongo
import scrapy
import time
import json
import chompjs
from time import sleep
from .. import utils
from scrapy import Request, Spider
from scrapy.selector import Selector
from scrapy.http import HtmlResponse, Request, FormRequest

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


class CoindeskLatest(Spider):
	name = "latestCoindesk"

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
				'slug': link_content.split('/')[-1],
				'author': '' if len(author) == 0 else author[1].lower(),
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
		recent_posts = response.css(
			'section.page-area-dotted-content div.story-stack section.list-body div.list-item-wrapper')
		for post in recent_posts:
			link_content = post.css('div.text-content a::attr(href)').getall()[-1]
			data = {
				'title': post.css('a h4.heading::text').get(),
				'subtitle': post.css('a p.card-text::text').get(),
				'link_content': link_content,
				'slug': link_content.split('/')[-1],
				'author': post.css('div.card-desc-block span.credit a::text').get().lower(),
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

	def parse_content(self, response, **kwargs):
		print(f"{color['warning']}Crawling detail page{color['endc']}")
		data_json = response.css('head')
		for content in data_json:
			data = {
				'raw_data': json.loads(content.css('script[type="application/ld+json"]::text').extract_first()),
				'source': 'coindesk',
			}
			yield data
		# ================================================
		# crawl full json data of specific post
		# ================================================
		# data_json = response.css('body')
		# for content in data_json:
		# 	data = {
		# 		'raw_data': json.loads(content.css('script[type="application/json"]::text').extract_first()),
		# 		'source': 'coindesk',
		# 	}
		# 	yield data
			sleep(1)


class CoindeskAll(Spider):
	name = "allCoindesk"

	def __init__(self):
		self.url = 'https://www.coindesk.com{}'
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
		url = 'https://www.coindesk.com/wp-json/v1/articles/format/news/{}?mode=list'
		total_page = 1
		for i in range(total_page):
			yield Request(url=url.format(i), callback=self.parse, headers=self.headers)

	def parse(self, response, **kwargs):
		data = json.loads(response.body)
		data['source'] = 'coindeskLatestNews'
		# print(data['posts'])
			# post_ = post['posts']
		for post in data['posts']:
			# print(f"{color['okcyan']}{post}{color['endc']}")
			link_content = self.url.format('/' + str(post['slug']))
			print(f"{color['okgreen']}{link_content}{color['endc']}")
			yield response.follow(url=link_content, callback=self.parse_content, headers=self.headers)
		yield data
		time.sleep(5)

	def parse_content(self, response, **kwargs):
		print(f"{color['warning']}Crawling detail page{color['endc']}")
		# <article id="article-68039" class="post__article" data-v-128018ef>
		data_json = response.css('body')
		for content in data_json:
			data = {
				'raw_data': json.loads(content.css('script[type="application/json"]::text').extract_first()),
				'source': 'coindesk',
			}
			print(f"Raw_content{color['okgreen']}{data}{color['endc']}")
			yield data
		# for article in articles:
		# 	data = {
		# 		'raw_content': article.css('div.post__content-wrapper::text').getall(),
		# 		'source': 'coindeskLatestNews',
		# 	}
		# 	print(f"Raw_content{color['okgreen']}{data}{color['endc']}")
		# 	yield data

class CoinTelegraphAll(Spider):
	name = 'allCoinTele'

	def start_requests(self, total_page=3):
		start_url = 'https://conpletus.cointelegraph.com/v1/'
		headers = {
			'authority': 'conpletus.cointelegraph.com',
			'method': 'POST',
			"sec-ch-ua": "\"Google Chrome\";v=\"89\", \"Chromium\";v=\"89\", \";Not A Brand\";v=\"99\"",
			'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36',
			'content-type': 'application/json',
			'origin': 'https://cointelegraph.com',
			'referer': 'https://cointelegraph.com/',
			'accept-language': 'en-US,en;q=0.9',
		}
		offset = 0
		length = 15
		# body='{"operationName": "TagPagePostsQuery","variables": {"slug": "bitcoin","order": "postPublishedTime","offset": 0,"length": 15,"short": "en","cacheTimeInMS": 300000},"query": "query TagPagePostsQuery($short: String, $slug: String\u0021, $order: String, $offset: Int\u0021, $length: Int\u0021) {\\n  locale(short: $short) {\\n    tag(slug: $slug) {\\n      cacheKey\\n      id\\n      posts(order: $order, offset: $offset, length: $length) {\\n        data {\\n          cacheKey\\n          id\\n          slug\\n          views\\n          postTranslate {\\n            cacheKey\\n            id\\n            title\\n            avatar\\n            published\\n            publishedHumanFormat\\n            leadText\\n            __typename\\n          }\\n          category {\\n            cacheKey\\n            id\\n            __typename\\n          }\\n          author {\\n            cacheKey\\n            id\\n            slug\\n            authorTranslates {\\n              cacheKey\\n              id\\n              name\\n              __typename\\n            }\\n            __typename\\n          }\\n          postBadge {\\n            cacheKey\\n            id\\n            label\\n            postBadgeTranslates {\\n              cacheKey\\n              id\\n              title\\n              __typename\\n            }\\n            __typename\\n          }\\n          showShares\\n          showStats\\n          __typename\\n        }\\n        postsCount\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n"}',
		for i in range(total_page):
			body_ = '{"operationName": "TagPagePostsQuery","variables": {"slug": "bitcoin","order": "postPublishedTime",' + \
					'"offset": {},'.format(offset) + \
					'"length": {},'.format(length) + \
					'"short": "en","cacheTimeInMS": 300000},"query": ' \
					'"query TagPagePostsQuery($short: String, $slug: String\u0021, $order: String, $offset: Int\u0021, $length: Int\u0021) {\\n  locale(short: $short) {\\n    tag(slug: $slug) {\\n      cacheKey\\n      id\\n      posts(order: $order, offset: $offset, length: $length) {\\n        data {\\n          cacheKey\\n          id\\n          slug\\n          views\\n          postTranslate {\\n            cacheKey\\n            id\\n            title\\n            avatar\\n            published\\n            publishedHumanFormat\\n            leadText\\n            __typename\\n          }\\n          category {\\n            cacheKey\\n            id\\n            __typename\\n          }\\n          author {\\n            cacheKey\\n            id\\n            slug\\n            authorTranslates {\\n              cacheKey\\n              id\\n              name\\n              __typename\\n            }\\n            __typename\\n          }\\n          postBadge {\\n            cacheKey\\n            id\\n            label\\n            postBadgeTranslates {\\n              cacheKey\\n              id\\n              title\\n              __typename\\n            }\\n            __typename\\n          }\\n          showShares\\n          showStats\\n          __typename\\n        }\\n        postsCount\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n"}'
			yield FormRequest(url=start_url, callback=self.parse, dont_filter=True, method="POST", body=body_, headers=headers)
			offset += 15

	def payload_data(self, offset=0, length=15):
		payload = [{
			"operationName": "TagPagePostsQuery",
			"variables": {
				"slug": "bitcoin",
				"order": "postPublishedTime",
				"offset": str(offset),
				"length": str(length),
				"short": "en",
				"cacheTimeInMS": 300000
			},
			"query": "query TagPagePostsQuery($short: String, $slug: String\u0021, $order: String, $offset: Int\u0021, $length: Int\u0021) {\\n  locale(short: $short) {\\n    tag(slug: $slug) {\\n      cacheKey\\n      id\\n      posts(order: $order, offset: $offset, length: $length) {\\n        data {\\n          cacheKey\\n          id\\n          slug\\n          views\\n          postTranslate {\\n            cacheKey\\n            id\\n            title\\n            avatar\\n            published\\n            publishedHumanFormat\\n            leadText\\n            __typename\\n          }\\n          category {\\n            cacheKey\\n            id\\n            __typename\\n          }\\n          author {\\n            cacheKey\\n            id\\n            slug\\n            authorTranslates {\\n              cacheKey\\n              id\\n              name\\n              __typename\\n            }\\n            __typename\\n          }\\n          postBadge {\\n            cacheKey\\n            id\\n            label\\n            postBadgeTranslates {\\n              cacheKey\\n              id\\n              title\\n              __typename\\n            }\\n            __typename\\n          }\\n          showShares\\n          showStats\\n          __typename\\n        }\\n        postsCount\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n"
		}]
		return str(payload[0])

	def parse(self, response, **kwargs):
		data = json.loads(response.body)
		item = {
			'raw_data': data,
			'source': 'coinTelegraph',
		}
		yield item
		sleep(3)
