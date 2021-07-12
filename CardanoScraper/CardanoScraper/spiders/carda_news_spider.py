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
# iohk.io/en/blog/posts/page-1
# ================================================================================================
class IohkContent(Spider):
	name = "allIohk"

	def start_requests(self):
		total_page = 0
		while True:
			yield Request(url=cfg.IOHK_API_DATA.format(total_page), callback=self.parse, headers=cfg.IOHK_HEADERS)
			utils.show_message('', 'warning', Request(url=cfg.IOHK_API_DATA.format(total_page), callback=self.parse, headers=cfg.IOHK_HEADERS))
			total_page += 1
			if total_page > cfg.IOHK_TOTAL_PAGE:
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
		total_page = cfg.LATEST_PAGE
		for i in range(total_page):
			yield Request(url=cfg.IOHK_API_DATA.format(i), callback=self.parse, headers=cfg.IOHK_HEADERS)

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
