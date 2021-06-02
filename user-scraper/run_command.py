import queue
import shlex
import pymongo
import subprocess
import os
import time
import threading


mongoClient = pymongo.MongoClient("mongodb://root:password@localhost:27017/")
myDatabase = mongoClient['twitterdata']
trackUser = myDatabase['trackUser']
followUser = myDatabase['followUser']
userTable = myDatabase['user']


class MyThread(threading.Thread):
	def __init__(self, start_, end_):
		threading.Thread.__init__(self)
		self.start_ = int(start_)
		self.end_ = int(end_)

	def run(self):
		start_time = time.time()
		normal_input_data(self.start_, self.end_)
		# auto_crawl(0, 2)
		end_time = time.time()
		print(f"\n\n\ntotal time: {end_time-start_time}")


def insert_one_to_follow_user(item):
	return followUser.insert_one(item)


def put_data_to_follow_user():
	i = 0
	for user in userTable.find({}, {'id': 1, 'screen_name': 1}).sort("statuses_count", -1):
		screen_name = user['screen_name']
		print(screen_name)
		if followUser.find_one({'screen_name': screen_name}):
			print(f'{screen_name} available')
			pass
		else:
			insert_one_to_follow_user(user)
			print(f'{i} import {screen_name} success!')
			i += 1


# put_data_to_follow_user()


def get_users():
	list_users = []
	users = followUser.find({}, {"screen_name": 1})
	print(users)
	for user in users:
		list_users.append(user['screen_name'])
	return list_users


def normal_input_data(start, end):
	for user in get_users()[start:end]:
		print(f"start: {user}")
		try:
			run_command(user)
		except NameError:
			print(NameError)


def run_command(user):
	command = 'scrapy crawl TweetScraper -a query="{}"'.format(user)
	# args = shlex.split(command)
	# print(args)
	# subprocess.Popen(args=args, shell=True)
	os.system(command)


def get_many_users(limit_user):
	list_users = []
	users = followUser.find({}, {'screen_name': 1}).limit(limit_user)
	for user in users:
		list_users.append(user['screen_name'])
	return list_users


def auto_crawl(n=0, limit_user=10, limit_threads=10, take_users=200):
	while True:
		listUsers = get_many_users(limit_user)
		threads = list()
		for index in range(limit_threads):
			u = listUsers[n:limit_user][index]
			print(f'start {u}')
			try:
				# start thread
				threading.Thread(target=run_command, args=(u,)).start()
			except NameError:
				print(f'Error: {NameError}')
		for index, thread in enumerate(threads):
			# end thread
			thread.join()
		n += limit_threads
		limit_user += limit_threads
		if n == take_users:
			break
		time.sleep(20)


def get_user_by(sort_by="statuses_count"):
	# .sort(sort_by, 1) ascending
	# .sort(sort_by, -1) descending
	list_users = userTable.find({}, {'screen_name': 1, sort_by: 1}).sort(sort_by, -1)
	for user in list_users:
		print(user['statuses_count'], user['screen_name'])
	return list_users


if __name__ == "__main__":
	start = time.time()
	auto_crawl()
	end = time.time()
	print(f"Total time: {end - start}")


# get_user_by()
# 183s for 100 users with sleep 20 among 10 users at once time
# 1179s ~19.64s for 500 user with sleep 20 among 10 users at once time 347 records
