import time
import codecs
import json
import re
import pymongo
import html
from datetime import datetime
from w3lib.html import remove_tags
from . import utils
from time import sleep
color = utils.colors_mark()
mongoClient = pymongo.MongoClient("mongodb://root:password@localhost:27017/")


def sample_data():
    data = {
        'id': '',  # id
        'title': '',  # postTranslate/title
        'subtitle': '',  # leadText
        'link_img': '',  # postTranslate/avatar
        'link_website_logo': '',
        'views': '',  # views
        'id_post_translate': '',  # postTranslate/id
        'description': '',  # postTranslate/leadText
        'slug_content': '',  # slug
        'link_content': '',  # https://cointelegraph.com/news/ + slug
        'raw_content': '',
        'keyword_ranking': {},
        'author': '',  # author/authorTranslates/name
        'id_author': '',  # author/authorTranslates/id
        'link_author': '',  # https://cointelegraph.com/authors/ + slug_author
        'slug_author': '',  # author/slug
        'tag': '',
        'link_tag': '',
        'published': '',  # postTranslate/published
        'date': '',
        'timestamp': '',
        'latest': 0,
        'approve': 1,
    }
    return data


class CardanoscraperPipeline(object):
    def __init__(self):
        self.myDatabase = mongoClient["cardanoNews"]
        self.postContents = self.myDatabase['allNews']
        # self.postContents = self.myDatabase['allNews1']
        self.testCarda = self.myDatabase['testAllNews2']
        self.link_website_logo = 'https://sjc3.discourse-cdn.com/business4/user_avatar/forum.cardano.org/cardano-foundation/45/22471_2.png'
        self.new_posts = []

    # ================================================
    # handle put data to GraphQl
    # ================================================
    def close_spider(self, spider):
        for index, value in enumerate(self.new_posts):
            utils.show_message(message='Latest Post for today', colour='okblue', data={index: value})
        print(f"{color['warning']}Cardano Crawl Completed!{color['endc']}")

    # call every item pipeline component
    def process_item(self, item, spider):
        print(f"\n{color['okblue']}Cardano Pipeline handling...{color['endc']}")
        # ================================================
        # we have two flows of data
        # 1st for posts, 2nd for contents
        # if run crawlAllCardanoNews, insert data into allNews table
        # ================================================
        if item['source'] == 'cardano':
            if 'title' in item:
                item['avatars'] = self.handle_link_avatars(item['avatars'])
                if self.postContents.find_one({'link_post': item['link_post']}):
                    self.update_table(self.postContents, item)
                else:
                    # item['link_website_logo'] = self.link_website_logo
                    utils.insert_into_table(self.postContents, item)
                    self.new_posts.append(item['link_post'])
            elif 'raw_content' in item:
                utils.handle_datetime(item, item['post_time'])
                utils.text_ranking(item, item['raw_content'])
                self.update_raw_content(self.postContents, item)
                print(f"{color['warning']}Imported raw_content to {utils.get_table(self.postContents)} {color['endc']}\n")
        # print(f"{color['warning']}This is{color['endc']}Item...{color['okgreen']}{item}{color['endc']}")
        return item

    def update_table(self, table, data):
        query = {
            "link_post": data['link_post'].strip(),
        }
        if table.update_one(query, {'$set': data}):
            # print(f"{color['okcyan']}Updating Latest Cardano page into {get_table(table)}{color['endc']} ")
            utils.update_success_notify(table)
        time.sleep(1)

    def update_raw_content(self, table, data):
        query = {
            "link_post": data['link_content'].strip()
        }
        if table.update_one(query, {'$set': data}):
            # print(f"{color['okcyan']}Updating Raw Content into {get_table(table)}{color['endc']} for post: {data['link_content']}")
            utils.update_rawcontent_notify(table, data)
        time.sleep(1)

    def handle_link_avatars(self, links):
        new_links = []
        parent = 'https://sjc3.discourse-cdn.com/business4'
        for link in links:
            if "https:" not in link:
                new_links.append(parent + link)
            else:
                pass
        return new_links


class IohkScraperPipeline(object):
    def __init__(self):
        self.myDatabase = mongoClient["cardanoNews"]
        self.iohk_sample1 = self.myDatabase['iohkSample']
        # self.iohk_sample1 = self.myDatabase['iohkSample2']
        self.link_website_logo = 'https://ucarecdn.com/a3d997dc-1781-445f-ad59-ad0e58c24cf3/-/resize/200/-/format/webp/-/quality/best/-/progressive/yes/'
        self.new_posts = []

    def close_spider(self, spider):
        for index, value in enumerate(self.new_posts):
            utils.show_message(message='Latest Post for today', colour='okblue', data={index: value})
        print(f"{color['warning']}IOHK Crawl Completed!{color['endc']}")

    def process_item(self, item, spider):
        print(f"\n{color['okblue']}IOHK Pipeline handling...{color['endc']}\n")
        if item['source'] == 'iohk':
            self.iohk_get_posts(item)
        return item

    def iohk_get_posts(self, data):
        content = data['result']['pageContext']
        profile_url = "https://iohk.io/en{}page-1/"
        iohk_url = "https://iohk.io/en/blog/posts/page-{}/"
        content_url = "https://iohk.io/en{}"
        posts = content['posts']
        recent_posts = content['recentPosts']
        total_pages = content['total_pages']
        current_page = content['current_page']
        sidebar_post_filter = content['filters']
        # current_url_page = iohk_url.format(content['crumbs'][0]['path'])
        # get all posts through all pages: 44 current pages
        for post in posts:
            iohk_all_posts = utils.initialize_sample_data()
            author_info = post['author']
            iohk_all_posts['publish_date'] = post['publish_date']
            iohk_all_posts['timestamp'] = utils.handle_datetime(iohk_all_posts, post['publish_date']),
            iohk_all_posts['author_title'] = author_info['title']
            iohk_all_posts['author_display_name'] = author_info['display_name']
            iohk_all_posts['author_thumbnail'] = author_info['thumbnail']
            iohk_all_posts['author_job_titles'] = author_info['job_titles']
            iohk_all_posts['author_profile_links'] = author_info['profile_links']  # all social links of the author
            iohk_all_posts['post_main_img'] = post['main_image']
            # iohk_all_posts['link_website_logo'] = self.link_website_logo
            iohk_all_posts['lang'] = post['lang']
            iohk_all_posts['title'] = post['title'].strip()
            iohk_all_posts['slug'] = post['slug']
            iohk_all_posts['subtitle'] = post['subtitle']
            iohk_all_posts['audio'] = post['audio']
            iohk_all_posts['soundcloud'] = post['soundcloud']
            iohk_all_posts['raw_content'] = post['body_content']
            # iohk_all_posts['recent_posts'] = recent_posts
            iohk_all_posts['total_pages'] = total_pages
            # iohk_all_posts['filters'] = sidebar_post_filter
            iohk_all_posts['current_page'] = current_page
            iohk_all_posts['current_url_page'] = iohk_url.format(current_page)
            iohk_all_posts['link_content'] = content_url.format(post['url'])
            iohk_all_posts['author_profile_url'] = profile_url.format(author_info['profile_url'])

            keyword_ranking = utils.text_ranking(iohk_all_posts, iohk_all_posts['raw_content'])

            print(f"Current page: {iohk_all_posts['current_url_page']}")
            print(f"Current post: {iohk_all_posts['title']}")
            iohk_all_posts['raw_data'] = post
            iohk_all_posts['keyword_ranking'] = keyword_ranking
            if self.iohk_sample1.find_one({'link_content': iohk_all_posts['link_content']}):
                self.update_iohk(self.iohk_sample1, iohk_all_posts)
                sleep(.05)
            else:
                utils.insert_into_table(self.iohk_sample1, iohk_all_posts)
                self.new_posts.append(iohk_all_posts['link_content'])
                sleep(.05)

    def update_iohk(self, table, data):
        query = {
            'link_content': data['link_content'].strip()
        }
        if table.update_one(query, {'$set': data}):
            # print(f"{color['okcyan']}Updating {get_table(table)} table{color['endc']}\n")
            utils.update_success_notify(table)
        time.sleep(.05)


class CoindeskScraperPipeline(object):
    def __init__(self):
        self.myDatabase = mongoClient['cardanoNews']
        self.coindesk = self.myDatabase['coindeskSample']
        # self.coindesk = self.myDatabase['coindeskLatest1']
        self.link_website_logo = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxNzMgMzMiPjxzdHlsZT4uc3Qwe2ZpbGw6I2YzYmIyZH0uc3Qxe2ZpbGw6I2ZmZn08L3N0eWxlPjxwYXRoIGNsYXNzPSJzdDAiIGQ9Ik0xNC44IDE2LjZjMCAuOS43IDEuNiAxLjYgMS42LjkgMCAxLjYtLjcgMS42LTEuNiAwLS45LS43LTEuNi0xLjYtMS42LS45IDAtMS42LjctMS42IDEuNk0yOC4zIDE1Yy0uOSAwLTEuNi43LTEuNiAxLjYgMCAuOS43IDEuNiAxLjYgMS42LjkgMCAxLjYtLjcgMS42LTEuNiAwLS45LS43LTEuNi0xLjYtMS42TTI4LjMgMjcuMWMtLjkgMC0xLjYuNy0xLjYgMS42IDAgLjkuNyAxLjYgMS42IDEuNi45IDAgMS42LS43IDEuNi0xLjYgMC0uOS0uNy0xLjYtMS42LTEuNiIvPjxwYXRoIGNsYXNzPSJzdDAiIGQ9Ik0zMS43IDEuN2MtMS42LTItNC41LTIuMS02LjItLjVsLS4yLjItLjQuM2MtMS42IDEuMy00IDEuMi01LjUtLjN2LS4xQzE4LjkuOCAxOC4yLjQgMTcuNS4yYy0uMSAwLS4zLS4xLS40LS4xSDE1LjVjLS4xIDAtLjIgMC0uMy4xSDE1Yy0uMSAwLS4yLjEtLjMuMSAwIDAtLjEgMC0uMS4xLS4xIDAtLjIuMS0uMy4xIDAgMC0uMSAwLS4xLjEtLjEuMS0uMi4xLS4zLjIgMCAwLS4xIDAtLjEuMS0uMS4xLS4yLjEtLjMuMmwtLjEuMS0uMi4yLS40LjNjLTEuNiAxLjMtNCAxLjItNS40LS4zIDAgMC0uMSAwLS4xLS4xbC0uMi0uMkM2LjUuNiA1LjguMiA1IC4xaC0uNC0xLjMtLjFjMCAuMS0uMS4xLS4yLjJoLS4xYy0uNS4yLTEgLjQtMS40LjhsLS4xLjEtLjMuM2MtLjQuNC0uNi45LS44IDEuMyAwIC4xLS4xLjItLjEuMyAwIC4xLS4xLjItLjEuNC0uMS43LS4xIDEuNC4xIDIuMSAwIC4xLjEuMi4xLjNWNmMwIC4xLjEuMi4xLjMuMS4xLjEuMi4yLjQuMi4xLjQuMy41LjRsLjIuMi4yLjJDMyA5IDMgMTEuNiAxLjQgMTMuMmMtLjIuMi0uNS41LS42LjctLjEuMS0uMS4yLS4yLjR2LjFjLS4xLjEtLjEuMi0uMi4zdi4xYzAgLjEtLjEuMi0uMS4zdi4xYzAgLjEgMCAuMi0uMS4zVjE3YzAgLjEgMCAuMi4xLjN2LjFjLjIuNy42IDEuNCAxLjIgMiAxLjYgMS42IDEuNiA0LjIgMCA1LjhsLS4xLjEtLjIuMnYuMWMtLjEuMS0uMi4yLS4yLjMgMCAwIDAgLjEtLjEuMS0uMS4xLS4xLjItLjIuM2wtLjEuMWMwIC4xLS4xLjEtLjEuMnMtLjEuMS0uMS4yIDAgLjEtLjEuMmMtLjIuNC0uMy45LS4zIDEuM1YyOS4xYy4xLjMuMS42LjMuOCAwIC4xLjEuMi4xLjJzMCAuMS4xLjFjMCAuMS4xLjIuMS4zIDAgMCAwIC4xLjEuMS4xLjIuMi4zLjMuNCAwIDAgMCAuMS4xLjEgMCAwIDAgLjEuMS4xIDAgLjEuMS4xLjEuMWwuMS4xYy4xLjEuMi4xLjIuMmwuMS4xcy4xIDAgLjEuMWMuMS4xLjIuMi4zLjIgMCAwIC4xIDAgLjEuMS4xLjEuMi4xLjMuMmguMWMuMS4xLjIuMS40LjEuMSAwIC4zLjEuNC4xaC4xYy4xIDAgLjIgMCAuMy4xaC45Yy4zIDAgLjUtLjEuOC0uMWguMWMuMSAwIC4yLS4xLjMtLjFINmMuMSAwIC4yLS4xLjMtLjFoLjFjLjItLjEuNS0uMy43LS40bC4zLS4zLjEtLjFjMS42LTEuNyA0LjItMS43IDUuOCAwIDEuOCAxLjkgNC44IDEuOCA2LjUtLjMgMS4yLTEuNSAxLjItMy43IDAtNS4zLTEuNi0yLTQuNS0yLjEtNi4yLS41bC0uMi4yLS40LjNjLTEuNiAxLjMtNCAxLjItNS41LS4zbC0uMi0uMkw3IDI1Yy0xLjMtMS42LTEuMi00IC4zLTUuNS45LS44IDEuMy0xLjkgMS4zLTN2LS4yLS4xYzAtMS0uNC0yLTEuMi0yLjcgMC0uMS0uMS0uMS0uMS0uMmwtLjMtLjRjLTEuMy0xLjYtMS4yLTQgLjMtNS41bC4xLS4xLjEtLjFjMS42LTEuNyA0LjItMS43IDUuOCAwbC4xLjEuMS4xLjIuMmMuMSAwIC4xLjEuMi4xcy4xLjEuMi4xLjEuMS4yLjEuMS4xLjIuMS4xLjEuMi4xLjEuMS4yLjEuMSAwIC4yLjFjLjEgMCAuMSAwIC4yLjFIMTdjLjEgMCAuMiAwIC4zLS4xaC4yYy4xIDAgLjItLjEuMy0uMWguMWMuMSAwIC4yLS4xLjQtLjIuNC0uMi44LS41IDEuMS0uOGwuMS0uMWMxLjYtMS43IDQuMi0xLjcgNS44IDAgMS43IDIgNC44IDEuOSA2LjQtLjIgMS4yLTEuNSAxLjItMy43IDAtNS4yIi8+PHBhdGggY2xhc3M9InN0MSIgZD0iTTU0LjUgMTQuMWMtLjYtLjYtMS4xLTEtMS44LTEuMy0uNi0uMy0xLjMtLjUtMi4yLS41LS44IDAtMS42LjItMi4yLjUtLjYuMy0xLjEuNy0xLjUgMS4zLS40LjUtLjcgMS4xLS45IDEuOC0uMi43LS4zIDEuNC0uMyAyLjEgMCAuNy4xIDEuNC40IDIuMS4yLjcuNiAxLjIgMSAxLjdzMSAuOSAxLjYgMS4yYy42LjMgMS4zLjQgMi4xLjQuOSAwIDEuNi0uMiAyLjItLjUuNi0uMyAxLjItLjcgMS43LTEuM2wyLjEgMi4yYy0uOC45LTEuNyAxLjUtMi43IDEuOS0xIC40LTIuMS42LTMuMy42LTEuMiAwLTIuNC0uMi0zLjQtLjYtMS0uNC0xLjktMS0yLjYtMS43LS43LS43LTEuMy0xLjYtMS43LTIuNi0uNC0xLS42LTIuMi0uNi0zLjQgMC0xLjIuMi0yLjQuNi0zLjQuNC0xIDEtMS45IDEuNy0yLjcuNy0uNyAxLjYtMS4zIDIuNi0xLjcgMS0uNCAyLjItLjYgMy40LS42IDEuMiAwIDIuMy4yIDMuMy42IDEuMS40IDIgMS4xIDIuOCAxLjlsLTIuMyAyTTYxLjMgMTcuOGMwIC44LjEgMS42LjQgMi4yLjIuNy42IDEuMyAxIDEuOHMxIC45IDEuNiAxLjFjLjYuMyAxLjQuNCAyLjIuNC44IDAgMS41LS4xIDIuMi0uNC42LS4zIDEuMi0uNyAxLjYtMS4xLjQtLjUuOC0xLjEgMS0xLjguMi0uNy40LTEuNC40LTIuMiAwLS44LS4xLTEuNi0uNC0yLjItLjItLjctLjYtMS4zLTEtMS44cy0xLS45LTEuNi0xLjFjLS42LS4zLTEuNC0uNC0yLjItLjQtLjggMC0xLjUuMS0yLjIuNC0uNi4zLTEuMi43LTEuNiAxLjEtLjQuNS0uOCAxLjEtMSAxLjgtLjIuNy0uNCAxLjQtLjQgMi4yem0tMy4yIDBjMC0xLjIuMi0yLjMuNi0zLjMuNC0xIDEtMS45IDEuOC0yLjcuOC0uOCAxLjYtMS40IDIuNy0xLjggMS0uNCAyLjEtLjcgMy4zLS43IDEuMiAwIDIuMy4yIDMuMy43IDEgLjQgMS45IDEgMi43IDEuOC44LjggMS4zIDEuNyAxLjggMi43LjQgMSAuNiAyLjEuNiAzLjMgMCAxLjItLjIgMi4zLS42IDMuMy0uNCAxLTEgMS45LTEuOCAyLjctLjguOC0xLjYgMS4zLTIuNyAxLjgtMSAuNC0yLjEuNy0zLjMuNy0xLjIgMC0yLjMtLjItMy4zLS43LTEtLjQtMS45LTEtMi43LTEuOC0uOC0uOC0xLjMtMS42LTEuOC0yLjctLjMtMS0uNi0yLjEtLjYtMy4zek03OCAyNS45aDN2LTE2aC0zdjE2em0tLjctMjEuOGMwLS42LjItMS4xLjYtMS42LjQtLjQuOS0uNyAxLjUtLjdzMS4xLjIgMS41LjdjLjQuNC42IDEgLjYgMS42IDAgLjYtLjIgMS4xLS42IDEuNi0uNC40LS45LjctMS41LjdzLTEuMS0uMi0xLjUtLjdjLS40LS40LS42LTEtLjYtMS42ek04NS4yIDkuOWgzdjIuNWguMWMuNC0uOSAxLTEuNiAyLTIuMS45LS41IDItLjggMy4zLS44LjggMCAxLjUuMSAyLjIuNC43LjIgMS4zLjYgMS44IDEuMS41LjUuOSAxLjEgMS4zIDEuOS4zLjguNSAxLjcuNSAyLjhWMjZoLTN2LTkuNWMwLS43LS4xLTEuNC0uMy0xLjktLjItLjUtLjUtMS0uOC0xLjMtLjMtLjMtLjctLjYtMS4yLS43LS40LS4xLS45LS4yLTEuNC0uMi0uNiAwLTEuMi4xLTEuNy4zLS41LjItMSAuNS0xLjQgMS0uNC40LS43IDEtLjkgMS43LS4yLjctLjMgMS41LS4zIDIuNHY4LjNoLTNWOS45TTExMC41IDIzLjRjLjggMCAxLjUtLjEgMi4yLS40LjctLjMgMS4yLS43IDEuNy0xLjIuNC0uNS44LTEuMSAxLTEuOC4yLS43LjQtMS40LjQtMi4zIDAtLjgtLjEtMS42LS40LTIuMy0uMi0uNy0uNi0xLjMtMS0xLjgtLjUtLjUtMS0uOS0xLjctMS4yLS43LS4zLTEuNC0uNC0yLjItLjQtLjggMC0xLjUuMS0yLjIuNC0uNy4zLTEuMi43LTEuNyAxLjItLjQuNS0uOCAxLjEtMSAxLjgtLjIuNy0uNCAxLjQtLjQgMi4zIDAgLjguMSAxLjYuNCAyLjMuMi43LjYgMS4zIDEgMS44czEgLjkgMS43IDEuMmMuNi4yIDEuNC40IDIuMi40em04LjMgMi40aC0zdi0yLjNoLS4xYy0uNi45LTEuNCAxLjUtMi40IDJzLTIuMS43LTMuMi43Yy0xLjIgMC0yLjQtLjItMy40LS42LTEtLjQtMS45LTEtMi42LTEuOC0uNy0uOC0xLjMtMS43LTEuNi0yLjctLjQtMS0uNi0yLjEtLjYtMy4zIDAtMS4yLjItMi4zLjYtMy40LjQtMSAuOS0xLjkgMS42LTIuNy43LS44IDEuNi0xLjQgMi42LTEuOCAxLS40IDIuMS0uNiAzLjQtLjYgMS4xIDAgMi4yLjIgMy4yLjcgMSAuNSAxLjggMS4yIDIuMyAyaC4xVjBoM3YyNS44ek0xMzQuMSAxNi41YzAtLjctLjEtMS4zLS4zLTEuOS0uMi0uNi0uNS0xLjEtLjktMS41LS40LS40LS45LS43LTEuNC0xLS42LS4yLTEuMi0uNC0yLS40LS43IDAtMS40LjEtMiAuNC0uNi4zLTEuMS42LTEuNiAxLjEtLjQuNC0uOC45LTEgMS41LS4yLjYtLjQgMS4xLS40IDEuNmg5LjZ6bS05LjYgMi41YzAgLjcuMiAxLjMuNSAxLjkuMy42LjcgMS4xIDEuMiAxLjUuNS40IDEuMS43IDEuNy45LjcuMiAxLjMuMyAyIC4zLjkgMCAxLjgtLjIgMi41LS43LjctLjQgMS4zLTEgMS45LTEuN2wyLjMgMS44Yy0xLjcgMi4yLTQuMSAzLjMtNy4xIDMuMy0xLjMgMC0yLjQtLjItMy40LS42LTEtLjQtMS45LTEtMi42LTEuOC0uNy0uOC0xLjMtMS42LTEuNi0yLjctLjQtMS0uNi0yLjEtLjYtMy4zIDAtMS4yLjItMi4zLjYtMy4zLjQtMSAxLTEuOSAxLjctMi43LjctLjggMS42LTEuMyAyLjYtMS44IDEtLjQgMi4xLS42IDMuMy0uNiAxLjQgMCAyLjYuMiAzLjYuNyAxIC41IDEuOCAxLjEgMi40IDEuOS42LjggMS4xIDEuNyAxLjQgMi43LjMgMSAuNCAyIC40IDMuMVYxOWgtMTIuOHpNMTQ5LjEgMTMuOWMtLjQtLjQtLjgtLjgtMS4zLTEuMS0uNS0uMy0xLjItLjUtMS45LS41cy0xLjMuMi0xLjkuNWMtLjUuMy0uOC43LS44IDEuMyAwIC41LjIuOS41IDEuMS4zLjMuNy41IDEuMS43LjQuMi45LjMgMS4zLjQuNS4xLjkuMiAxLjIuMi42LjIgMS4zLjMgMS44LjYuNi4yIDEuMS41IDEuNS45LjQuNC43LjggMSAxLjMuMi41LjQgMS4xLjQgMS45IDAgLjktLjIgMS43LS42IDIuMy0uNC42LS45IDEuMi0xLjUgMS42LS42LjQtMS4zLjctMi4xLjktLjguMi0xLjYuMy0yLjMuMy0xLjMgMC0yLjUtLjItMy41LS42LTEtLjQtMS45LTEuMS0yLjctMi4ybDIuMy0xLjljLjUuNSAxIC45IDEuNiAxLjMuNi40IDEuMy42IDIuMi42LjQgMCAuOCAwIDEuMi0uMS40LS4xLjctLjIgMS0uNC4zLS4yLjUtLjQuNy0uNi4yLS4zLjMtLjYuMy0uOSAwLS40LS4xLS44LS40LTEuMS0uMy0uMy0uNi0uNS0xLS43LS40LS4yLS44LS4zLTEuMi0uNGwtMS4yLS4zYy0uNi0uMi0xLjMtLjMtMS44LS41LS42LS4yLTEuMS0uNS0xLjUtLjgtLjQtLjMtLjgtLjgtMS4xLTEuMy0uMy0uNS0uNC0xLjItLjQtMS45IDAtLjguMi0xLjYuNS0yLjIuMy0uNi44LTEuMSAxLjQtMS41LjYtLjQgMS4yLS43IDEuOS0uOS43LS4yIDEuNS0uMyAyLjItLjMgMS4xIDAgMi4xLjIgMy4xLjYgMSAuNCAxLjggMS4xIDIuNCAybC0yLjQgMS43TTE1NC45LjRoM3YxNi4ybDYuOC02LjhoNC4xbC03LjMgNy4yIDggOC42aC00LjNsLTcuMy04LjJ2OC4yaC0zVi40Ii8+PC9zdmc+"
        self.url = 'https://www.coindesk.com{}'
        self.new_posts = []

    def close_spider(self, spider):
        utils.handle_empty_content(self.coindesk, self.new_posts)
        print(f"{color['warning']}Coindesk Crawl Completed!{color['endc']}")

    # ================================================
    # classify flow of data and push data to mongoDb
    # ================================================
    def process_item(self, item, spider):
        print(f"{color['okblue']}Coindesk Pipeline handling...{color['endc']}\n")
        if item['source'] == 'coindesk':
            if 'title' in item:
                self.handle_links(item)
                utils.handle_datetime(item, item['date'])
                if self.coindesk.find_one({'link_content': item['link_content']}):
                    self.update_table(self.coindesk, item)
                else:
                    utils.insert_into_table(self.coindesk, item)
                    utils.show_message('Post', 'okblue', item['link_content'])
                    self.new_posts.append(item['link_content'])
            elif 'raw_data' in item:
                # utils.show_message('raw_data', 'fail', item['slug_content'])
                self.insert_raw_content(self.coindesk, item)
        elif item['source'] == 'coindeskLatestNews':
            if 'next' in item:
                self.coindesk_get_post(item)
            elif 'raw_content' in item:
                self.coindesk_get_raw_content(self.coindesk, data=item)
        return item

    def update_table(self, table, data):
        query = {
            'link_content': data['link_content']
        }
        if table.update_one(query, {'$set': data}):
            utils.update_success_notify(table)
        time.sleep(1)

    def insert_raw_content(self, table, data):
        slug_content = data['slug_content']
        # many kinds of public post date
        self.handle_datetime(data)
        # some Video post had no content
        self.handle_content(data)
        data['raw_data'] = ''
        query = {
            "slug_content": slug_content,
        }
        if table.update_one(query, {'$set': data}):
            print(f"{color['okgreen']}Update raw_content success!{color['endc']} in {self.url.format('/' + str(slug_content)) }")
        time.sleep(1)

    def update_latest_news(self, table, data):
        query = {
            'slug_content': data['slug_content']
        }
        if table.update_one(query, {'$set': data}):
            utils.update_success_notify(table)

    def coindesk_get_post(self, data):
        posts = data['posts']
        for post in posts:
            coindesk_sample_data = sample_data()
            img = post['images']['images']
            coindesk_sample_data['title'] = post['title']
            coindesk_sample_data['subtitle'] = post['text']
            if 'desktop' in img:
                coindesk_sample_data['link_img'] = img['desktop']['src']
            elif 'mobile' in img:
                coindesk_sample_data['link_img'] = img['mobile']['src']
            elif 'mobile@2x' in img:
                coindesk_sample_data['link_img'] = img['mobile@2x']['src']
            elif 'mobile@3x' in img:
                coindesk_sample_data['link_img'] = img['mobile@3x']['src']
            elif 'full' in img:
                coindesk_sample_data['link_img'] = img['full']['src']
            else:
                coindesk_sample_data['link_img'] = ''
            # coindesk_sample_data['link_website_logo'] = "website logo"
            coindesk_sample_data['slug_content'] = post['slug']
            coindesk_sample_data['link_content'] = self.url.format('/' + str(post['slug']))
            coindesk_sample_data['author'] = post['authors'][0]['name']
            coindesk_sample_data['slug_author'] = post['authors'][0]['slug']
            coindesk_sample_data['link_author'] = self.url.format('/author/' + str(post['authors'][0]['slug']))
            coindesk_sample_data['tag'] = post['tag']['name']
            coindesk_sample_data['link_tag'] = self.url.format('/' + str(post['tag']['slug']))
            coindesk_sample_data['published'] = post['date']
            coindesk_sample_data['timestamp'] = datetime.strptime(post['date'], '%Y-%m-%dT%H:%M:%S').timestamp()
            if self.coindesk.find_one({'slug_content': coindesk_sample_data['slug_content']}):
                self.update_latest_news(self.coindesk, coindesk_sample_data)
                time.sleep(.05)
            else:
                utils.insert_into_table(self.coindesk, data=coindesk_sample_data)
                self.new_posts.append(coindesk_sample_data['link_content'])
                time.sleep(.05)

    def coindesk_get_raw_content(self, table, data):
        raw_content = data['raw_content']
        data['clean_content'] = utils.clean_html_tags(data['raw_content'])
        utils.show_message('raw_content', 'okgreen', raw_content)
        keyword_ranking = utils.text_ranking(data, raw_content)
        data['keyword_ranking'] = keyword_ranking
        data['raw_data'] = ''
        if table.find_one({'slug_content': data['slug_content']}):
            self.update_latest_news(self.coindesk, data=data)
        sleep(.05)

    def standard_date(self, date, data):
        standard_date = data[date].split(':')[:2]
        standard_date = ':'.join(standard_date)
        return standard_date

    def handle_content(self, data):
        data['raw_content'] = utils.decode_html_content(data['raw_content'])
        data['clean_content'] = utils.clean_html_tags(data['raw_content'])
        data['keyword_ranking'] = utils.text_ranking(data, data['raw_content'])
        utils.show_message('keywords', 'warning', data['keyword_ranking'])

    def handle_datetime(self, data):
        data['timestamp'] = datetime.strptime(str(data['date']), "%Y-%m-%dT%H:%M:%S").timestamp()

    def handle_links(self, data):
        data['link_content'] = self.url.format(str(data['link_content']))
        data['link_tag'] = self.url.format(str(data['link_tag']))
        data['link_author'] = self.url.format(str(data['link_author']))


class CoinTelegraphScraperPipeline(object):
    def __init__(self):
        self.url = 'https://cointelegraph.com/{}'
        self.myDatabase = mongoClient['cardanoNews']
        self.coinTele = self.myDatabase['coinTelegraphSample']
        # self.coinTele = self.myDatabase['coinTelegraphLatestTest']
        self.link_website_logo = "data:image/jpeg;base64,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"
        self.new_posts = []

    def close_spider(self, spider):
        utils.handle_empty_content(self.coinTele, self.new_posts)
        print(f"{color['warning']}CoinTelegraph Crawl Completed!{color['endc']}")

    def process_item(self, item, spider):
        if item['source'] == 'coinTelegraph':
            if 'title' in item:
                print(f"{color['okblue']}Cointelegraph Pipeline handling...{color['endc']}\n")
                self.cointele_get_post(item)
            elif 'raw_data' in item:
                self.get_content(item)
        return item

    # ================================================
    # decode html tag and clean content
    # get keyword ranking
    # ================================================
    def get_content(self, data):
        data_ = data['raw_data']
        link_content = data['link_content']
        # decode_html_content = codecs.decode(data_, 'unicode-escape')
        decode_html_content = codecs.decode(data_, 'unicode-escape')
        # utils.show_message('decode_html_content', 'okcyan', decode_html_content)

        # get clean content for keywords ranking
        data_content = decode_html_content.split('fullText="')
        raw_content = data_content[1].split('audio="')[0]

        decode1 = utils.decode_html_content(raw_content)
        # utils.show_message('decode1', 'okgreen', decode1)
        # utils.show_message('decode_html_content', 'okcyan', raw_content)

        raw_content = raw_content.split('<template data-name="subscription_form"')[0]
        clean_content = remove_tags(raw_content)
        # set keywords
        data['keyword_ranking'] = utils.text_ranking(data, clean_content)
        if 'tag' in data:
            tag = data['tag']
            data['keyword_ranking'][tag] = '6.5'
        else:
            post = self.coinTele.find_one({'link_content': link_content})
            data['keyword_ranking'][post['tag']] = post['tag_point']
        utils.show_message('keyword_ranking', 'warning', data['keyword_ranking'])

        data['raw_content'] = str(raw_content)
        data['clean_content'] = str(clean_content)
        data['raw_data'] = ''
        # self.update_news(self.coinTele, data)
        utils.update_news(self.coinTele, data)

    def cointele_get_post(self, data):
        for post in data['data']:
            cointele_sample_data = sample_data()
            post_badge_title = post['postBadge']['postBadgeTranslates'][0]['title'].lower().strip()
            cointele_sample_data['id'] = post['id']
            cointele_sample_data['title'] = post['postTranslate']['title'].strip()
            cointele_sample_data['subtitle'] = str(post['postTranslate']['leadText']).strip()
            cointele_sample_data['link_img'] = post['postTranslate']['avatar'].strip()
            # cointele_sample_data['link_website_logo'] = self.link_website_logo
            cointele_sample_data['views'] = post['views']
            cointele_sample_data['id_post_translate'] = post['postTranslate']['id']  # postTranslate/id
            cointele_sample_data['description'] = str(post['postTranslate']['leadText']).strip()  # postTranslate/leadText
            if post_badge_title == 'experts answer' or post_badge_title == 'explained':
                cointele_sample_data['link_content'] = self.url.format('explained/' + str(post['slug']))
            else:
                cointele_sample_data['link_content'] = self.url.format('news/' + str(post['slug']))  # https://cointelegraph.com/news/ + slug
            cointele_sample_data['slug_content'] = post['slug'].strip()  # slug
            cointele_sample_data['author'] = post['author']['authorTranslates'][0]['name'].strip()  # author/authorTranslates/name
            cointele_sample_data['id_author'] = post['author']['authorTranslates'][0]['id'].strip()  # author/authorTranslates/id
            cointele_sample_data['link_author'] = self.url.format('authors/' + str(post['author']['slug'])).strip()  # https://cointelegraph.com/authors/ + slug_author
            cointele_sample_data['slug_author'] = post['author']['slug'].strip()  # author/slug
            if 'tag' in data:
                id_tag = data['tag']
                tag_ = self.handle_tag(id_tag)
                cointele_sample_data['tag'] = tag_
                # if tag_ != '':
                cointele_sample_data['link_tag'] = 'https://cointelegraph.com/tags/' + str(tag_)
                cointele_sample_data['tag_point'] = '5.01234321'
                # else:
                # cointele_sample_data['link_tag'] = ''
            cointele_sample_data['source'] = 'coinTelegraph'
            utils.handle_utc_datetime(post['postTranslate']['published'], cointele_sample_data)
            if self.coinTele.find_one({'link_content': cointele_sample_data['link_content']}):
                # self.update_news(self.coinTele, cointele_sample_data)
                utils.update_news(self.coinTele, cointele_sample_data)
                time.sleep(1)
            else:
                utils.insert_into_table(self.coinTele, cointele_sample_data)
                utils.show_message('Post', 'okblue', cointele_sample_data['link_content'])
                self.new_posts.append(cointele_sample_data['link_content'])
                time.sleep(1)

    def handle_tag(self, tag):
        if tag == '4':
            tag_ = 'bitcoin'
            return tag_
        elif tag == '26':
            tag_ = 'litecoin'
            return tag_
        elif tag == '581':
            tag_ = 'ripple'
            return tag_
        elif tag == '553':
            tag_ = 'ethereum'
            return tag_
        elif tag == '11':
            tag_ = 'blockchain'
            return tag_
        elif tag == '414':
            tag_ = 'business'
            return tag_
        else:
            utils.show_message('other tag', 'fail', 1)


class AdapulseScraperPipeline(object):
    def __init__(self):
        self.link_website_logo = 'https://adapulse.io/wp-content/uploads/2021/03/logonew@2x.png'
        self.myDatabase = mongoClient['cardanoNews']
        self.adaPulse = self.myDatabase['adaPulseSample']
        self.new_posts = []

    def close_spider(self, spider):
        for i, post in enumerate(self.new_posts):
            utils.show_message('New posts for today', 'okcyan', {i, post})

    def process_item(self, item, spider):
        if item['source'] == 'adapulse.io':
            if 'title' in item:
                utils.show_message('', 'okblue', 'AdaPulse Pipeline handling...')
                # self.adaPulse.insert_one(item)
                self.get_posts(item)
        # return item

    def get_posts(self, item):
        item['timestamp'] = utils.handle_datetime(item, item[''])
        if self.adaPulse.find_one({'link_content': item['link_content']}):
            utils.update_news(self.adaPulse, item)
            time.sleep(.5)
        else:
            utils.insert_into_table(self.adaPulse, item)
            utils.show_message('Post', 'okblue', item['link_content'])
            self.new_posts.append(item['link_content'])
            time.sleep(.5)
