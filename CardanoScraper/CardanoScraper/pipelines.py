import time
import json
import re
import pymongo
from datetime import datetime
from . import utils

color = utils.colors_mark()
mongoClient = pymongo.MongoClient("mongodb://root:password@localhost:27017/")

sample_data = """    insetData["title"] = newsData["title"]
        insetData["description"] = ""
        insetData["content"] = newsData["raw_content"]
        insetData["websiteUri"] = newsData["link_content"]
        insetData["keywords"] = JSON.stringify(newsData["keyword_ranking"])
        insetData["createdAt"] = new Date(newsData["timestamp"] * 1000)"""


class CardanoscraperPipeline(object):
    def __init__(self):
        self.myDatabase = mongoClient["cardanoNews"]
        self.postContents = self.myDatabase['allNews']
        self.testCarda = self.myDatabase['testAllNews2']

    # ================================================
    # handle put data to GraphQl
    # ================================================
    def close_spider(self, spider):
        print(f"{color['warning']}Crawl Completed!{color['endc']}")

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
                    utils.insert_into_table(self.postContents, item)
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

    def close_spider(self, spider):
        print(f"{color['warning']}Crawl Completed!{color['endc']}")

    def process_item(self, item, spider):
        print(f"\n{color['okblue']}IOHK Pipeline handling...{color['endc']}\n")
        if item['source'] == 'iohk':
            self.iohk_get_posts(item)
        # elif item['source'] == 'coindesk':
        #     return item
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
                time.sleep(2)
            else:
                utils.insert_into_table(self.iohk_sample1, iohk_all_posts)
                time.sleep(2)

    def update_iohk(self, table, data):
        query = {
            'link_content': data['link_content'].strip()
        }
        if table.update_one(query, {'$set': data}):
            # print(f"{color['okcyan']}Updating {get_table(table)} table{color['endc']}\n")
            utils.update_success_notify(table)
        time.sleep(1)


class CoindeskScraperPipeline(object):
    def __init__(self):
        self.myDatabase = mongoClient['cardanoNews']
        self.coindesk = self.myDatabase['coindeskSample']
        self.coindesk_test = self.myDatabase['coindeskTest']
        self.url = 'https://www.coindesk.com{}'

    def close_spider(self, spider):
        print(f"{color['warning']}Crawl Completed!{color['endc']}")

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
            elif 'raw_data' in item:
                self.insert_raw_content(self.coindesk, item)
        # return item

    def update_table(self, table, data):
        query = {
            'link_content': data['link_content']
        }
        if table.update_one(query, {'$set': data}):
            utils.update_success_notify(table)
        time.sleep(1)

    def handle_links(self, data):
        data['link_content'] = self.url.format(str(data['link_content']))
        data['link_tag'] = self.url.format(str(data['link_tag']))
        data['link_author'] = self.url.format(str(data['link_author']))

    def insert_raw_content(self, table, data):
        post = data['raw_data']
        # many kinds of public post date
        if 'datePublished' in post:
            date_published = post['datePublished'].split('+')[0]
            print(f"{color['fail']}{date_published}{color['endc']}")
            data['timestamp'] = datetime.strptime(date_published, '%Y-%m-%dT%H:%M:%S').timestamp()
        elif 'dateModified' in post:
            date_published = post['dateModified'].split('+')[0]
            print(f"{color['fail']}{date_published}{color['endc']}")
            data['timestamp'] = datetime.strptime(date_published, '%Y-%m-%dT%H:%M:%S').timestamp()
        else:
            date_published = post['uploadDate'].split('.')[0]
            print(f"{color['fail']}{date_published}{color['endc']}")
            data['timestamp'] = datetime.strptime(date_published, '%Y-%m-%dT%H:%M:%S').timestamp()

        # some Video post had no content
        if 'articleBody' in post:
            data['raw_content'] = post['articleBody']
        else:
            data['raw_content'] = ''

        link_post = post['url'].strip()
        slug = link_post.split('.com')[1]
        query = {
            "link_content": self.url.format(str(slug))
        }
        if table.update_one(query, {'$set': data}):
            print(f"{color['okgreen']}Update raw_content success!{color['endc']} in {self.url.format(str(slug))}")
        time.sleep(1)

# 1623924558 https://www.coindesk.com/iron-finance-says-it-suffered-cryptos-first-large-scale-bank-run-in-token-crash-postmortem
