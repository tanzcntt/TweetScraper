import pymongo
from TweetScraper.colors import Colors
from datetime import datetime

mongoClient = pymongo.MongoClient("mongodb://root:password@localhost:27017/")
myDatabase = mongoClient["twitterdata"]
userTable = myDatabase['user']
followUserTable = myDatabase['followUser']
testTable = myDatabase['test']

y = userTable.find()


def find_one():
	x = userTable.find_one()


# result will excluded "id_str" from the result
def find_exclude():
	for x in userTable.find({}, {"id_str": 0}):
		print(x)


# insert one record to db
def insert_one_to_table(item):
	x = followUserTable.insert_one(item)
	return x


def insert_many_to_table(items):
	return followUserTable.insert_many(items)


def put_data_to_table():
	i = 0
	# only take id and screen_name
	for x in userTable.find({}, {'id': 1, 'screen_name': 1}):
		if insert_one_to_table(x):
			print(f'Import {i} success!')
		# print(i, x)
		i += 1


# data = {'data': {'user': {'id': 'VXNlcjoyMjk0MDIxOQ==',
# 						  'rest_id': '22940219',
# 						  'affiliates_highlighted_label': {},
# 						  'legacy': {'created_at': 'Thu Mar 05 16:33:48 +0000 2009', 'default_profile': False,
# 									 'default_profile_image': False, 'description': '',
# 									 'entities': {'description': {'urls': []}, 'url': {'urls': [
# 										 {'display_url': 'eminem.com', 'expanded_url': 'http://www.eminem.com',
# 										  'url': 'http://t.co/sG0n8tkeh4', 'indices': [0, 22]}]}},
# 									 'fast_followers_count': 0, 'favourites_count': 0, 'followers_count': 22613854,
# 									 'friends_count': 0, 'has_custom_timelines': False, 'is_translator': False,
# 									 'listed_count': 54289, 'location': 'Detroit', 'media_count': 421,
# 									 'name': 'Marshall Mathers', 'normal_followers_count': 22613854,
# 									 'pinned_tweet_ids_str': ['1339799237605900288'], 'profile_banner_extensions': {
# 								  'mediaColor': {'r': {'ok': {
# 									  'palette': [{'percentage': 46.4, 'rgb': {'blue': 15, 'green': 14, 'red': 53}},
# 												  {'percentage': 45.77, 'rgb': {'blue': 85, 'green': 73, 'red': 72}},
# 												  {'percentage': 5.65, 'rgb': {'blue': 13, 'green': 17, 'red': 79}},
# 												  {'percentage': 1.07, 'rgb': {'blue': 47, 'green': 22, 'red': 25}},
# 												  {'percentage': 0.55,
# 												   'rgb': {'blue': 40, 'green': 19, 'red': 71}}]}}}},
# 									 'profile_banner_url': 'https://pbs.twimg.com/profile_banners/22940219/1608271811',
# 									 'profile_image_extensions': {'mediaColor': {'r': {'ok': {
# 										 'palette': [{'percentage': 92.41, 'rgb': {'blue': 30, 'green': 30, 'red': 30}},
# 													 {'percentage': 5.37,
# 													  'rgb': {'blue': 207, 'green': 207, 'red': 207}}]}}}},
# 									 'profile_image_url_https': 'https://pbs.twimg.com/profile_images/1218209106491793408/ZZ7zbeWL_normal.jpg',
# 									 'profile_interstitial_type': '', 'protected': False, 'screen_name': 'Eminem',
# 									 'statuses_count': 1071, 'translator_type': 'regular',
# 									 'url': 'http://t.co/sG0n8tkeh4', 'verified': True, 'withheld_in_countries': []},
# 						  'legacy_extended_profile': {},
# 						  'is_profile_translatable': False}}}

my_date = datetime.now()
# legacy = data['data']['user']['legacy']


# def put_to_test():
# 	myDict = [
# 		{"rest_id": data['data']['user']['rest_id'],
# 		 "crawlTime": my_date.isoformat(),
# 		 "followers_count": legacy['followers_count'],
# 		 "friends_count": legacy['friends_count'],
# 		 "favourites_count": legacy['favourites_count'],
# 		 "fast_followers_count": legacy['fast_followers_count'],
# 		 "listed_count": legacy['listed_count'],
# 		 "media_count": legacy['media_count'],
# 		 "normal_followers_count": legacy['normal_followers_count'],
# 		 "statuses_count": legacy['statuses_count'],
# 		 "verified": legacy['verified'],
# 		 }
# 	]
# 	if testTable.insert_many(myDict):
# 		print("success")

# print(Colors.WARNING + "warning")
# print("abc")

def find_user():
	list_users = []
	users = followUserTable.find({}, {"screen_name": 1})
	for user in users:
		print(user['screen_name'])
		list_users.append(user['screen_name'])
	print(list_users)

if __name__ == "__main__":
	pass
	put_data_to_table()
	# put_to_test()
	# find_user()
