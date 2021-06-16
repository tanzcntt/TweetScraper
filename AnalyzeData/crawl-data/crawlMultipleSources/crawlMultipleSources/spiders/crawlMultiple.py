import scrapy
from time import sleep
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request


class BlockchaininfluencersSpider(CrawlSpider):
	name = 'influencers'
	allowed_domains = ['www.upfolio.com/blockchain-influencers']
	start_urls = ['https://www.upfolio.com/blockchain-influencers/']

	# rules = (
	#     Rule(LinkExtractor(allow=r'Items/'), callback='parse_item', follow=True),
	# )

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
