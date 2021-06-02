import requests

headers = {
	'authority': 'twitter.com',
	'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
	'x-twitter-client-language': 'vi',
	'x-csrf-token': '8a644c92873b25719489af4e8d5937d657cf2e1606c4858d110e77358ceaa011ea751b7bdc5aff4423d9d909cce2b6d0a480038e0e1594805a3b70f180a5d4990d20c9e7a2b35808759d2524868923b8',
	'sec-ch-ua-mobile': '?0',
	'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
	'content-type': 'application/json',
	'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36',
	'x-twitter-auth-type': 'OAuth2Session',
	'x-twitter-active-user': 'yes',
	'accept': '*/*',
	'sec-fetch-site': 'same-origin',
	'sec-fetch-mode': 'cors',
	'sec-fetch-dest': 'empty',
	'referer': 'https://twitter.com/',
	'accept-language': 'en-US,en;q=0.9',
	'cookie': 'personalization_id="v1_EOfGH9SnYUbpPzOKALzTMQ=="; guest_id=v1%3A162193305456291859; _ga=GA1.2.2104893886.1621993444; _twitter_sess=BAh7CSIKZmxhc2hJQzonQWN0aW9uQ29udHJvbGxlcjo6Rmxhc2g6OkZsYXNo%250ASGFzaHsABjoKQHVzZWR7ADoPY3JlYXRlZF9hdGwrCES2O8B5AToMY3NyZl9p%250AZCIlODZkMzg2ZWQzN2ZiZWEwMzcwOTVkNzhmMjgxMzAwNjg6B2lkIiU0ZjA0%250AYzZkMTdhNzVlN2E5NzE4NjEzM2ZmYTI4MGI0Mw%253D%253D--f01f431ad430f9322a7d8772f7aed33aa0d59610; _gid=GA1.2.175327337.1622427810; _sl=1; external_referer=padhuUp37zj9xuUOXCNFvGXUXmFWu3h9RbvCou2th62t8qpRtR3BhPixmmJ9DJd0|0|8e8t2xd8A2w%3D; kdt=0d9s7iKweiBfuhDUa53uXwdagFfNqClTwX71J8aS; auth_token=948467ce41edd946051df9597411ed0d3290f573; ct0=8a644c92873b25719489af4e8d5937d657cf2e1606c4858d110e77358ceaa011ea751b7bdc5aff4423d9d909cce2b6d0a480038e0e1594805a3b70f180a5d4990d20c9e7a2b35808759d2524868923b8; twid=u%3D1399229100502360070; at_check=true; mbox=session#8c9772f3d8624b1dac0c7f067989d1b8#1622439901|PC#8c9772f3d8624b1dac0c7f067989d1b8.38_0#1685682841; cd_user_id=179c0d7da57fc-0beb21182ca819-3b7c0a50-100200-179c0d7da5847b; lang=vi',
}

params = (
	('variables', '{"screen_name":"eminem","withHighlightedLabel":true}'),
)


def abc(name):
	return (('variables', '{"screen_name":"{}","withHighlightedLabel":true}').__format__(name),)


screen_name = ['Eminem', 'RaoulGMI', 'RaoulGMI', 'RealVisionBot', 'KennethDredd']


def param(name):
	return tuple("('variables','" + '{"screen_name":' + "{}".format(name) + ', "withHighlightedLabel":true}' + "'),")
	# return ('variables','" + '{"screen_name":' + "{name_}".format(name_=name) + ', "withHighlightedLabel":true}' + "'),"
	# return '("variables", "{"screen_name":f'{name}',"withHighlightedLabel":true}")'


response = requests.get('https://twitter.com/i/api/graphql/Vf8si2dfZ1zmah8ePYPjDQ/UserByScreenNameWithoutResults',
						headers=headers, params=param("eminem"))

# NB. Original query string below. It seems impossible to parse and
# reproduce query strings 100% accurately so the one below is given
# in case the reproduced version is not "correct".
# response = requests.get('https://twitter.com/i/api/graphql/Vf8si2dfZ1zmah8ePYPjDQ/UserByScreenNameWithoutResults?variables=%7B%22screen_name%22%3A%22eminem%22%2C%22withHighlightedLabel%22%3Atrue%7D', headers=headers)

# print(response.json())
print(type(params))
# print(type(abc("abc")))
print(type(param("eminem")))
