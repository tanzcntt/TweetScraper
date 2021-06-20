import os
import re
import json
import shutil
from time import sleep
from itemadapter import ItemAdapter
from . import text_rank_4_keyword
from datetime import datetime

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
					  'https', 'www', 'com', 'boys', 'dan', 'con', 'los', 'que'}
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
		data['timestamp'] = datetime.strptime(date_time, '%b %d, %Y').timestamp()
		return data['timestamp']
	elif len(date_time) == 0:  # date is '' in recent posts: source returns: Yesterday at 4:39 p.m, Yesterday at 4:39 p.m,..
		data['timestamp'] = datetime.now().timestamp()
		return data['timestamp']
	# datetime of cardano
	data['timestamp'] = datetime.strptime(date_time, "%d %B %Y %H:%M").timestamp()
	return data['timestamp']


def get_table(table):
	return str(table).split(', ')[-1].split("'")[1]


def write_json_file(file, item):
	line = json.dumps(ItemAdapter(item['avatars']).asdict()) + '\n'
	file.write(line)


def text_ranking(data, raw_content_):
	raw_content = remove_html_tags(raw_content_)
	textRank.analyze(raw_content, window_size=6)
	data['keyword_ranking'] = textRank.get_keywords(10)
	return data['keyword_ranking']


def insert_into_table(table, data):
	if table.insert_one(data):
		print(f"{color['okgreen']}Imported Posts {get_table(table)} success!!!{color['endc']}")
	sleep(1)


def update_success_notify(table):
	print(f"{color['okcyan']}Updating {get_table(table)} table{color['endc']}\n")


def update_rawcontent_notify(table, data):
	print(f"{color['okcyan']}Updating Raw Content into {get_table(table)}{color['endc']} for post: {data['link_content']}")


def insert_success_notify(table):
	print(f"{color['okgreen']}Imported Posts {get_table(table)} success!!!{color['endc']}")


def show_message(message, colour, data):
	print(f"{message}: {color[colour]}{data}{color['endc']}")
