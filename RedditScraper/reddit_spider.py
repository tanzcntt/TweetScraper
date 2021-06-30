import os
import json
import pymongo
import praw
import pandas as pd
import utils
from datetime import datetime
from time import sleep


helpers = utils.Utils()
cardano_systems = ['cardano', 'CardanoDevelopers', 'CardanoStakePools', 'Cardano_ELI5', 'CardanoNFTs']


def post_reddit(post):
	return [post.title, post.score, post.id, post.subreddit, post.url, post.num_comments, post.selftext, post.created]


class RedditCrawl(object):
	def __init__(self, subreddit, limit_posts, mode):
		self.mongoClient = pymongo.MongoClient("mongodb://root:password@localhost:27017/")
		self.myDatabase = self.mongoClient['dhuntData']
		self.redditSample = self.myDatabase['reddit']
		self.reddit = praw.Reddit(client_id='2joBTPQGTQc9hw', client_secret='AJniSlLx_9B2xdoXSZVSlhGz56Ebww', user_agent='Scraping Cardano')
		self.subreddit = subreddit  # ['cardano', 'CardanoDevelopers', 'CardanoStakePools', 'Cardano_ELI5', 'CardanoNFTs']
		self.limit = limit_posts
		self.mode = mode
		self.reddit_url = "https://www.reddit.com/r/cardano/{}"

	def sample_data(self, post):
		data = {
			'author': str(post.author),
			'id': post.id,
			'name': post.name,
			'title': post.title,
			'like': post.score,
			'upvote_ratio': post.upvote_ratio,
			'num_comments': post.num_comments,
			# 'comments': post.comments,
			'subreddit': str(post.subreddit),
			'link_content': self.reddit_url.format(post.permalink),
			'permalink': post.permalink,
			'urls_in_post': post.url,
			# 'link_flair_template_id': post.link_flair_template_id,
			'link_flair_text': post.link_flair_text,
			'raw_content': post.selftext,
			'created': datetime.fromtimestamp(post.created).isoformat(),
			'timestamp': post.created,
			# 'clicked': post.clicked,  # Whether or not the submission has been clicked by the client.
			# 'distinguished': post.distinguished,  # Whether or not the submission is distinguished.
			# 'edited': post.edited,  # Whether or not the submission has been edited.
			# 'is_original_content': post.is_original_content,  # Whether or not the submission has been set as original content.
		}
		return data

	def load_posts(self, post):
		return [post.title, post.score, post.id, post.subreddit,
				post.url, post.num_comments, post.selftext, post.created]

	def get_posts(self):
		new_posts = self.check_modes()
		# data = list(map(self.load_posts, new_posts))
		# self.save_to_csv(data, 'new')
		for index, post in enumerate(new_posts):
			print(f"{index} Inserting...'id': {post.id}, 'title': {post.title}")
			self.insert_into_table(table=self.redditSample, data=self.sample_data(post))
			sleep(.02)

	def check_modes(self):
		if self.mode == 'new':
			new_posts = self.reddit.subreddit(self.subreddit).new(limit=self.limit)
			return new_posts
		elif self.mode == 'top':
			new_posts = self.reddit.subreddit(self.subreddit).top(limit=self.limit)
			return new_posts
		elif self.mode == 'hot':
			new_posts = self.reddit.subreddit(self.subreddit).hot(limit=self.limit)
			return new_posts

	def get_comments(self):
		pass

	def save_comments(self):
		pass

	def save_to_csv(self, data, file_name):
		posts = pd.DataFrame(data, columns=['id', 'title', 'like', 'num_comments', 'subreddit', 'url', 'selftext', 'created'])
		file_name_ = f'reddit_{file_name}.csv'
		posts.to_csv(utils.csv_path + file_name_)
		dir_path = os.path.realpath(file_name_)  # dirname(os.path.realpath(file_name_))
		helpers.show_message('Saved to', 'warning', dir_path)

	def save_to_json(self, file_name):
		df = pd.read_csv(file_name, encoding='ISO-8859-1')
		file_name_ = f'reddit_{file_name}.json'
		if df.to_json(utils.json_path + file_name_):
			dir_path = os.path.realpath(file_name_)
			helpers.show_message('Saved to', 'warning', dir_path)

	def insert_into_table(self, table, data):
		if table.find_one({'link_content': data['link_content']}):
			self.update_table(table, data)
		else:
			if table.insert_one(data):
				helpers.show_message('Import data success', 'okgreen', 1)

	def update_table(self, table, data):
		query = {
			'id': data['id'],
		}
		if table.update_one(query, {'$set': data}):
			helpers.show_message('Updating', 'okblue', data["link_content"] + '\n')

	def subreddit_description(self):
		description = self.reddit.subreddit(self.subreddit)
		helpers.show_message(f'{self.subreddit} description', 'bold', description)

	def main(self):
		self.get_posts()


if __name__ == '__main__':
	RedditCrawl(subreddit='cardano', limit_posts=50, mode='new').main()
	RedditCrawl(subreddit='cardano', limit_posts=50, mode='top').main()
	RedditCrawl(subreddit='cardano', limit_posts=50, mode='hot').main()
