import time

from . import utils
import json
import re
import pymongo
from itemadapter import ItemAdapter
from . import text_rank_4_keyword
from datetime import datetime

color = utils.colors_mark()
textRank = text_rank_4_keyword.TextRank4Keyword()
mongoClient = pymongo.MongoClient("mongodb://root:password@localhost:27017/")

sample_data = """    insetData["title"] = newsData["title"]
        insetData["description"] = ""
        insetData["content"] = newsData["raw_content"]
        insetData["websiteUri"] = newsData["link_content"]
        insetData["keywords"] = JSON.stringify(newsData["keyword_ranking"])
        insetData["createdAt"] = new Date(newsData["timestamp"] * 1000)"""


def initialize_sample_data():
    data = {
        'publish_date': '',
        'timestamp': '',
        'approve': 1,
        'author_title': '',
        'author_display_name': '',
        'author_thumbnail': '',
        'author_job_titles': '',
        'author_profile_links': '',
        'post_main_img': '',
        'lang': '',
        'title': '',
        'slug': '',
        'subtitle': '',
        'audio': '',
        'soundcloud': [],
        'raw_content': '',
        'keyword_ranking': '',
        'total_pages': '',
        'filters': '',
        'recent_posts': '',
        'current_page': '',
        'current_url_page': '',
        'link_content': '',
        'author_profile_url': '',
        'source': 'iohk',
        'raw_data': '',
    }
    return data


def handle_datetime(data, date_time):
    # cardar date type: 28 November 2017 19:22
    if '-' in date_time:
        date_time = date_time.split('T')[0]
        data['timestamp'] = datetime.strptime(date_time, "%Y-%m-%d").timestamp()
        return data['timestamp']
    data['timestamp'] = datetime.strptime(date_time, "%d %B %Y %H:%M").timestamp()
    return data['timestamp']


def get_table(table):
    return str(table).split(', ')[-1].split("'")[1]


def write_json_file(file, item):
    line = json.dumps(ItemAdapter(item['avatars']).asdict()) + '\n'
    file.write(line)


def text_ranking(data, raw_content_):
    raw_content = utils.remove_html_tags(raw_content_)
    textRank.analyze(raw_content, window_size=6)
    data['keyword_ranking'] = textRank.get_keywords(10)
    return data['keyword_ranking']


def insert_into_table(table, data):
    if table.insert_one(data):
        print(f"{color['okgreen']}Imported Posts {get_table(table)} success!!!{color['endc']}")
    time.sleep(1)


def update_success_notify(table):
    print(f"{color['okcyan']}Updating {get_table(table)} table{color['endc']}\n")


def update_rawcontent_notify(table, data):
    print(f"{color['okcyan']}Updating Raw Content into {get_table(table)}{color['endc']} for post: {data['link_content']}")


def insert_success_notify(table):
    print(f"{color['okgreen']}Imported Posts {get_table(table)} success!!!{color['endc']}")


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
        # we have two flows of data
        # 1st for posts, 2nd for contents
        # ================================================
        # if run crawlAllCardanoNews, insert data into allNews table
        # for Update to analyze
        # ================================================
        if item['source'] == 'cardano':
            if 'title' in item:
                item['avatars'] = self.handle_link_avatars(item['avatars'])
                if self.postContents.find_one({'link_post': item['link_post']}):
                    self.update_table(self.postContents, item)
                else:
                    insert_into_table(self.postContents, item)
            elif 'raw_content' in item:
                handle_datetime(item, item['post_time'])
                text_ranking(item, item['raw_content'])
                self.update_raw_content(self.postContents, item)
                print(f"{color['warning']}Imported raw_content to {get_table(self.postContents)} {color['endc']}\n")
        # ================================================
        # for test every day
        # ================================================
        # if item['source'] == 'cardano':
        #     if 'title' in item:
        #         item['avatars'] = self.handle_link_avatars(item['avatars'])
        #         if self.testCarda.find_one({'link_post': item['link_post']}):
        #             self.update_table(self.testCarda, item)
        #         else:
        #             insert_into_table(self.testCarda, item)
        #     elif 'raw_content' in item:
        #         handle_datetime(item, item['post_time'])
        #         text_ranking(item, item['raw_content'])
        #         self.update_raw_content(self.testCarda, item)
        #         print(f"{color['warning']}Imported raw_content to {get_table(self.testCarda)} {color['endc']}\n")
        # ================================================
        #
        # ================================================
        # print(f"{color['warning']}This is{color['endc']}Item...{color['okgreen']}{item}{color['endc']}")
        return item

    def update_table(self, table, data):
        query = {
            "link_post": data['link_post'].strip(),
        }
        if table.update_one(query, {'$set': data}):
            # print(f"{color['okcyan']}Updating Latest Cardano page into {get_table(table)}{color['endc']} ")
            update_success_notify(table)
        time.sleep(1)

    def update_raw_content(self, table, data):
        query = {
            "link_post": data['link_content'].strip()
        }
        if table.update_one(query, {'$set': data}):
            # print(f"{color['okcyan']}Updating Raw Content into {get_table(table)}{color['endc']} for post: {data['link_content']}")
            update_rawcontent_notify(table, data)
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
        self.iohk_sample1 = self.myDatabase['iohkSampleTest']

    def close_spider(self, spider):
        print(f"{color['warning']}Crawl Completed!{color['endc']}")

    def process_item(self, item, spider):
        print(f"\n{color['okblue']}IOHK Pipeline handling...{color['endc']}")
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
            iohk_all_posts = initialize_sample_data()
            author_info = post['author']
            iohk_all_posts['publish_date'] = post['publish_date']
            iohk_all_posts['timestamp'] = handle_datetime(iohk_all_posts, post['publish_date']),
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

            keyword_ranking = text_ranking(iohk_all_posts, iohk_all_posts['raw_content'])

            print(f"Current page: {iohk_all_posts['current_url_page']}")
            print(f"Current post: {iohk_all_posts['title']}")
            iohk_all_posts['raw_data'] = post
            iohk_all_posts['keyword_ranking'] = keyword_ranking
            if self.iohk_sample1.find_one({'link_content': iohk_all_posts['link_content']}):
                self.update_iohk(self.iohk_sample1, iohk_all_posts)
                time.sleep(2)
            else:
                insert_into_table(self.iohk_sample1, iohk_all_posts)
                time.sleep(2)

    def update_iohk(self, table, data):
        query = {
            'link_content': data['link_content'].strip()
        }
        if table.update_one(query, {'$set': data}):
            # print(f"{color['okcyan']}Updating {get_table(table)} table{color['endc']}\n")
            update_success_notify(table)
        time.sleep(1)


class CoindeskScraperPipeline(object):
    def __init__(self):
        self.myDatabase = mongoClient['cardanoNews']
        self.coindesk = self.myDatabase['coindeskSample']

    def close_spider(self, spider):
        print(f"{color['warning']}Crawl Completed!{color['endc']}")

    def process_item(self, item, spider):
        if item['source'] == 'coindesk':
            if 'title' in item:
                self.handle_links(item)
                insert_into_table(self.coindesk, item)
            elif 'raw_data' in item:
                return item
            return item

    def handle_links(self, data):
        url = 'https://www.coindesk.com{}'
        data['link_content'] = url.format(str(data['link_content']))
        data['link_tag'] = url.format(str(data['link_tag']))
        data['link_author'] = url.format(str(data['link_author']))
