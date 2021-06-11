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
		self.url_ = 'https://gql.dhunt.io/'
		self.headers = {
			"Authorization": "Bearer defaulttoken"
		}

	def tweet_without_keyword(self):
		pass

	def idea_without_keyword(self):
		transport = AIOHTTPTransport(url=self.url_, headers=self.headers)
		# create a Graphql client using the defined transport
		client = Client(transport=transport, fetch_schema_from_transport=True)
		i_ = 0
		while True:
			query = gql(
				"""query ideaWithoutKeyword($take: Int!, $skip: Int!){
					ideaWithoutKeyword(take: $take, skip: $skip){
						id
						contentJson
						keywords
					}
				}"""
			)
			result = client.execute(query, variable_values={"take": 10, "skip": 0})

			# ================================================
			# Handle text ranking
			# ================================================
			ideas = result['ideaWithoutKeyword']
			if ideas:
				for idea in ideas:
					list_content = ''
					content_json = idea["contentJson"]
					for i in content_json:
						content_json[i]['a'] = utils.remove_html_tags(content_json[i]['a'])
						content_json[i]['b'] = utils.remove_html_tags(content_json[i]['b'])
						list_content += content_json[i]['a']
						list_content += content_json[i]['b']
						if 'c' in content_json[i]:
							content_json[i]['c'] = utils.remove_html_tags(content_json[i]['c'])
							list_content += content_json[i]['c']

					keywords = self.keywords_ranking(list_content)
					print(f"{colors['okcyan']} {keywords} {colors['endc']}")
					with open('test_stopwords2.json', 'a') as file:
						file.write(str(i_) + str(keywords))
					self.push_data_to_submit_idea(idea['id'], keywords)
				i_ += 1
			else:
				break

	def keywords_ranking(self, raw_content):
		textRank.analyze(raw_content, window_size=6, candidate_post=['NOUN', 'PROPN'])  # , stopwords=stop_list)
		keywords = textRank.get_keywords(10)
		return keywords

	def push_data_to_submit_idea(self, id, keywords):
		params = {"keywords": str(keywords), "id": id}
		print(params)
		transport = AIOHTTPTransport(url=self.url_, headers=self.headers)
		client = Client(transport=transport, fetch_schema_from_transport=True)
		query = gql(
			"""
			mutation submitIdeaKeyword($keywords : String!, $id : String!){
				submitIdeaKeyword(keywords : $keywords, id : $id) {
					id
					keywords
				}
			}
			"""
		)
		client.execute(query, variable_values=params)


start = time.time()
data = HandleKeywords()
print(data.idea_without_keyword())
end = time.time()
print(f"{colors['okblue']} Total time:{(end - start)/60} {colors['endc']}")
