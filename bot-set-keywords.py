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
		while True:
			query = gql(
				"""query {
					ideaWithoutKeyword{
						id
						contentJson
						keywords
					}
				}"""
			)
			result = client.execute(query)
			ideas = result['ideaWithoutKeyword']
			for idea in ideas:
				list_content = ''
				content_json = idea["contentJson"]
				for i in content_json:
					content_json[i]['a'] = self.remove_html_tags(content_json[i]['a'])
					content_json[i]['b'] = self.remove_html_tags(content_json[i]['b'])
					list_content += content_json[i]['a']
					list_content += content_json[i]['b']

				print(f"{str(i_)} {colors['okgreen']} {list_content} {colors['endc']}")

				keywords = self.keywords_ranking(list_content)
				print(f"{colors['okcyan']} {keywords} {colors['endc']}")
			i_ += 1
			if result['ideaWithoutKeyword']:
				pass
			time.sleep(2)

	def keywords_ranking(self, raw_content):
		textRank.analyze(raw_content, window_size=6, candidate_post=['NOUN', 'PROPN'], stopwords={'%'})
		keywords = textRank.get_keywords(8)
		return keywords
		# data['keyword']

	def remove_html_tags(self, raw_content):
		clean = re.compile('<.*?>')
		return re.sub(clean, '', raw_content)


data = HandleKeywords()
print(data.idea_without_keyword())
