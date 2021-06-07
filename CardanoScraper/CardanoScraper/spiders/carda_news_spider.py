import scrapy
from scrapy import Request
from .. import utils


class CardanoSpider(scrapy.Spider):
	name = "cardaSpider"

	def start_requests(self):
		urls = [
			'https://forum.cardano.org/c/english/announcements/13?page=0',
			'https://forum.cardano.org/c/english/announcements/13?page=1',
			'https://forum.cardano.org/c/english/announcements/13?page=2',
		]
		for url in urls:
			yield Request(url=url, callback=self.parse)

	def parse(self, response, **kwargs):
		page = response.url.split('page=')[1]
		# page = "all", save all page in 1 html file
		utils.save_to_html(page, content=response.body)

		posts = response.css('tr.topic-list-item')
		for post in posts:
			yield {
				'main_link_title': post.css('td.main-link span.link-top-line a.raw-topic-link::text').get(),
				'link_post': post.css('td.main-link span.link-top-line a::attr(href)').get(),
				'posters': post.css('td.posters a::attr(href)').getall(),
				'replies': post.css('td.replies span.posts::text').get(),
				'views': post.css('td.views span.views::text').get(),
				'date': post.css('td::text').getall()[-1],
			}
