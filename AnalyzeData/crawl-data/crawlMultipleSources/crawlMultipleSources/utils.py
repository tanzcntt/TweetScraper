import os
import re


csv_path = 'CardanoScraper/CardanoScraper/Data/csv/'
raw_data_path = 'CardanoScraper/CardanoScraper/Data/raw/'


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


# create_data_directory()


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


def remove_html_tags(raw_content):
	clean = re.compile('<.*?>')
	clear_html_tags = re.sub(clean, '', raw_content)
	clear_html_tags = re.sub('[\@\#]\w+', ' ', clear_html_tags)
	clear_html_tags = re.sub('[\/\#]\w+', ' ', clear_html_tags)
	clear_html_tags = re.sub('[^A-Za-z0-9]+', ' ', clear_html_tags)
	clean_small_words = remove_small_words(clear_html_tags)
	return clean_small_words


def remove_small_words(words):
	split_words = words.lower().split(' ')
	unwanted_words = {'https', 'g', 'm', 'heck', 'ser', '200k', 'longgggg',
					  'wzrds', 'omarzb5', 'tel', 'haha', 'co', 'lol', 'heck',
					  'https', 'www', 'com', 'boys', 'dan', 'con', 'los', 'que',
					  'hmmm', 'hell', 'shit', 'damn'}
	split_words = [ele for ele in split_words if ele not in unwanted_words]

	for word in split_words:
		if 'https' == word.strip():
			split_words.remove('https')
		if len(word) < 3:
			split_words.remove(word)
	return ' '.join(split_words).lower()
