import os
import re
from w3lib import html
from TweetScraper.CardanoScraper.CardanoScraper.text_rank_4_keyword import TextRank4Keyword

csv_path = 'Data/csv/'
json_path = 'Data/json/'
textRank = TextRank4Keyword()


class Utils:
	def __init__(self):
		pass

	def colors_mark(self):
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

	def create_data_directory(self):
		if os.path.isdir(csv_path) is False:
			os.makedirs(csv_path, exist_ok=True)
			os.makedirs(json_path, exist_ok=True)
		else:
			pass
	# color = colors_mark()

	def show_message(self, message, colour, data):
		print(f"{message}: {self.colors_mark()[colour]}{data}{self.colors_mark()['endc']}")

	def remove_html_tags(self, raw_content):
		clean = re.compile('<.*?>')
		clear_html_tags = re.sub(clean, '', raw_content)
		clear_html_tags = re.sub('[\@\#]\w+', ' ', clear_html_tags)
		clear_html_tags = re.sub('[\/\#]\w+', ' ', clear_html_tags)
		clear_special_char = re.sub('[^A-Za-z0-9]+', ' ', clear_html_tags)
		return self.remove_small_words(clear_special_char)

	def remove_small_words(self, words):
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

	def clean_html_tags(self, raw_content):
		return html.remove_tags(raw_content)

	def text_ranking(self, raw_content_):
		raw_content = self.clean_html_tags(raw_content_)
		raw_content = self.remove_html_tags(raw_content)
		# raw_content = remove_small_words(raw_content)
		textRank.analyze(raw_content, window_size=6)
		# data['keyword_ranking'] = textRank.get_keywords(10)
		return textRank.get_keywords(10)


Utils().create_data_directory()
