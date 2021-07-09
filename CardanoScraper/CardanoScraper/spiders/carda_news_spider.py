import pymongo
import time
import json
from time import sleep
from .. import utils
from .. import config as cfg
from scrapy import Spider
from scrapy.http import Request, FormRequest, HtmlResponse
from scrapy.selector import Selector

color = utils.colors_mark()
mongoClient = pymongo.MongoClient("mongodb://root:password@localhost:27017/")
myDatabase = mongoClient["cardanoNews"]


# ================================================================================================
# forum.cardano.org
# ================================================================================================
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
		print(f"{color['fail']}Latest Cardano Thread{color['endc']}")
		# page = "all", save all page in 1 html file
		# utils.save_to_html(page, content=response.body)
		page = response.url
		# get data through HTML form
		utils.show_message('Type response', 'fail', type(response))
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
			# print(f"{color['fail']}{data['link_post']}{color['endc']}")
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
		print(f"{color['fail']}All Cardano Thread{color['endc']}")
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


# ================================================================================================
# iohk.io/en/blog/posts/page-1
# ================================================================================================
class IohkContent(Spider):
	name = "allIohk"

	def start_requests(self):
		url = "https://iohk.io/page-data/en/blog/posts/page-{}/page-data.json"
		total_page = 0
		while True:
			yield Request(url=url.format(total_page), callback=self.parse, headers=cfg.IOHK_HEADERS)
			print(
				f"{color['warning']}{Request(url=url.format(total_page), callback=self.parse, headers=cfg.IOHK_HEADERS)}{color['endc']}")
			total_page += 1
			if total_page > 45:
				break

	def parse_item(self, response):
		# page = response.url
		content = json.loads(response.body)
		content['source'] = 'iohk'
		yield content
		time.sleep(2)


class IohkLatest(Spider):
	name = 'latestIohk'

	def start_requests(self):
		start_url = 'https://iohk.io/page-data/en/blog/posts/page-{}/page-data.json'
		total_page = 4
		for i in range(total_page):
			yield Request(url=start_url.format(i), callback=self.parse, headers=cfg.IOHK_HEADERS)

	def parse(self, response, **kwargs):
		print(f"{color['fail']}Latest IOHK Thread{color['endc']}")
		content = json.loads(response.body)
		content['source'] = 'iohk'
		yield content
		time.sleep(2)


# ================================================================================================
# Coindesk.com
# ================================================================================================
# coindesk.com
class CoindeskLatest(Spider):
	name = "latestCoindesk"

	def start_requests(self):
		url = 'https://www.coindesk.com/'
		yield Request(url=url, callback=self.parse, headers=cfg.COINDESK_HEADERS)

	def parse(self, response, **kwargs):
		# posts = response.css('div.top-right-bar section.article-card-fh')
		# ================================================
		# Data in top-section
		# ================================================
		coindesk_url = 'https://www.coindesk.com'
		print(f"{color['fail']}Latest Coindesk Thread{color['endc']}")
		top_section_posts = response.css('section.article-card-fh')
		for post in top_section_posts:
			author = post.css('div.card-desc span.card-author a::text').getall()
			print(f"Author1: {color['okcyan']}{author}{color['endc']}")
			link_content = post.css('div.card-text-block h2.heading a::attr(href)').get()
			data = {
				'tag': post.css('div.card-img-block a.button span.eyebrow-button-text::text').get(),
				'link_tag': post.css('div.card-img-block a.eyebrow-button::attr(href)').get(),
				'title': post.css('div.card-text-block h2.heading a::text').get(),
				'subtitle': post.css('div.text-group p.card-text::text').get(),
				'link_content': link_content,
				'slug_content': link_content.split('/')[-1],
				'author': '' if len(author) == 0 else author[1].lower(),
				'link_author': post.css('div.card-desc span.card-author a::attr(href)').get(),
				'date': post.css('span.card-date::text').get(),
				'source': 'coindesk',
				'latest': 1,
				'approve': 1,
			}
			yield response.follow(url=link_content, callback=self.parse_content, headers=cfg.COINDESK_HEADERS)
			yield data
			sleep(.75)
		# ================================================
		# data on story-stack-chinese-wrapper
		# ================================================
		recent_posts = response.css(
			'section.page-area-dotted-content div.story-stack section.list-body div.list-item-wrapper')
		for post in recent_posts:
			author = post.css('div.card-desc-block span.credit a::text').getall()
			print(f"Author2: {color['okcyan']}{author}{color['endc']}")
			link_content = post.css('div.text-content a::attr(href)').getall()[-1]
			data = {
				'title': post.css('a h4.heading::text').get(),
				'subtitle': post.css('a p.card-text::text').get(),
				'link_content': link_content,
				'slug_content': link_content.split('/')[-1],
				'author': '' if len(author) == 0 else author[0].lower(),
				'link_author': post.css('div.card-desc-block span.credit a::attr(href)').get(),
				'date': '',
				'tag': post.css('a.button span.eyebrow-button-text::text').get(),
				'link_tag': post.css('div.text-content a.button::attr(href)').get(),
				'source': 'coindesk',
				'latest': 1,
				'approve': 1,
			}
			yield response.follow(url=link_content, callback=self.parse_content, headers=cfg.COINDESK_HEADERS)
			yield data
			sleep(0.75)

	def parse_content(self, response, **kwargs):
		page = response.url
		print(f"{color['warning']}Crawling detail page {page}{color['endc']}")
		data_json = response.css('body')
		for content in data_json:
			raw_data = json.loads(content.css('script[type="application/json"]::text').extract_first())
			# raw_data = json.loads(content.css('script[type="application/ld+json"]::text').extract_first())
			if 'podcasts' in page:
				pass
			elif 'tv' in page:
				pass
			else:
				data = raw_data['props']['initialProps']['pageProps']['data']
				img = data['media']['images']
				item = {
					'slug_content': data['slug'],
					'raw_content': data['amp'],
					'date': data['published'],
					'link_img': img['desktop']['src'] if 'desktop' in img else img['mobile']['src'],
					'source': 'coindesk',
					'raw_data': raw_data,
				}
				yield item
				sleep(1)


# ================================================
# coindesk.com/news
# ================================================
class CoindeskAll(Spider):
	name = "allCoindesk"

	def __init__(self):
		self.url = 'https://www.coindesk.com{}'

	def start_requests(self):
		url = 'https://www.coindesk.com/wp-json/v1/articles/format/news/{}?mode=list'
		total_page = cfg.COINDESK_TOTAL_PAGE  # max page = 99 <23/06/21>
		while True:
			yield Request(url=url.format(total_page), callback=self.parse, headers=cfg.COINDESK_HEADERS)
			total_page += 1
			if total_page > 100:
				break
	# for i in range(total_page):
	# 	yield Request(url=url.format(i), callback=self.parse, headers=self.headers)

	def parse(self, response, **kwargs):
		print(f"{color['fail']}All Coindesk Thread{color['endc']}")
		data = json.loads(response.body)
		data['source'] = 'coindeskLatestNews'
		# get link content
		for post in data['posts']:
			link_content = self.url.format('/' + str(post['slug']))
			print(f"{color['okgreen']}{link_content}{color['endc']}")
			yield response.follow(url=link_content, callback=self.parse_content, headers=cfg.COINDESK_HEADERS)
		yield data
		time.sleep(2)

	def parse_content(self, response, **kwargs):
		page = response.url
		print(f"{color['warning']}Crawling detail page {page}{color['endc']}")
		data_json = response.css('body')
		for content in data_json:
			raw_data = json.loads(content.css('script[type="application/json"]::text').extract_first())
			data = raw_data['props']['initialProps']['pageProps']['data']
			item = {
				'slug_content': data['slug'],
				'raw_content': data['amp'],
				'source': 'coindeskLatestNews',
				'raw_data': raw_data,
			}
			yield item
			sleep(.1)


# ================================================================================================
# cointelegraph.com
# ================================================================================================
# cointelegraph.com/tags/bitcoin
class CoinTeleBitcoinAll(Spider):
	name = 'allCointeleBitcoin'

	def start_requests(self):
		start_url = cfg.COINTELEGRAPH_API_DATA
		offset = 0
		length = 15
		# body='{"operationName": "TagPagePostsQuery","variables": {"slug": "bitcoin","order": "postPublishedTime","offset": 0,"length": 15,"short": "en","cacheTimeInMS": 300000},"query": "query TagPagePostsQuery($short: String, $slug: String\u0021, $order: String, $offset: Int\u0021, $length: Int\u0021) {\\n  locale(short: $short) {\\n    tag(slug: $slug) {\\n      cacheKey\\n      id\\n      posts(order: $order, offset: $offset, length: $length) {\\n        data {\\n          cacheKey\\n          id\\n          slug\\n          views\\n          postTranslate {\\n            cacheKey\\n            id\\n            title\\n            avatar\\n            published\\n            publishedHumanFormat\\n            leadText\\n            __typename\\n          }\\n          category {\\n            cacheKey\\n            id\\n            __typename\\n          }\\n          author {\\n            cacheKey\\n            id\\n            slug\\n            authorTranslates {\\n              cacheKey\\n              id\\n              name\\n              __typename\\n            }\\n            __typename\\n          }\\n          postBadge {\\n            cacheKey\\n            id\\n            label\\n            postBadgeTranslates {\\n              cacheKey\\n              id\\n              title\\n              __typename\\n            }\\n            __typename\\n          }\\n          showShares\\n          showStats\\n          __typename\\n        }\\n        postsCount\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n"}',
		for i in range(cfg.COINTELEGRAPH_TOTAL_PAGE):
			body_ = '{"operationName": "TagPagePostsQuery","variables": {"slug": "bitcoin","order": "postPublishedTime",' + \
					'"offset": {},'.format(offset) + \
					'"length": {},'.format(length) + \
					'"short": "en","cacheTimeInMS": 300000},"query": ' \
					'"query TagPagePostsQuery($short: String, $slug: String\u0021, $order: String, $offset: Int\u0021, $length: Int\u0021) {\\n  locale(short: $short) {\\n    tag(slug: $slug) {\\n      cacheKey\\n      id\\n      posts(order: $order, offset: $offset, length: $length) {\\n        data {\\n          cacheKey\\n          id\\n          slug\\n          views\\n          postTranslate {\\n            cacheKey\\n            id\\n            title\\n            avatar\\n            published\\n            publishedHumanFormat\\n            leadText\\n            __typename\\n          }\\n          category {\\n            cacheKey\\n            id\\n            __typename\\n          }\\n          author {\\n            cacheKey\\n            id\\n            slug\\n            authorTranslates {\\n              cacheKey\\n              id\\n              name\\n              __typename\\n            }\\n            __typename\\n          }\\n          postBadge {\\n            cacheKey\\n            id\\n            label\\n            postBadgeTranslates {\\n              cacheKey\\n              id\\n              title\\n              __typename\\n            }\\n            __typename\\n          }\\n          showShares\\n          showStats\\n          __typename\\n        }\\n        postsCount\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n"}'
			yield FormRequest(url=start_url, callback=self.parse,
							  dont_filter=True, method="POST",
							  body=body_, headers=cfg.COINTELEGRAPH_HEADERS)
			offset += 15

	def parse(self, response, **kwargs):
		print(f"{color['fail']}All Bitcoin CoinTelegraph Thread{color['endc']}")
		data = json.loads(response.body)
		# get link content
		data_ = data['data']['locale']['tag']['posts']['data']
		for post in data_:
			post_badge_title = post['postBadge']['postBadgeTranslates'][0]['title'].lower()
			if post_badge_title == 'experts answer' or post_badge_title == 'explained':
				# link_content = self.url.format('explained/' + str(post['slug']))
				pass
			# else:
			link_content = cfg.COINTELEGRAPH_URL.format(
				'news/' + str(post['slug']))  # https://cointelegraph.com/news/ + slug
			yield response.follow(url=link_content, callback=self.parse_content, headers=cfg.COINTELEGRAPH_HEADERS)
		item = {
			'title': '',
			'data': data_,
			'source': 'coinTelegraph',
		}
		yield item
		sleep(3)

	def parse_content(self, response):
		page = response.url
		print(f"{color['okgreen']}Crawling raw content in {page}{color['endc']}")
		data = response.css('body')
		for content in data:
			item = {
				"raw_data": content.css('script::text').get(),
				'link_content': page,
				'tag': 'bitcoin',
				"source": "coinTelegraph",
			}
			yield item
			sleep(2)


# ================================================
# cointelegraph.com/tags/ethereum
# ================================================
class CoinTeleEthereumAll(Spider):
	name = 'allCointeleEthereum'

	def start_requests(self):
		start_url = cfg.COINTELEGRAPH_API_DATA
		offset = 0
		length = 15
		# body='{"operationName": "TagPagePostsQuery","variables": {"slug": "bitcoin","order": "postPublishedTime","offset": 0,"length": 15,"short": "en","cacheTimeInMS": 300000},"query": "query TagPagePostsQuery($short: String, $slug: String\u0021, $order: String, $offset: Int\u0021, $length: Int\u0021) {\\n  locale(short: $short) {\\n    tag(slug: $slug) {\\n      cacheKey\\n      id\\n      posts(order: $order, offset: $offset, length: $length) {\\n        data {\\n          cacheKey\\n          id\\n          slug\\n          views\\n          postTranslate {\\n            cacheKey\\n            id\\n            title\\n            avatar\\n            published\\n            publishedHumanFormat\\n            leadText\\n            __typename\\n          }\\n          category {\\n            cacheKey\\n            id\\n            __typename\\n          }\\n          author {\\n            cacheKey\\n            id\\n            slug\\n            authorTranslates {\\n              cacheKey\\n              id\\n              name\\n              __typename\\n            }\\n            __typename\\n          }\\n          postBadge {\\n            cacheKey\\n            id\\n            label\\n            postBadgeTranslates {\\n              cacheKey\\n              id\\n              title\\n              __typename\\n            }\\n            __typename\\n          }\\n          showShares\\n          showStats\\n          __typename\\n        }\\n        postsCount\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n"}',
		for i in range(cfg.COINTELEGRAPH_TOTAL_PAGE):
			body_ = '{"operationName": "TagPagePostsQuery","variables": {"slug": "ethereum","order": "postPublishedTime",' + \
					'"offset": {},'.format(offset) + \
					'"length": {},'.format(length) + \
					'"short": "en","cacheTimeInMS": 300000},"query": ' \
					'"query TagPagePostsQuery($short: String, $slug: String\u0021, $order: String, $offset: Int\u0021, $length: Int\u0021) {\\n  locale(short: $short) {\\n    tag(slug: $slug) {\\n      cacheKey\\n      id\\n      posts(order: $order, offset: $offset, length: $length) {\\n        data {\\n          cacheKey\\n          id\\n          slug\\n          views\\n          postTranslate {\\n            cacheKey\\n            id\\n            title\\n            avatar\\n            published\\n            publishedHumanFormat\\n            leadText\\n            __typename\\n          }\\n          category {\\n            cacheKey\\n            id\\n            __typename\\n          }\\n          author {\\n            cacheKey\\n            id\\n            slug\\n            authorTranslates {\\n              cacheKey\\n              id\\n              name\\n              __typename\\n            }\\n            __typename\\n          }\\n          postBadge {\\n            cacheKey\\n            id\\n            label\\n            postBadgeTranslates {\\n              cacheKey\\n              id\\n              title\\n              __typename\\n            }\\n            __typename\\n          }\\n          showShares\\n          showStats\\n          __typename\\n        }\\n        postsCount\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n"}'
			yield FormRequest(url=start_url, callback=self.parse,
							  dont_filter=True, method="POST",
							  body=body_, headers=cfg.COINTELEGRAPH_HEADERS)
			offset += 15

	def parse(self, response, **kwargs):
		print(f"{color['fail']}All Ethereum CoinTelegraph Thread{color['endc']}")
		data = json.loads(response.body)
		# get link content
		data_ = data['data']['locale']['tag']['posts']['data']
		for post in data_:
			post_badge_title = post['postBadge']['postBadgeTranslates'][0]['title'].lower()
			if post_badge_title == 'experts answer' or post_badge_title == 'explained':
				pass
			# else:
			link_content = cfg.COINTELEGRAPH_URL.format(
				'news/' + str(post['slug']))  # https://cointelegraph.com/news/ + slug
			yield response.follow(url=link_content, callback=self.parse_content, headers=cfg.COINTELEGRAPH_HEADERS)
		item = {
			'title': '',
			'data': data_,
			'source': 'coinTelegraph',
		}
		yield item
		sleep(3)

	def parse_content(self, response):
		page = response.url
		print(f"{color['okgreen']}Crawling raw content in {page}{color['endc']}")
		data = response.css('body')
		for content in data:
			item = {
				"raw_data": content.css('script::text').get(),
				'link_content': page,
				'tag': 'ethereum',
				"source": "coinTelegraph",
			}
			yield item
			sleep(2)


# ================================================
# cointelegraph.com/tags/blockchain
# ================================================
class CoinTeleBlockchainAll(Spider):
	name = 'allCointeleBlockchain'

	def start_requests(self):
		start_url = cfg.COINTELEGRAPH_API_DATA
		offset = 0
		length = 15
		for i in range(cfg.COINTELEGRAPH_TOTAL_PAGE):
			body_ = '{"operationName": "TagPagePostsQuery","variables": {"slug": "blockchain","order": "postPublishedTime",' + \
					'"offset": {},'.format(offset) + \
					'"length": {},'.format(length) + \
					'"short": "en","cacheTimeInMS": 300000},"query": ' \
					'"query TagPagePostsQuery($short: String, $slug: String\u0021, $order: String, $offset: Int\u0021, $length: Int\u0021) {\\n  locale(short: $short) {\\n    tag(slug: $slug) {\\n      cacheKey\\n      id\\n      posts(order: $order, offset: $offset, length: $length) {\\n        data {\\n          cacheKey\\n          id\\n          slug\\n          views\\n          postTranslate {\\n            cacheKey\\n            id\\n            title\\n            avatar\\n            published\\n            publishedHumanFormat\\n            leadText\\n            __typename\\n          }\\n          category {\\n            cacheKey\\n            id\\n            __typename\\n          }\\n          author {\\n            cacheKey\\n            id\\n            slug\\n            authorTranslates {\\n              cacheKey\\n              id\\n              name\\n              __typename\\n            }\\n            __typename\\n          }\\n          postBadge {\\n            cacheKey\\n            id\\n            label\\n            postBadgeTranslates {\\n              cacheKey\\n              id\\n              title\\n              __typename\\n            }\\n            __typename\\n          }\\n          showShares\\n          showStats\\n          __typename\\n        }\\n        postsCount\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n"}'
			yield FormRequest(url=start_url, callback=self.parse,
							  dont_filter=True, method="POST",
							  body=body_, headers=cfg.COINTELEGRAPH_HEADERS)
			offset += 15

	def parse(self, response, **kwargs):
		print(f"{color['fail']}All Blockchain CoinTelegraph Thread{color['endc']}")
		data = json.loads(response.body)  # load json data from API
		data_ = data['data']['locale']['tag']['posts']['data']
		for post in data_:
			post_badge_title = post['postBadge']['postBadgeTranslates'][0]['title'].lower()
			if post_badge_title == 'experts answer' or post_badge_title == 'explained':
				# link_content = self.url.format('explained/' + str(post['slug']))
				pass
			# else:
			link_content = cfg.COINTELEGRAPH_URL.format(
				'news/' + str(post['slug']))  # https://cointelegraph.com/news/ + slug
			yield response.follow(url=link_content, callback=self.parse_content, headers=cfg.COINTELEGRAPH_HEADERS)
		item = {
			'title': '',
			'data': data_,
			'source': 'coinTelegraph',
		}
		yield item
		sleep(3)

	def parse_content(self, response):
		page = response.url
		print(f"{color['okgreen']}Crawling raw content in {page}{color['endc']}")
		data = response.css('body')
		for content in data:
			item = {
				"raw_data": content.css('script::text').get(),
				'link_content': page,
				'tag': 'blockchain',
				"source": "coinTelegraph",
			}
			yield item
			sleep(2)


# ================================================
# cointelegraph.com/tags/litecoin
# ================================================
class CoinTeleLitecoinAll(Spider):
	name = 'allCointeleLitecoin'

	def start_requests(self):
		start_url = cfg.COINTELEGRAPH_API_DATA
		offset = 0
		length = 15
		for i in range(cfg.COINTELEGRAPH_TOTAL_PAGE):
			body_ = '{"operationName": "TagPagePostsQuery","variables": {"slug": "litecoin","order": "postPublishedTime",' + \
					'"offset": {},'.format(offset) + \
					'"length": {},'.format(length) + \
					'"short": "en","cacheTimeInMS": 300000},"query": ' \
					'"query TagPagePostsQuery($short: String, $slug: String\u0021, $order: String, $offset: Int\u0021, $length: Int\u0021) {\\n  locale(short: $short) {\\n    tag(slug: $slug) {\\n      cacheKey\\n      id\\n      posts(order: $order, offset: $offset, length: $length) {\\n        data {\\n          cacheKey\\n          id\\n          slug\\n          views\\n          postTranslate {\\n            cacheKey\\n            id\\n            title\\n            avatar\\n            published\\n            publishedHumanFormat\\n            leadText\\n            __typename\\n          }\\n          category {\\n            cacheKey\\n            id\\n            __typename\\n          }\\n          author {\\n            cacheKey\\n            id\\n            slug\\n            authorTranslates {\\n              cacheKey\\n              id\\n              name\\n              __typename\\n            }\\n            __typename\\n          }\\n          postBadge {\\n            cacheKey\\n            id\\n            label\\n            postBadgeTranslates {\\n              cacheKey\\n              id\\n              title\\n              __typename\\n            }\\n            __typename\\n          }\\n          showShares\\n          showStats\\n          __typename\\n        }\\n        postsCount\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n"}'
			yield FormRequest(url=start_url, callback=self.parse,
							  dont_filter=True, method="POST",
							  body=body_, headers=cfg.COINTELEGRAPH_HEADERS)
			offset += 15

	def parse(self, response, **kwargs):
		print(f"{color['fail']}All Litecoin CoinTelegraph Thread{color['endc']}")
		data = json.loads(response.body)  # load json data from API
		data_ = data['data']['locale']['tag']['posts']['data']
		for post in data_:
			post_badge_title = post['postBadge']['postBadgeTranslates'][0]['title'].lower()
			if post_badge_title == 'experts answer' or post_badge_title == 'explained':
				# link_content = self.url.format('explained/' + str(post['slug']))
				pass
			# else:
			link_content = cfg.COINTELEGRAPH_URL.format('news/' + str(post['slug']))  # https://cointelegraph.com/news/ + slug
			yield response.follow(url=link_content, callback=self.parse_content, headers=cfg.COINTELEGRAPH_HEADERS)
		item = {
			'title': '',
			'data': data_,
			'source': 'coinTelegraph',
		}
		yield item
		sleep(3)

	def parse_content(self, response):
		page = response.url
		print(f"{color['okgreen']}Crawling raw content in {page}{color['endc']}")
		data = response.css('body')
		for content in data:
			item = {
				"raw_data": content.css('script::text').get(),
				'link_content': page,
				'tag': 'litecoin',
				"source": "coinTelegraph",
			}
			yield item
			sleep(2)


# ================================================
# crawl 4 categories for latest news
# 'bitcoin', 'litecoin', 'blockchain', 'ethereum'
# ================================================
class CoinTelegraphLatest(Spider):
	name = 'latestCointele'

	def start_requests(self):
		start_url = cfg.COINTELEGRAPH_API_DATA
		latest_page = cfg.LATEST_PAGE
		offset = 0
		length = 15
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

	def parse(self, response, **kwargs):
		data = json.loads(response.body)
		print(f"{color['fail']}Latest CoinTelegraph Thread{color['endc']}")
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
		page = response.url
		print(f"{color['okgreen']}Crawling raw content in {page}{color['endc']}")
		data = response.css('body')
		for content in data:
			item = {
				'raw_data': content.css('script::text').get(),
				'link_content': page,
				# 'tag': 'bitcoin',
				"source": "coinTelegraph",
			}
			yield item
			sleep(2)


class AdapulseAll(Spider):
	name = 'allAdapulse'

	def start_requests(self):
		start_url = cfg.ADAPULSE_API_DATA
		for i in range(cfg.ADAPULSE_TOTAL_PAGE):
			body_ = 'action=csco_ajax_load_more&page={}'.format(i) + \
					'&posts_per_page=6&query_data=%7B%22infinite_load%22%3Afalse%2C%22query_vars%22%3A%7B%22ignore_sticky_posts%22%3Atrue%2C%22is_post_query%22%3Atrue%2C%22orderby%22%3A%22date%22%2C%22order%22%3A%22DESC%22%2C%22paged%22%3A1%2C%22posts_per_page%22%3A6%2C%22post_type%22%3A%22post%22%2C%22offset%22%3A%224%22%7D%2C%22in_the_loop%22%3Atrue%2C%22is_single%22%3Afalse%2C%22is_page%22%3Atrue%2C%22is_archive%22%3Afalse%2C%22is_author%22%3Afalse%2C%22is_category%22%3Afalse%2C%22is_tag%22%3Afalse%2C%22is_tax%22%3Afalse%2C%22is_home%22%3Afalse%2C%22is_singular%22%3Atrue%7D&attributes=%7B%22canvasClassName%22%3A%22cnvs-block-posts-1615051549690%22%2C%22canvasLocation%22%3A%22section-content%22%2C%22marginTop%22%3A0%2C%22paddingTop%22%3A0%2C%22layout%22%3A%22horizontal-type-1%22%2C%22query%22%3A%7B%22posts_type%22%3A%22post%22%2C%22categories%22%3A%22%22%2C%22tags%22%3A%22%22%2C%22formats%22%3A%22%22%2C%22posts%22%3A%22%22%2C%22offset%22%3A%224%22%2C%22orderby%22%3A%22date%22%2C%22order%22%3A%22DESC%22%2C%22time_frame%22%3A%22%22%2C%22taxonomy%22%3A%22%22%2C%22terms%22%3A%22%22%7D%2C%22layout_horizontal-type-1_paginationTypeAlt%22%3A%22ajax%22%2C%22layout_horizontal-type-1_areaPostsCount%22%3A6%2C%22layout_horizontal-type-1_typographyHeading%22%3A%221.85rem%22%2C%22layout_horizontal-type-1_showExcerpt%22%3Atrue%2C%22canvasBlockName%22%3A%22canvas%5C%2Fposts%22%2C%22queryGroup%22%3A%22%22%2C%22avoidDuplicatePosts%22%3Afalse%2C%22buttonLabel%22%3A%22View+Post%22%2C%22buttonStyle%22%3A%22%22%2C%22buttonSize%22%3A%22%22%2C%22buttonFullWidth%22%3Afalse%2C%22buttonColorBg%22%3A%22%22%2C%22buttonColorBg_dark%22%3A%22%22%2C%22buttonColorBgHover%22%3A%22%22%2C%22buttonColorBgHover_dark%22%3A%22%22%2C%22buttonColorText%22%3A%22%22%2C%22buttonColorText_dark%22%3A%22%22%2C%22buttonColorTextHover%22%3A%22%22%2C%22buttonColorTextHover_dark%22%3A%22%22%2C%22colorHeading_dark%22%3A%22%23000%22%2C%22colorHeadingHover_dark%22%3A%22%235a5a5a%22%2C%22colorText_dark%22%3A%22%22%2C%22colorMetaLinks_dark%22%3A%22%22%2C%22colorMetaLinksHover_dark%22%3A%22%22%2C%22colorMeta_dark%22%3A%22%22%2C%22layout_standard-type-1_columns_tablet%22%3A1%2C%22layout_standard-type-1_columns_mobile%22%3A1%2C%22layout_standard-type-1_gap_posts_tablet%22%3A%2240px%22%2C%22layout_standard-type-1_gap_posts_mobile%22%3A%2240px%22%2C%22layout_standard-type-2_columns_tablet%22%3A1%2C%22layout_standard-type-2_columns_mobile%22%3A1%2C%22layout_standard-type-2_gap_posts_tablet%22%3A%2240px%22%2C%22layout_standard-type-2_gap_posts_mobile%22%3A%2240px%22%2C%22layout_standard-type-3_columns_tablet%22%3A1%2C%22layout_standard-type-3_columns_mobile%22%3A1%2C%22layout_standard-type-3_gap_posts_tablet%22%3A%2240px%22%2C%22layout_standard-type-3_gap_posts_mobile%22%3A%2240px%22%2C%22layout_standard-type-4_columns_tablet%22%3A1%2C%22layout_standard-type-4_columns_mobile%22%3A1%2C%22layout_standard-type-4_gap_posts_tablet%22%3A%2240px%22%2C%22layout_standard-type-4_gap_posts_mobile%22%3A%2240px%22%2C%22layout_horizontal-type-1_columns%22%3A1%2C%22layout_horizontal-type-1_columns_tablet%22%3A1%2C%22layout_horizontal-type-1_columns_mobile%22%3A1%2C%22layout_horizontal-type-1_gap_posts%22%3A%2240px%22%2C%22layout_horizontal-type-1_gap_posts_tablet%22%3A%2240px%22%2C%22layout_horizontal-type-1_gap_posts_mobile%22%3A%2240px%22%2C%22layout_horizontal-type-1_image_width%22%3A%22half%22%2C%22layout_horizontal-type-1_bordersBetweenPosts%22%3Afalse%2C%22layout_horizontal-type-1_post_format%22%3Atrue%2C%22layout_horizontal-type-1_video%22%3Afalse%2C%22layout_horizontal-type-1_imageOrientation%22%3A%22original%22%2C%22layout_horizontal-type-1_imageSize%22%3A%22medium_large%22%2C%22layout_horizontal-type-1_typographyHeadingTag%22%3A%22h2%22%2C%22layout_horizontal-type-1_typographyExcerpt%22%3A%220.875rem%22%2C%22layout_horizontal-type-1_showMetaCategory%22%3Atrue%2C%22layout_horizontal-type-1_showMetaAuthor%22%3Atrue%2C%22layout_horizontal-type-1_showMetaDate%22%3Atrue%2C%22layout_horizontal-type-1_showMetaComments%22%3Afalse%2C%22layout_horizontal-type-1_showMetaViews%22%3Afalse%2C%22layout_horizontal-type-1_showMetaReadingTime%22%3Afalse%2C%22layout_horizontal-type-1_showMetaShares%22%3Afalse%2C%22layout_horizontal-type-1_metaCompact%22%3Afalse%2C%22layout_horizontal-type-1_metaExcerptLength%22%3A100%2C%22layout_horizontal-type-2_columns_tablet%22%3A1%2C%22layout_horizontal-type-2_columns_mobile%22%3A1%2C%22layout_horizontal-type-2_gap_posts_tablet%22%3A%2240px%22%2C%22layout_horizontal-type-2_gap_posts_mobile%22%3A%2240px%22%2C%22layout_horizontal-type-3_columns_tablet%22%3A1%2C%22layout_horizontal-type-3_columns_mobile%22%3A1%2C%22layout_horizontal-type-3_gap_posts_tablet%22%3A%2240px%22%2C%22layout_horizontal-type-3_gap_posts_mobile%22%3A%2240px%22%2C%22layout_horizontal-type-4_columns_tablet%22%3A1%2C%22layout_horizontal-type-4_columns_mobile%22%3A1%2C%22layout_horizontal-type-4_gap_posts_tablet%22%3A%2240px%22%2C%22layout_horizontal-type-4_gap_posts_mobile%22%3A%2240px%22%2C%22layout_horizontal-type-5_columns_tablet%22%3A1%2C%22layout_horizontal-type-5_columns_mobile%22%3A1%2C%22layout_horizontal-type-5_gap_posts_tablet%22%3A%2240px%22%2C%22layout_horizontal-type-5_gap_posts_mobile%22%3A%2240px%22%2C%22layout_tile-type-1_columns_tablet%22%3A1%2C%22layout_tile-type-1_columns_mobile%22%3A1%2C%22layout_tile-type-1_gap_posts_tablet%22%3A%2240px%22%2C%22layout_tile-type-1_gap_posts_mobile%22%3A%2240px%22%2C%22layout_tile-type-2_columns_tablet%22%3A1%2C%22layout_tile-type-2_columns_mobile%22%3A1%2C%22layout_tile-type-2_gap_posts_tablet%22%3A%220px%22%2C%22layout_tile-type-2_gap_posts_mobile%22%3A%220px%22%2C%22layout_tile-type-3_columns_tablet%22%3A1%2C%22layout_tile-type-3_columns_mobile%22%3A1%2C%22layout_tile-type-3_gap_posts_tablet%22%3A%220px%22%2C%22layout_tile-type-3_gap_posts_mobile%22%3A%220px%22%2C%22layout_reviews-1_colorHeading_dark%22%3A%22%23000%22%2C%22layout_reviews-1_colorHeadingHover_dark%22%3A%22%235a5a5a%22%2C%22layout_reviews-1_colorMeta_dark%22%3A%22%22%2C%22layout_reviews-1_colorMetaLinks_dark%22%3A%22%22%2C%22layout_reviews-1_colorMetaLinksHover_dark%22%3A%22%22%2C%22layout_reviews-2_colorHeading_dark%22%3A%22%23000%22%2C%22layout_reviews-2_colorHeadingHover_dark%22%3A%22%235a5a5a%22%2C%22layout_reviews-2_colorMeta_dark%22%3A%22%22%2C%22layout_reviews-2_colorMetaLinks_dark%22%3A%22%22%2C%22layout_reviews-2_colorMetaLinksHover_dark%22%3A%22%22%2C%22layout_reviews-3_colorHeading_dark%22%3A%22%23000%22%2C%22layout_reviews-3_colorHeadingHover_dark%22%3A%22%235a5a5a%22%2C%22layout_reviews-3_colorMeta_dark%22%3A%22%22%2C%22layout_reviews-3_colorMetaLinks_dark%22%3A%22%22%2C%22layout_reviews-3_colorMetaLinksHover_dark%22%3A%22%22%2C%22layout_reviews-4_colorHeading_dark%22%3A%22%23000%22%2C%22layout_reviews-4_colorHeadingHover_dark%22%3A%22%235a5a5a%22%2C%22layout_reviews-4_colorMeta_dark%22%3A%22%22%2C%22layout_reviews-4_colorMetaLinks_dark%22%3A%22%22%2C%22layout_reviews-4_colorMetaLinksHover_dark%22%3A%22%22%2C%22layout_reviews-5_colorHeading_dark%22%3A%22%23000%22%2C%22layout_reviews-5_colorHeadingHover_dark%22%3A%22%235a5a5a%22%2C%22layout_reviews-5_colorMeta_dark%22%3A%22%22%2C%22layout_reviews-5_colorMetaLinks_dark%22%3A%22%22%2C%22layout_reviews-5_colorMetaLinksHover_dark%22%3A%22%22%2C%22layout_reviews-6_colorHeading_dark%22%3A%22%23000%22%2C%22layout_reviews-6_colorHeadingHover_dark%22%3A%22%235a5a5a%22%2C%22layout_reviews-6_colorMeta_dark%22%3A%22%22%2C%22layout_reviews-6_colorMetaLinks_dark%22%3A%22%22%2C%22layout_reviews-6_colorMetaLinksHover_dark%22%3A%22%22%2C%22layout_reviews-7_colorHeading_dark%22%3A%22%23000%22%2C%22layout_reviews-7_colorHeadingHover_dark%22%3A%22%235a5a5a%22%2C%22layout_reviews-7_colorMeta_dark%22%3A%22%22%2C%22layout_reviews-7_colorMetaLinks_dark%22%3A%22%22%2C%22layout_reviews-7_colorMetaLinksHover_dark%22%3A%22%22%2C%22layout_reviews-8_colorHeading_dark%22%3A%22%23000%22%2C%22layout_reviews-8_colorHeadingHover_dark%22%3A%22%235a5a5a%22%2C%22layout_reviews-8_colorMeta_dark%22%3A%22%22%2C%22layout_reviews-8_colorMetaLinks_dark%22%3A%22%22%2C%22layout_reviews-8_colorMetaLinksHover_dark%22%3A%22%22%2C%22className%22%3A%22cnvs-block-posts+cnvs-block-posts-1615051549690+cnvs-block-posts-layout-horizontal-type-1%22%7D&options=%7B%22paginationTypeAlt%22%3A%22ajax%22%2C%22areaPostsCount%22%3A6%2C%22typographyHeading%22%3A%221.85rem%22%2C%22showExcerpt%22%3Atrue%2C%22columns%22%3A1%2C%22columns_tablet%22%3A1%2C%22columns_mobile%22%3A1%2C%22gap_posts%22%3A%2240px%22%2C%22gap_posts_tablet%22%3A%2240px%22%2C%22gap_posts_mobile%22%3A%2240px%22%2C%22image_width%22%3A%22half%22%2C%22bordersBetweenPosts%22%3Afalse%2C%22post_format%22%3Atrue%2C%22video%22%3Afalse%2C%22imageOrientation%22%3A%22original%22%2C%22imageSize%22%3A%22medium_large%22%2C%22typographyHeadingTag%22%3A%22h2%22%2C%22typographyExcerpt%22%3A%220.875rem%22%2C%22showMetaCategory%22%3Atrue%2C%22showMetaAuthor%22%3Atrue%2C%22showMetaDate%22%3Atrue%2C%22showMetaComments%22%3Afalse%2C%22showMetaViews%22%3Afalse%2C%22showMetaReadingTime%22%3Afalse%2C%22showMetaShares%22%3Afalse%2C%22metaCompact%22%3Afalse%2C%22metaExcerptLength%22%3A100%7D&_ajax_nonce=6d1b9fb3f7'
		# body_ = 'action=csco_ajax_load_more&page=1&posts_per_page=6&query_data=%7B%22infinite_load%22%3Afalse%2C%22query_vars%22%3A%7B%22ignore_sticky_posts%22%3Atrue%2C%22is_post_query%22%3Atrue%2C%22orderby%22%3A%22date%22%2C%22order%22%3A%22DESC%22%2C%22paged%22%3A1%2C%22posts_per_page%22%3A6%2C%22post_type%22%3A%22post%22%2C%22offset%22%3A%224%22%7D%2C%22in_the_loop%22%3Atrue%2C%22is_single%22%3Afalse%2C%22is_page%22%3Atrue%2C%22is_archive%22%3Afalse%2C%22is_author%22%3Afalse%2C%22is_category%22%3Afalse%2C%22is_tag%22%3Afalse%2C%22is_tax%22%3Afalse%2C%22is_home%22%3Afalse%2C%22is_singular%22%3Atrue%7D&attributes=%7B%22canvasClassName%22%3A%22cnvs-block-posts-1615051549690%22%2C%22canvasLocation%22%3A%22section-content%22%2C%22marginTop%22%3A0%2C%22paddingTop%22%3A0%2C%22layout%22%3A%22horizontal-type-1%22%2C%22query%22%3A%7B%22posts_type%22%3A%22post%22%2C%22categories%22%3A%22%22%2C%22tags%22%3A%22%22%2C%22formats%22%3A%22%22%2C%22posts%22%3A%22%22%2C%22offset%22%3A%224%22%2C%22orderby%22%3A%22date%22%2C%22order%22%3A%22DESC%22%2C%22time_frame%22%3A%22%22%2C%22taxonomy%22%3A%22%22%2C%22terms%22%3A%22%22%7D%2C%22layout_horizontal-type-1_paginationTypeAlt%22%3A%22ajax%22%2C%22layout_horizontal-type-1_areaPostsCount%22%3A6%2C%22layout_horizontal-type-1_typographyHeading%22%3A%221.85rem%22%2C%22layout_horizontal-type-1_showExcerpt%22%3Atrue%2C%22canvasBlockName%22%3A%22canvas%5C%2Fposts%22%2C%22queryGroup%22%3A%22%22%2C%22avoidDuplicatePosts%22%3Afalse%2C%22buttonLabel%22%3A%22View+Post%22%2C%22buttonStyle%22%3A%22%22%2C%22buttonSize%22%3A%22%22%2C%22buttonFullWidth%22%3Afalse%2C%22buttonColorBg%22%3A%22%22%2C%22buttonColorBg_dark%22%3A%22%22%2C%22buttonColorBgHover%22%3A%22%22%2C%22buttonColorBgHover_dark%22%3A%22%22%2C%22buttonColorText%22%3A%22%22%2C%22buttonColorText_dark%22%3A%22%22%2C%22buttonColorTextHover%22%3A%22%22%2C%22buttonColorTextHover_dark%22%3A%22%22%2C%22colorHeading_dark%22%3A%22%23000%22%2C%22colorHeadingHover_dark%22%3A%22%235a5a5a%22%2C%22colorText_dark%22%3A%22%22%2C%22colorMetaLinks_dark%22%3A%22%22%2C%22colorMetaLinksHover_dark%22%3A%22%22%2C%22colorMeta_dark%22%3A%22%22%2C%22layout_standard-type-1_columns_tablet%22%3A1%2C%22layout_standard-type-1_columns_mobile%22%3A1%2C%22layout_standard-type-1_gap_posts_tablet%22%3A%2240px%22%2C%22layout_standard-type-1_gap_posts_mobile%22%3A%2240px%22%2C%22layout_standard-type-2_columns_tablet%22%3A1%2C%22layout_standard-type-2_columns_mobile%22%3A1%2C%22layout_standard-type-2_gap_posts_tablet%22%3A%2240px%22%2C%22layout_standard-type-2_gap_posts_mobile%22%3A%2240px%22%2C%22layout_standard-type-3_columns_tablet%22%3A1%2C%22layout_standard-type-3_columns_mobile%22%3A1%2C%22layout_standard-type-3_gap_posts_tablet%22%3A%2240px%22%2C%22layout_standard-type-3_gap_posts_mobile%22%3A%2240px%22%2C%22layout_standard-type-4_columns_tablet%22%3A1%2C%22layout_standard-type-4_columns_mobile%22%3A1%2C%22layout_standard-type-4_gap_posts_tablet%22%3A%2240px%22%2C%22layout_standard-type-4_gap_posts_mobile%22%3A%2240px%22%2C%22layout_horizontal-type-1_columns%22%3A1%2C%22layout_horizontal-type-1_columns_tablet%22%3A1%2C%22layout_horizontal-type-1_columns_mobile%22%3A1%2C%22layout_horizontal-type-1_gap_posts%22%3A%2240px%22%2C%22layout_horizontal-type-1_gap_posts_tablet%22%3A%2240px%22%2C%22layout_horizontal-type-1_gap_posts_mobile%22%3A%2240px%22%2C%22layout_horizontal-type-1_image_width%22%3A%22half%22%2C%22layout_horizontal-type-1_bordersBetweenPosts%22%3Afalse%2C%22layout_horizontal-type-1_post_format%22%3Atrue%2C%22layout_horizontal-type-1_video%22%3Afalse%2C%22layout_horizontal-type-1_imageOrientation%22%3A%22original%22%2C%22layout_horizontal-type-1_imageSize%22%3A%22medium_large%22%2C%22layout_horizontal-type-1_typographyHeadingTag%22%3A%22h2%22%2C%22layout_horizontal-type-1_typographyExcerpt%22%3A%220.875rem%22%2C%22layout_horizontal-type-1_showMetaCategory%22%3Atrue%2C%22layout_horizontal-type-1_showMetaAuthor%22%3Atrue%2C%22layout_horizontal-type-1_showMetaDate%22%3Atrue%2C%22layout_horizontal-type-1_showMetaComments%22%3Afalse%2C%22layout_horizontal-type-1_showMetaViews%22%3Afalse%2C%22layout_horizontal-type-1_showMetaReadingTime%22%3Afalse%2C%22layout_horizontal-type-1_showMetaShares%22%3Afalse%2C%22layout_horizontal-type-1_metaCompact%22%3Afalse%2C%22layout_horizontal-type-1_metaExcerptLength%22%3A100%2C%22layout_horizontal-type-2_columns_tablet%22%3A1%2C%22layout_horizontal-type-2_columns_mobile%22%3A1%2C%22layout_horizontal-type-2_gap_posts_tablet%22%3A%2240px%22%2C%22layout_horizontal-type-2_gap_posts_mobile%22%3A%2240px%22%2C%22layout_horizontal-type-3_columns_tablet%22%3A1%2C%22layout_horizontal-type-3_columns_mobile%22%3A1%2C%22layout_horizontal-type-3_gap_posts_tablet%22%3A%2240px%22%2C%22layout_horizontal-type-3_gap_posts_mobile%22%3A%2240px%22%2C%22layout_horizontal-type-4_columns_tablet%22%3A1%2C%22layout_horizontal-type-4_columns_mobile%22%3A1%2C%22layout_horizontal-type-4_gap_posts_tablet%22%3A%2240px%22%2C%22layout_horizontal-type-4_gap_posts_mobile%22%3A%2240px%22%2C%22layout_horizontal-type-5_columns_tablet%22%3A1%2C%22layout_horizontal-type-5_columns_mobile%22%3A1%2C%22layout_horizontal-type-5_gap_posts_tablet%22%3A%2240px%22%2C%22layout_horizontal-type-5_gap_posts_mobile%22%3A%2240px%22%2C%22layout_tile-type-1_columns_tablet%22%3A1%2C%22layout_tile-type-1_columns_mobile%22%3A1%2C%22layout_tile-type-1_gap_posts_tablet%22%3A%2240px%22%2C%22layout_tile-type-1_gap_posts_mobile%22%3A%2240px%22%2C%22layout_tile-type-2_columns_tablet%22%3A1%2C%22layout_tile-type-2_columns_mobile%22%3A1%2C%22layout_tile-type-2_gap_posts_tablet%22%3A%220px%22%2C%22layout_tile-type-2_gap_posts_mobile%22%3A%220px%22%2C%22layout_tile-type-3_columns_tablet%22%3A1%2C%22layout_tile-type-3_columns_mobile%22%3A1%2C%22layout_tile-type-3_gap_posts_tablet%22%3A%220px%22%2C%22layout_tile-type-3_gap_posts_mobile%22%3A%220px%22%2C%22layout_reviews-1_colorHeading_dark%22%3A%22%23000%22%2C%22layout_reviews-1_colorHeadingHover_dark%22%3A%22%235a5a5a%22%2C%22layout_reviews-1_colorMeta_dark%22%3A%22%22%2C%22layout_reviews-1_colorMetaLinks_dark%22%3A%22%22%2C%22layout_reviews-1_colorMetaLinksHover_dark%22%3A%22%22%2C%22layout_reviews-2_colorHeading_dark%22%3A%22%23000%22%2C%22layout_reviews-2_colorHeadingHover_dark%22%3A%22%235a5a5a%22%2C%22layout_reviews-2_colorMeta_dark%22%3A%22%22%2C%22layout_reviews-2_colorMetaLinks_dark%22%3A%22%22%2C%22layout_reviews-2_colorMetaLinksHover_dark%22%3A%22%22%2C%22layout_reviews-3_colorHeading_dark%22%3A%22%23000%22%2C%22layout_reviews-3_colorHeadingHover_dark%22%3A%22%235a5a5a%22%2C%22layout_reviews-3_colorMeta_dark%22%3A%22%22%2C%22layout_reviews-3_colorMetaLinks_dark%22%3A%22%22%2C%22layout_reviews-3_colorMetaLinksHover_dark%22%3A%22%22%2C%22layout_reviews-4_colorHeading_dark%22%3A%22%23000%22%2C%22layout_reviews-4_colorHeadingHover_dark%22%3A%22%235a5a5a%22%2C%22layout_reviews-4_colorMeta_dark%22%3A%22%22%2C%22layout_reviews-4_colorMetaLinks_dark%22%3A%22%22%2C%22layout_reviews-4_colorMetaLinksHover_dark%22%3A%22%22%2C%22layout_reviews-5_colorHeading_dark%22%3A%22%23000%22%2C%22layout_reviews-5_colorHeadingHover_dark%22%3A%22%235a5a5a%22%2C%22layout_reviews-5_colorMeta_dark%22%3A%22%22%2C%22layout_reviews-5_colorMetaLinks_dark%22%3A%22%22%2C%22layout_reviews-5_colorMetaLinksHover_dark%22%3A%22%22%2C%22layout_reviews-6_colorHeading_dark%22%3A%22%23000%22%2C%22layout_reviews-6_colorHeadingHover_dark%22%3A%22%235a5a5a%22%2C%22layout_reviews-6_colorMeta_dark%22%3A%22%22%2C%22layout_reviews-6_colorMetaLinks_dark%22%3A%22%22%2C%22layout_reviews-6_colorMetaLinksHover_dark%22%3A%22%22%2C%22layout_reviews-7_colorHeading_dark%22%3A%22%23000%22%2C%22layout_reviews-7_colorHeadingHover_dark%22%3A%22%235a5a5a%22%2C%22layout_reviews-7_colorMeta_dark%22%3A%22%22%2C%22layout_reviews-7_colorMetaLinks_dark%22%3A%22%22%2C%22layout_reviews-7_colorMetaLinksHover_dark%22%3A%22%22%2C%22layout_reviews-8_colorHeading_dark%22%3A%22%23000%22%2C%22layout_reviews-8_colorHeadingHover_dark%22%3A%22%235a5a5a%22%2C%22layout_reviews-8_colorMeta_dark%22%3A%22%22%2C%22layout_reviews-8_colorMetaLinks_dark%22%3A%22%22%2C%22layout_reviews-8_colorMetaLinksHover_dark%22%3A%22%22%2C%22className%22%3A%22cnvs-block-posts+cnvs-block-posts-1615051549690+cnvs-block-posts-layout-horizontal-type-1%22%7D&options=%7B%22paginationTypeAlt%22%3A%22ajax%22%2C%22areaPostsCount%22%3A6%2C%22typographyHeading%22%3A%221.85rem%22%2C%22showExcerpt%22%3Atrue%2C%22columns%22%3A1%2C%22columns_tablet%22%3A1%2C%22columns_mobile%22%3A1%2C%22gap_posts%22%3A%2240px%22%2C%22gap_posts_tablet%22%3A%2240px%22%2C%22gap_posts_mobile%22%3A%2240px%22%2C%22image_width%22%3A%22half%22%2C%22bordersBetweenPosts%22%3Afalse%2C%22post_format%22%3Atrue%2C%22video%22%3Afalse%2C%22imageOrientation%22%3A%22original%22%2C%22imageSize%22%3A%22medium_large%22%2C%22typographyHeadingTag%22%3A%22h2%22%2C%22typographyExcerpt%22%3A%220.875rem%22%2C%22showMetaCategory%22%3Atrue%2C%22showMetaAuthor%22%3Atrue%2C%22showMetaDate%22%3Atrue%2C%22showMetaComments%22%3Afalse%2C%22showMetaViews%22%3Afalse%2C%22showMetaReadingTime%22%3Afalse%2C%22showMetaShares%22%3Afalse%2C%22metaCompact%22%3Afalse%2C%22metaExcerptLength%22%3A100%7D&_ajax_nonce=6d1b9fb3f7'
			yield FormRequest(url=start_url, callback=self.parse,
							  dont_filter=True, method='POST',
							  body=body_, headers=cfg.ADAPULSE_HEADERS)

	def parse(self, response, **kwargs):
		utils.show_message('', 'fail', 'All Adapulse Thread')
		data = json.loads(response.body)
		raw_contents = data['data']['content']

		def extraction_with_css(post, query):
			return post.css(query).get(default='').strip()

		response_ = HtmlResponse(url='url', body=raw_contents, encoding='utf-8')
		# title = Selector(response=response_).xpath('//h2/a/text()').getall()
		for post in response_.xpath('//article'):
			item = {
				'title': extraction_with_css(post, 'h2 a::text'),
				'link_content': extraction_with_css(post, 'a::attr(href)'),
				'subtitle': extraction_with_css(post, 'div.cs-entry__excerpt::text'),
				'link_img': extraction_with_css(post, 'noscript img::attr(src)'),
				'description': extraction_with_css(post, 'div.cs-entry__excerpt::text'),
				'slug_content': extraction_with_css(post, 'a::attr(href)').split('.io')[1],
				'author': extraction_with_css(post, 'span.cs-author::text'),
				'link_author': extraction_with_css(post, 'a.cs-meta-author-inner::attr(href)'),
				'tag': post.css('li a::text').getall(),
				'link_tag': post.css('li a::attr(href)').getall(),
				'published': extraction_with_css(post, 'div.cs-meta-date::text'),
				'source': 'adapulse.io',
				'latest': 0,
				'approve': 1,
			}
			yield response.follow(url=item['link_content'], callback=self.parse_content, headers=cfg.ADAPULSE_HEADERS)
			utils.show_message('', 'warning', response.follow(url=item['link_content'], callback=self.parse_content, headers=cfg.ADAPULSE_HEADERS))
			# utils.show_message('title', 'okcyan', item)
			yield item
		sleep(1.5)

	def parse_content(self, response):
		def extraction_with_css(query):
			return response.css(query).get(default='').strip()
		# get datePublished and dateModified
		json_data = response.css('head')
		json_data = json.loads(json_data.css('script[type="application/ld+json"]::text').extract_first())
		json_data = json_data['@graph'][2]
		data = {
			'raw_content': extraction_with_css('div.entry-content'),
			'link_content': extraction_with_css('div.pk-share-buttons-wrap::attr(data-share-url)'),
			'datePublished': json_data['datePublished'] if 'datePublished' in json_data else '',
			'dateModified': json_data['dateModified'] if 'dateModified' in json_data else '',
			'source': 'adapulse.io',
		}
		yield data
		sleep(.5)
