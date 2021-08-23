import json
from time import sleep
from .. import utils
from scrapy import Spider
from scrapy.http import Request, FormRequest, HtmlResponse
from .. import config as cfg


class NewsbtcSpider(Spider):
	name = 'newsbtc'

	def __init__(self, mode, **kwargs):
		super(NewsbtcSpider, self).__init__()
		self.mode = mode

	def start_requests(self):
		start_url = cfg.NEWSBTC_API_DATA
		if self.mode == 'latest':
			utils.show_message('Crawling:', 'okgreen', self.mode.upper())
			for i in range(cfg.LATEST_PAGE):
				body_ = 'lang=en_US&action=jnews_module_ajax_jnews_block_3&module=true&data%5Bfilter%5D=0&data%5Bfilter_type%5D=all&data%5B' + \
						'current_page%5D={}&data%5Battribute%5D%5Bheader_icon%5D=&data%5Battribute%5D%5B'.format(i+1) + \
						'first_title%5D=&data%5Battribute%5D%5Bsecond_title%5D=&data%5Battribute%5D%5Burl%5D=&data%5Battribute%5D%5Bheader_type%5D=heading_6&data%5Battribute%5D%5Bheader_background%5D=&data%5Battribute%5D%5Bheader_secondary_background%5D=&data%5Battribute%5D%5Bheader_text_color%5D=&data%5Battribute%5D%5Bheader_line_color%5D=&data%5Battribute%5D%5Bheader_accent_color%5D=&data%5Battribute%5D%5Bheader_filter_category%5D=&data%5Battribute%5D%5Bheader_filter_author%5D=&data%5Battribute%5D%5Bheader_filter_tag%5D=&data%5Battribute%5D%5Bheader_filter_text%5D=All&data%5Battribute%5D%5Bpost_type%5D=post&data%5Battribute%5D%5Bcontent_type%5D=all&data%5B' + \
						'attribute%5D%5Bnumber_post%5D={}&data%5Battribute%5D%5Bpost_offset%5D=0&data%5B'.format(cfg.NEWSBTC_NUMBER_POST) + \
						'attribute%5D%5Bunique_content%5D=disable&data%5Battribute%5D%5Binclude_post%5D=&data%5Battribute%5D%5Bexclude_post%5D=&data%5Battribute%5D%5B' + \
						'include_category%5D={}&data%5Battribute%5D%5Bexclude_category%5D=&data%5B'.format(3) + \
						'attribute%5D%5Binclude_author%5D=&data%5Battribute%5D%5Binclude_tag%5D=&data%5Battribute%5D%5Bexclude_tag%5D=&data%5Battribute%5D%5Bevents_year%5D=&data%5Battribute%5D%5Bevents_month%5D=&data%5Battribute%5D%5Bsort_by%5D=latest&data%5Battribute%5D%5Bdate_format%5D=default&data%5Battribute%5D%5Bdate_format_custom%5D=Y%2Fm%2Fd&data%5Battribute%5D%5Bexcerpt_length%5D=20&data%5Battribute%5D%5Bexcerpt_ellipsis%5D=...&data%5Battribute%5D%5Bforce_normal_image_load%5D=&data%5Battribute%5D%5Bpagination_mode%5D=loadmore&data%5Battribute%5D%5Bpagination_nextprev_showtext%5D=&data%5Battribute%5D%5B' + \
						'pagination_number_post%5D={}&data%5Battribute%5D%5Bpagination_scroll_limit%5D=0&'.format(cfg.NEWSBTC_NUMBER_POST) + \
					   	'data%5Battribute%5D%5Bads_type%5D=disable&data%5Battribute%5D%5Bads_position%5D=1&data%5Battribute%5D%5Bads_random%5D=&data%5Battribute%5D%5Bads_image%5D=&data%5Battribute%5D%5Bads_image_tablet%5D=&data%5Battribute%5D%5Bads_image_phone%5D=&data%5Battribute%5D%5Bads_image_link%5D=&data%5Battribute%5D%5Bads_image_alt%5D=&data%5Battribute%5D%5Bads_image_new_tab%5D=&data%5Battribute%5D%5Bgoogle_publisher_id%5D=&data%5Battribute%5D%5Bgoogle_slot_id%5D=&data%5Battribute%5D%5Bgoogle_desktop%5D=auto&data%5Battribute%5D%5Bgoogle_tab%5D=auto&data%5Battribute%5D%5Bgoogle_phone%5D=auto&data%5Battribute%5D%5Bcontent%5D=&data%5Battribute%5D%5Bads_bottom_text%5D=&data%5Battribute%5D%5Bboxed%5D=false&data%5Battribute%5D%5Bboxed_shadow%5D=false&data%5Battribute%5D%5Bel_id%5D=&data%5Battribute%5D%5Bel_class%5D=&data%5Battribute%5D%5Bscheme%5D=&data%5Battribute%5D%5Bcolumn_width%5D=auto&data%5Battribute%5D%5Btitle_color%5D=&data%5Battribute%5D%5Baccent_color%5D=&data%5Battribute%5D%5Balt_color%5D=&data%5Battribute%5D%5Bexcerpt_color%5D=&data%5Battribute%5D%5Bcss%5D=&data%5Battribute%5D%5Bpaged%5D=1&data%5Battribute%5D%5Bpagination_align%5D=center&data%5Battribute%5D%5Bpagination_navtext%5D=false&data%5Battribute%5D%5Bpagination_pageinfo%5D=false&data%5Battribute%5D%5Bbox_shadow%5D=false&data%5Battribute%5D%5Bpush_archive%5D=true&data%5Battribute%5D%5Bcolumn_class%5D=jeg_col_2o3&data%5Battribute%5D%5Bclass%5D=jnews_block_3'
				yield FormRequest(url=start_url, callback=self.parse, dont_filter=True, method='POST', body=body_, headers=cfg.NEWSBTC_HEADERS)
		elif self.mode == 'all':
			utils.show_message('Crawling:', 'okgreen', self.mode.upper())
			for i in range(cfg.NEWSBTC_TOTAL_PAGE):
				body_ = 'lang=en_US&action=jnews_module_ajax_jnews_block_3&module=true&data%5Bfilter%5D=0&data%5Bfilter_type%5D=all&data%5B' + \
						'current_page%5D={}&data%5Battribute%5D%5Bheader_icon%5D=&data%5Battribute%5D%5B'.format(i+1) + \
						'first_title%5D=&data%5Battribute%5D%5Bsecond_title%5D=&data%5Battribute%5D%5Burl%5D=&data%5Battribute%5D%5Bheader_type%5D=heading_6&data%5Battribute%5D%5Bheader_background%5D=&data%5Battribute%5D%5Bheader_secondary_background%5D=&data%5Battribute%5D%5Bheader_text_color%5D=&data%5Battribute%5D%5Bheader_line_color%5D=&data%5Battribute%5D%5Bheader_accent_color%5D=&data%5Battribute%5D%5Bheader_filter_category%5D=&data%5Battribute%5D%5Bheader_filter_author%5D=&data%5Battribute%5D%5Bheader_filter_tag%5D=&data%5Battribute%5D%5Bheader_filter_text%5D=All&data%5Battribute%5D%5Bpost_type%5D=post&data%5Battribute%5D%5Bcontent_type%5D=all&data%5B' + \
						'attribute%5D%5Bnumber_post%5D={}&data%5Battribute%5D%5Bpost_offset%5D=0&data%5B'.format(cfg.NEWSBTC_NUMBER_POST) + \
						'attribute%5D%5Bunique_content%5D=disable&data%5Battribute%5D%5Binclude_post%5D=&data%5Battribute%5D%5Bexclude_post%5D=&data%5Battribute%5D%5B' + \
						'include_category%5D={}&data%5Battribute%5D%5Bexclude_category%5D=&data%5B'.format(3) + \
						'attribute%5D%5Binclude_author%5D=&data%5Battribute%5D%5Binclude_tag%5D=&data%5Battribute%5D%5Bexclude_tag%5D=&data%5Battribute%5D%5Bevents_year%5D=&data%5Battribute%5D%5Bevents_month%5D=&data%5Battribute%5D%5Bsort_by%5D=latest&data%5Battribute%5D%5Bdate_format%5D=default&data%5Battribute%5D%5Bdate_format_custom%5D=Y%2Fm%2Fd&data%5Battribute%5D%5Bexcerpt_length%5D=20&data%5Battribute%5D%5Bexcerpt_ellipsis%5D=...&data%5Battribute%5D%5Bforce_normal_image_load%5D=&data%5Battribute%5D%5Bpagination_mode%5D=loadmore&data%5Battribute%5D%5Bpagination_nextprev_showtext%5D=&data%5Battribute%5D%5B' + \
						'pagination_number_post%5D={}&data%5Battribute%5D%5Bpagination_scroll_limit%5D=0&'.format(cfg.NEWSBTC_NUMBER_POST) + \
					   	'data%5Battribute%5D%5Bads_type%5D=disable&data%5Battribute%5D%5Bads_position%5D=1&data%5Battribute%5D%5Bads_random%5D=&data%5Battribute%5D%5Bads_image%5D=&data%5Battribute%5D%5Bads_image_tablet%5D=&data%5Battribute%5D%5Bads_image_phone%5D=&data%5Battribute%5D%5Bads_image_link%5D=&data%5Battribute%5D%5Bads_image_alt%5D=&data%5Battribute%5D%5Bads_image_new_tab%5D=&data%5Battribute%5D%5Bgoogle_publisher_id%5D=&data%5Battribute%5D%5Bgoogle_slot_id%5D=&data%5Battribute%5D%5Bgoogle_desktop%5D=auto&data%5Battribute%5D%5Bgoogle_tab%5D=auto&data%5Battribute%5D%5Bgoogle_phone%5D=auto&data%5Battribute%5D%5Bcontent%5D=&data%5Battribute%5D%5Bads_bottom_text%5D=&data%5Battribute%5D%5Bboxed%5D=false&data%5Battribute%5D%5Bboxed_shadow%5D=false&data%5Battribute%5D%5Bel_id%5D=&data%5Battribute%5D%5Bel_class%5D=&data%5Battribute%5D%5Bscheme%5D=&data%5Battribute%5D%5Bcolumn_width%5D=auto&data%5Battribute%5D%5Btitle_color%5D=&data%5Battribute%5D%5Baccent_color%5D=&data%5Battribute%5D%5Balt_color%5D=&data%5Battribute%5D%5Bexcerpt_color%5D=&data%5Battribute%5D%5Bcss%5D=&data%5Battribute%5D%5Bpaged%5D=1&data%5Battribute%5D%5Bpagination_align%5D=center&data%5Battribute%5D%5Bpagination_navtext%5D=false&data%5Battribute%5D%5Bpagination_pageinfo%5D=false&data%5Battribute%5D%5Bbox_shadow%5D=false&data%5Battribute%5D%5Bpush_archive%5D=true&data%5Battribute%5D%5Bcolumn_class%5D=jeg_col_2o3&data%5Battribute%5D%5Bclass%5D=jnews_block_3'
				yield FormRequest(url=start_url, callback=self.parse,
								  dont_filter=True, method='POST',
								  body=body_, headers=cfg.NEWSBTC_HEADERS)
		else:
			utils.show_message('', 'fail', 'Please retype mode: `latest` or `all`')
			exit()

	def parse(self, response, **kwargs):
		utils.show_message('response.url: ', 'okcyan', response.url)
		json_data = json.loads(response.body)
		raw_contents = json_data['content']
		response_ = HtmlResponse(url='url', body=raw_contents, encoding='utf-8')
		for post in response_.xpath('//article'):
			item = {
				'title': utils.decode_html_content(utils.extraction_with_css(post, 'h3[class="jeg_post_title"] a::text')),
				'link_content': utils.extraction_with_css(post, 'h3[class="jeg_post_title"] a::attr(href)'),
				'subtitle': utils.decode_html_content(utils.extraction_with_css(post, 'div[class="jeg_post_excerpt"] p::text')),
				'link_img': utils.extraction_with_css(post, 'div.thumbnail-container img::attr(data-src)'),
				'slug_content': utils.extraction_with_css(post, 'h3[class="jeg_post_title"] a::attr(href)').split('.com')[1],
				'author': utils.extraction_with_css(post, 'div[class="jeg_meta_author"] a::text'),
				'link_author': utils.extraction_with_css(post, 'div[class="jeg_meta_author"] a::attr(href)'),
				'published': utils.extraction_with_css(post, 'div[class="jeg_meta_date"] a::text'),
				'source': 'newsbtc.com',
				'latest': 1 if self.mode == 'latest' else 0,
				'approve': 1,
			}
			yield response.follow(url=item['link_content'], callback=self.parse_content, headers=cfg.NEWSBTC_HEADERS)
			yield item
			sleep(.25)

	def parse_content(self, response):
		json_data = response.css('head')
		json_data = json.loads(json_data.css('script[type="application/ld+json"]::text').extract_first())
		json_data = json_data['@graph'][0]
		default_img = 'https://www.newsbtc.com/wp-content/uploads/2021/04/cropped-cropped-cropped-favicon-200x200.png'
		item = {
			'link_img': json_data['image']['url'] if 'image' in json_data else default_img,
			'link_content': response.url,
			'datePublished': json_data['datePublished'] if 'datePublished' in json_data else '',
			'dateModified': json_data['dateModified'] if 'dateModified' in json_data else json_data['datePublished'],
			'keywords': list(map(lambda x: x.replace(' ', '').lower() if ' ' in x else x.lower(), json_data['Keywords'].split(','))) if 'Keywords' in json_data else [],
			'source': 'newsbtc.com',
		}
		# utils.show_message('item', 'okgreen', item)
		raw_data = utils.decode_html_content(utils.extraction_with_css(response, 'div.content-inner'))
		raw_ = response.css('div.content-inner')
		jeg_ad = raw_.css('div[class="jeg_ad jeg_ad_article"]').getall()
		js = raw_.css('script[type="text/javascript"]').getall()
		# remove advertise
		for value in jeg_ad:
			raw_data = raw_data.replace(value, '')
		# remove text/javascript
		for value in js:
			raw_data = raw_data.replace(value, '')
		item['raw_content'] = utils.decode_html_content(raw_data)
		yield item
		# sleep(.2)
