import os
import re
import json
import shutil
import calendar
from w3lib import html
from dateutil.parser import parse
from time import sleep
from itemadapter import ItemAdapter
from . import text_rank_4_keyword
from datetime import datetime, timezone
from scrapy.http import Request

csv_path = 'CardanoScraper/CardanoScraper/Data/csv/'
raw_data_path = 'CardanoScraper/CardanoScraper/Data/raw/'
textRank = text_rank_4_keyword.TextRank4Keyword()


def colors_mark():
	colors = {
		'header': '\033[95m',
		'okblue': '\033[94m',
		'okcyan': '\033[96m',
		'okgreen': '\033[92m',
		'warning': '\033[93m',
		'fail': '\033[91m',
		'endc': '\033[0m',
		'bold': '\033[1m',
		'underline': '\033[4m',
	}
	return colors


color = colors_mark()


def remove_punctuation(word):
	return re.sub(r'[!?.:;,"()-]', "", word)


def save_to_html(page, content):
	html_file = f'cardano-{page}.html'
	html_path = raw_data_path + html_file
	with open(html_path, 'wb') as file:
		file.write(content)
		print(f'Saved file to: {html_path}')


def create_data_directory():
	# create Date directory
	os.makedirs('CardanoScraper/CardanoScraper/Data/csv', exist_ok=True)
	os.makedirs('CardanoScraper/CardanoScraper/Data/raw', exist_ok=True)


def remove_html_tags(raw_content):
	clean = re.compile('<.*?>')
	clear_html_tags = re.sub(clean, '', raw_content)
	clear_html_tags = re.sub('[\@\#]\w+', ' ', clear_html_tags)
	clear_html_tags = re.sub('[\/\#]\w+', ' ', clear_html_tags)
	clear_special_char = re.sub('[^A-Za-z0-9]+', ' ', clear_html_tags)
	return remove_small_words(clear_special_char)


def remove_small_words(words):
	split_words = words.lower().split(' ')
	unwanted_words = {'https', 'g', 'm', 'heck', 'ser', '200k', 'longgggg',
					  'wzrds', 'omarzb5', 'tel', 'haha', 'co',
					  'https', 'www', 'com', 'boys', 'dan', 'con', 'los', 'que', 'url', 'nbsp', 'title'}
	split_words = [ele for ele in split_words if ele not in unwanted_words]

	for word in split_words:
		if 'https' == word.strip():
			split_words.remove('https')
		if len(word) < 3:
			split_words.remove(word)
	return ' '.join(split_words).lower()


def initialize_sample_data():
	data = {
		'publish_date': '',
		'timestamp': '',
		'approve': 1,
		'author_title': '',
		'author_display_name': '',
		'author_thumbnail': '',
		'author_job_titles': '',
		'author_profile_links': '',
		'post_main_img': '',
		'lang': '',
		'title': '',
		'slug': '',
		'subtitle': '',
		'audio': '',
		'soundcloud': [],
		'raw_content': '',
		'keyword_ranking': '',
		'total_pages': '',
		'filters': '',
		'recent_posts': '',
		'current_page': '',
		'current_url_page': '',
		'link_content': '',
		'author_profile_url': '',
		'source': 'iohk',
		'raw_data': '',
	}
	return data


def handle_datetime(data, date_time):
	# cardar: 28 November 2017 19:22
	# coindesk: Jun 17, 2021
	# iohk:
	# datetime of IOHK
	if '-' in date_time:
		date_time = date_time.split('T')[0]
		data['timestamp'] = datetime.strptime(date_time, "%Y-%m-%d").timestamp()
		return data['timestamp']
	# datetime of coindesk
	elif ',' in date_time and len(date_time) != 0:
		# data['timestamp'] = datetime.strptime(date_time, '%b %d, %Y').timestamp()
		data['timestamp'] = datetime.strptime(date_time, '%B %d, %Y').timestamp() \
			if date_time.split(' ')[0] in calendar.month_name \
			else datetime.strptime(date_time, '%b %d, %Y').timestamp()
		return data['timestamp']
	elif len(date_time) == 0:  # date is '' in recent posts: source returns: Yesterday at 4:39 p.m, Yesterday at 4:39 p.m,..
		data['timestamp'] = datetime.now().timestamp()
		return data['timestamp']
	# datetime of cardano
	data['timestamp'] = datetime.strptime(date_time, "%d %B %Y %H:%M").timestamp()
	return data['timestamp']


def handle_utc_datetime(str_date, data):
	my_date = parse(str_date)
	# data['published'] = str_date
	# data['date'] = str_date
	data['timestamp'] = my_date.timestamp()


def get_table(table):
	return str(table).split(', ')[-1].split("'")[1]


def write_json_file(file, item):
	line = json.dumps(ItemAdapter(item['avatars']).asdict()) + '\n'
	file.write(line)


def decode_html_content(raw_content):
	return html.remove_entities(raw_content)


def clean_html_tags(raw_content):
	return html.remove_tags(raw_content)


def text_ranking(data, raw_content_):
	raw_content = clean_html_tags(raw_content_)
	raw_content = remove_html_tags(raw_content)
	# raw_content = remove_small_words(raw_content)
	textRank.analyze(raw_content, window_size=6)
	data['keyword_ranking'] = textRank.get_keywords(10)
	return data['keyword_ranking']


def insert_into_table(table, data):
	if table.insert_one(data):
		show_message('', 'okgreen', f'Imported into table: {get_table(table)} | Post: {data["link_content"] if "link_content" in data else data["link_post"]}')
	sleep(1)


# ================================================
# update table: query follows link_content
# ================================================
def update_news(table, data):
	query = {
		'link_content': data['link_content'],
	}
	if table.update_one(query, {'$set': data}):
		show_message('', 'okcyan', f'Updated into table: {get_table(table)} | Post: {data["link_content"] if "link_content" in data else data["link_post"]}')
	sleep(.5)


def update_success_notify(table):
	print(f"{color['okcyan']}Updated {get_table(table)} table Successfully!{color['endc']}\n")


def update_rawcontent_notify(table, data):
	print(f"{color['okcyan']}Updating Raw Content into {get_table(table)}{color['endc']} for post: {data['link_content']}")


def insert_success_notify(table):
	print(f"{color['okgreen']}Imported Posts {get_table(table)} success!!!{color['endc']}")


def show_message(message, colour, data):
	print(f"{message} {color[colour]}{data}{color['endc']}")


def show_keyword(data):
	show_message('Getting raw_content', 'okcyan', data['link_content'])
	show_message('keyword_ranking', 'warning', data['keyword_ranking'])


def handle_empty_content(table, new_posts):
	data = table.find()
	for post in data:
		link_content = post['link_content']
		if 'raw_content' not in post:
			show_message('empty content', 'fail', link_content)
			if link_content in new_posts:
				new_posts.remove(link_content)
			my_query = {'link_content': link_content}
			posts = table.find({}, my_query)
			for empty_content in posts:
				# utils.show_message('empty content', 'fail', empty_content)
				pass
			if table.delete_one(my_query):
				show_message('Empty content post was deleted!', 'okblue', 1)
		elif post['raw_content'] == '':
			my_query = {'link_content': link_content}
			show_message('raw_content = ""', 'fail', link_content)
			if link_content in new_posts:
				new_posts.remove(link_content)
			if table.delete_one(my_query):
				pass
		else:
			pass
	for index, value in enumerate(new_posts):
		show_message(message='Latest Post for today', colour='okblue', data={index: value})
