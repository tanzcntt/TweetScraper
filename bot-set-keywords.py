import sys
import time
import pymongo
import re
import getopt
import asyncio
from CardanoScraper.CardanoScraper.text_rank_4_keyword import TextRank4Keyword
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
import utils

# ================================================
# Options
# ================================================

stop_list = {
    '%', 'quot;how', 'ins', 'outs', '0Self', 'https://', '×', 'FAQ', 'ii', 'カルダノプラットフォームの分散化の実現には、高度の機能の実現だけではなく、大衆がいかにそれを理解し、利用できる環境の提供が必要となる。しかし、ブロックチェン全般とカルダノ独自の技術開発上の用語をまとめたコンテンツはあまり見られないのが現状である'
    '当プロジェクトによって、カルダノプラットフォームをめぐる技術上または専門的な用語をわかりやすく説明できるWEB辞書を構築するものである',
    "また、この用語辞書は、ウェブ上に単なる文字情報として提供するだけでなく、アニメーションや動画像による音声や映像によっても構成されるのが特徴である",
    "。", "さらに、同コンテンツは、英語によるコンテンツを基本とするが、利用者層の多い日本語、韓国語、中国語にも翻訳して提供できるようにする",
    "１）技術用語や専門用語の数", "E", "amp", "#", "ex", "X", "+", "X1", "$", "https://", "PRüF", ":)", "set", "®", "co",
    "|", "10k", "+15",
}

colors = utils.colors_mark()
argumentList = sys.argv[1:]
options = "u:t:"
long_options = ['url', 'token']
url = ''
token = ''
try:
	arguments, values = getopt.getopt(argumentList, options, long_options)
	# checking each argument
	for currentArgument, currentValue in arguments:
		if currentArgument in ('-u', '--url'):
			url = str(currentValue)
		if currentArgument in ('-t', '--token'):
			token = str(currentValue)
except getopt.error as err:
	print(err)

print(url, token)

textRank = TextRank4Keyword()


class HandleKeywords():
	def __init__(self):
		self.mongoClient = pymongo.MongoClient('mongodb://root:password@localhost:27017/')
		self.myDatabase = self.mongoClient['dhuntData']
		self.twitter = self.myDatabase['twitter']
		self.idea = self.myDatabase['idea']

	def tweet_without_keyword(self):
		pass

	def idea_without_keyword(self):
		url_ = 'https://gql.dhunt.io/'
		headers = {
			"Authorization": "Bearer defaulttoken"
		}
		transport = AIOHTTPTransport(url=url_, headers=headers)

		# create a Graphql client using the defined transport
		client = Client(transport=transport, fetch_schema_from_transport=True)
		i_ = 0
		take = 40
		skip = 0
		while True:
			print(take, skip)
			query = gql(
				"""query ideaWithoutKeyword($take: Int!, $skip: Int!){
					ideaWithoutKeyword(take: $take, skip: $skip){
						id
						contentJson
						keywords
					}
				}"""
			)
			result = client.execute(query, variable_values={"take": take, "skip": skip})

			# ================================================
			# Handle text ranking
			# ================================================
			ideas = result['ideaWithoutKeyword']
			for idea in ideas:
				list_content = ''
				content_json = idea["contentJson"]
				for i in content_json:
					content_json[i]['a'] = utils.remove_html_tags(content_json[i]['a'])
					content_json[i]['b'] = utils.remove_html_tags(content_json[i]['b'])
					list_content += content_json[i]['a']
					list_content += content_json[i]['b']

				# print(f"{str(i_)} {colors['okgreen']} {list_content} {colors['endc']}")
				keywords = self.keywords_ranking(list_content)
				print(f"{colors['okcyan']} {keywords} {colors['endc']}")
				with open('test_stopwords2.json', 'a') as file:
					file.write(str(i_) + str(keywords))

			i_ += 1
			take += 40
			skip += 40
			# if result['ideaWithoutKeyword']:
			# 	pass
			if take == 400:
				break
			print(take, skip)
			# time.sleep(1)


	def keywords_ranking(self, raw_content):
		textRank.analyze(raw_content.lower(), window_size=6, candidate_post=['NOUN', 'PROPN'])  # , stopwords=stop_list)
		keywords = textRank.get_keywords(10)
		return keywords

	# def remove_html_tags(self, raw_content):
	# 	clean = re.compile('<.*?>')
	# 	clear_special_char = re.sub('[^A-Za-z0-9]+', ' ', raw_content)
	# 	return re.sub(clean, '', clear_special_char)


start = time.time()
data = HandleKeywords()
print(data.idea_without_keyword())
end = time.time()
print(f"{colors['okblue']} Total time:{(end - start)/60} {colors['endc']}")
# limit, offset
