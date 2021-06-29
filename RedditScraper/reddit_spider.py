import praw

reddit = praw.Reddit(client_id='2joBTPQGTQc9hw', client_secret='AJniSlLx_9B2xdoXSZVSlhGz56Ebww', user_agent='Scraping Cardano')

hot_posts = reddit.subreddit('cardano').new(limit=1000)
for index, post in enumerate(hot_posts):
	print(index, post.title, ' || ', post.selftext)
	print('\n')
	# pass

# carda_posts = reddit.subreddit('cardano')
# print(carda_posts.description)

# ml_subreddit = reddit.subreddit('MachineLearning')
#
# print(ml_subreddit.description)
