import pymongo
import re, json, logging
import urllib.parse
from urllib.parse import quote
from pprint import pprint
from datetime import datetime

from pymongo.errors import ServerSelectionTimeoutError
from scrapy import http
from scrapy.spiders import CrawlSpider
from scrapy.shell import inspect_response
from scrapy.core.downloader.middleware import DownloaderMiddlewareManager
from scrapy_selenium import SeleniumRequest, SeleniumMiddleware

from TweetScraper.items import Tweet, User


logger = logging.getLogger(__name__)


class TweetScraper(CrawlSpider):
    name = 'TweetScraper'
    allowed_domains = ['twitter.com']

    def __init__(self, query=''):
        self.mongoClient = pymongo.MongoClient("mongodb://root:password@localhost:27017/")
        self.myDatabase = self.mongoClient["twitterdata"]
        self.trackUser = self.myDatabase['trackUser']
        self.followUser = self.myDatabase['followUser']
        self.date = datetime.now()
        self.non_exist_users = []
        try:
            info = self.mongoClient.server_info()  # Forces a call.
            # print("info: ", info)
        except ServerSelectionTimeoutError:
            print("server is down.")

        self.url = (
            'https://twitter.com/i/api/graphql/Vf8si2dfZ1zmah8ePYPjDQ/UserByScreenNameWithoutResults?'
        )
        self.url = self.url + 'variables=%7B%22screen_name%22%3A%22{query}%22%2C%22withHighlightedLabel%22%3Atrue%7D'
        self.query = query
        self.num_search_issued = 0
        # regex for finding next cursor
        self.cursor_re = re.compile('"(scroll:[^"]*)"')

    # def encode(self, enToDe):
    #     return urllib.parse.quote_plus(enToDe)

    def enToDe(self, query):
        query_decode = f'{"screen_name":{query},"withHighlightedLabel":true}'
        return urllib.parse.quote_plus(query_decode)

    def start_requests(self):
        """
        Use the landing page to get cookies first
        """
        yield SeleniumRequest(url="https://twitter.com/explore", callback=self.parse_home_page)

    def parse_home_page(self, response):
        """
        Use the landing page to get cookies first
        """
        # inspect_response(response, self)
        self.update_cookies(response)
        for r in self.start_query_request():
            yield r


    def update_cookies(self, response):
        driver = response.meta['driver']
        try:
            self.cookies = driver.get_cookies()
            self.x_guest_token = driver.get_cookie('gt')['value']
            # self.x_csrf_token = driver.get_cookie('ct0')['value']
        except:
            logger.info('cookies are not updated!')

        self.headers = {
            'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            'x-guest-token': self.x_guest_token,
            # 'x-csrf-token': self.x_csrf_token,
        }
        print('token:______________________________________________________')
        print(self.x_guest_token)
        print('\n______________________________________________________\n')
        print('headers:\n--------------------------\n')
        print(self.headers)
        print('\n--------------------------\n')

    def start_query_request(self, cursor=None):
        """
        Generate the search request
        """
        if cursor:
            url = self.url + '&cursor={cursor}'
            url = url.format(query=quote(self.query), cursor=quote(cursor))
        else:
            url = self.url.format(query=quote(self.query))
        request = http.Request(url, callback=self.parse_result_page, cookies=self.cookies, headers=self.headers)
        yield request

        self.num_search_issued += 1
        if self.num_search_issued % 100 == 0:
            # get new SeleniumMiddleware            
            for m in self.crawler.engine.downloader.middleware.middlewares:
                if isinstance(m, SeleniumMiddleware):
                    m.spider_closed()
            self.crawler.engine.downloader.middleware = DownloaderMiddlewareManager.from_crawler(self.crawler)
            # update cookies
            # yield SeleniumRequest(url="https://twitter.com/explore", callback=self.update_cookies, dont_filter=True)
            yield SeleniumRequest(url="https://twitter.com/{query}", callback=self.update_cookies, dont_filter=True)

    def sample_data(self, data):
        print("self.query: ", self.query)

        try:
            legacy = data['data']['user']['legacy']
            rest_id = data['data']['user']['rest_id']
            my_dict = [
                {"rest_id": rest_id,
                 "screen_name": self.query,
                 "crawlTime": self.date.isoformat(),
                 "followers_count": legacy['followers_count'],
                 "friends_count": legacy['friends_count'],
                 "favourites_count": legacy['favourites_count'],
                 "fast_followers_count": legacy['fast_followers_count'],
                 "listed_count": legacy['listed_count'],
                 "media_count": legacy['media_count'],
                 "normal_followers_count": legacy['normal_followers_count'],
                 "statuses_count": legacy['statuses_count'],
                 "verified": legacy['verified'],
                 "legacy": legacy
                 }
            ]
            return my_dict
        except NameError:
            print(NameError, "Name Error; " + self.query)

    def parse_result_page(self, response):
        """
        Get the tweets & users & next request
        """
        # inspect_response(response, self)

        # handle current page
        data = json.loads(response.text)
        if not data['data']:
            self.non_exist_users.append(self.query)
            nonExistUsers = self.myDatabase['nonExistUsers']
            nonExistUsers.insert_one({
                "createdAt": self.date.isoformat(),
                "screen_name": self.query})
            self.followUser.delete_one({"screen_name": self.query})
            print(f'Removed: {self.query}\n--------------------------')
        else:
            print(f"importing {self.query} to trackUser table...")
            if self.save_many_to_track_user(self.sample_data(data)):
                print('\033[92m' + 'Import Success!' + '\033[0m')
            else:
                print('\033[93m' + 'Import Fail' + '\033[0m')
        print(self.non_exist_users)

    def parse_tweet_item(self, items):
        for k, v in items.items():
            # assert k == v['id_str'], (k,v)
            tweet = Tweet()
            tweet['id_'] = k
            tweet['raw_data'] = v
            yield tweet


    def parse_user_item(self, items):
        for k,v in items.items():
            # assert k == v['id_str'], (k,v)
            user = User()
            user['id_'] = k
            user['raw_data'] = v
            yield user

    def save_one_to_track_user(self, item):
        x = self.trackUser.insert_one(item)
        return x

    def save_many_to_track_user(self, items):
        return self.trackUser.insert_many(items)

# I asking my
# what is yield, understand Generators <= Iterables
# create new table and insert users from the User table: id, screen_name
# python call command follow user table
# handle 10 users firstly
# after that handle 1000<split to small 100, 100, 100,...>
#
