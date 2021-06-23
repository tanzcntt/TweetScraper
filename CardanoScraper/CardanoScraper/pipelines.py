import time
import json
import re
import pymongo
from datetime import datetime
from . import utils
from time import sleep
color = utils.colors_mark()
mongoClient = pymongo.MongoClient("mongodb://root:password@localhost:27017/")

# sample_data = """    insetData["title"] = newsData["title"]
#         insetData["description"] = ""
#         insetData["content"] = newsData["raw_content"]
#         insetData["websiteUri"] = newsData["link_content"]
#         insetData["keywords"] = JSON.stringify(newsData["keyword_ranking"])
#         insetData["createdAt"] = new Date(newsData["timestamp"] * 1000)"""


def sample_data():
    data = {
        'id': '',  # id
        'title': '',  # postTranslate/title
        'subtitle': '',
        'link_img': '',  # postTranslate/avatar
        'views': '',  # views
        'id_post_translate': '',  # postTranslate/id
        'description': '',  # postTranslate/leadText
        'link_content': '',  # https://cointelegraph.com/news/ + slug
        'slug_content': '',  # slug
        'raw_content': '',
        'keyword_ranking': '',
        'author': '',  # author/authorTranslates/name
        'id_author': '',  # author/authorTranslates/id
        'link_author': '',  # https://cointelegraph.com/authors/ + slug_author
        'slug_author': '',  # author/slug
        'tag': '',
        'link_tag': '',
        'published': '',  # postTranslate/published
        'timestamp': '',
        'latest': 0,
        'approve': 1,
    }
    return data


class CardanoscraperPipeline(object):
    def __init__(self):
        self.myDatabase = mongoClient["cardanoNews"]
        self.postContents = self.myDatabase['allNews']
        self.testCarda = self.myDatabase['testAllNews2']
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
                    utils.insert_into_table(self.postContents, item)
                    self.new_posts.append(item['link_content'])
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
        self.new_posts = []

    def close_spider(self, spider):
        for index, value in enumerate(self.new_posts):
            utils.show_message(message='Latest Post for today', colour='okblue', data={index: value})
        print(f"{color['warning']}IOHK Crawl Completed!{color['endc']}")

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
                self.new_posts.append(iohk_all_posts['link_content'])
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
        # self.coindesk = self.myDatabase['coindeskSample']
        self.coindesk = self.myDatabase['coindeskTest6']
        self.url = 'https://www.coindesk.com{}'
        self.new_posts = []

    def close_spider(self, spider):
        data = self.coindesk.find()
        for post in data:
            if 'raw_content' not in post:
                print(post['link_content'])
                my_query = {'link_content': post['link_content']}
                posts = self.coindesk.find({}, my_query)
                for empty_content in posts:
                    utils.show_message('empty content', 'fail', empty_content)
                if self.coindesk.delete_one(my_query):
                    utils.show_message('delete empty content post', 'fail', '')
            elif post['raw_content'] == '':
                my_query = {'link_content': post['link_content']}
                if self.coindesk.delete_one(my_query):
                    utils.show_message('delete empty content post', 'fail', '')
            else:
                pass
        for index, value in enumerate(self.new_posts):
            utils.show_message(message='Latest Post for today', colour='okblue', data={index: value})
        print(f"{color['warning']}Coindesk Crawl Completed!{color['endc']}")

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
                    self.new_posts.append(item['link_content'])
            elif 'raw_data' in item:
                self.insert_raw_content(self.coindesk, item)
        elif item['source'] == 'coindeskLatestNews':
            if 'next' in item:
                self.coindesk_get_post(item)
            elif 'raw_content' in item:
                self.coindesk_get_raw_content(self.coindesk, data=item)

    def update_table(self, table, data):
        query = {
            'link_content': data['link_content']
        }
        if table.update_one(query, {'$set': data}):
            utils.update_success_notify(table)
        time.sleep(1)

    def insert_raw_content(self, table, data):
        post = data['raw_data']
        self.handle_link_img(post, data)
        # many kinds of public post date
        self.handle_datetime(post, data)
        # some Video post had no content
        self.handle_content(post, data)

        link_post = post['url'].strip()
        slug_content = link_post.split('/')[-1]
        # author = post['author'][0]['name']
        # print(author)
        # link_content = self.url.format(str(slug_content))
        query = {
            "slug_content": slug_content
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
            coindesk_sample_data['title'] = post['title']
            coindesk_sample_data['subtitle'] = post['text']
            coindesk_sample_data['link_img'] = post['images']['images']['desktop']['src']
            coindesk_sample_data['slug_content'] = post['slug']
            coindesk_sample_data['link_content'] = self.url.format('/' + str(post['slug']))
            coindesk_sample_data['author'] = post['authors'][0]['name']
            coindesk_sample_data['slug_author'] = post['authors'][0]['slug']
            coindesk_sample_data['link_author'] = self.url.format('/author/' + str(post['authors'][0]['slug']))
            coindesk_sample_data['tag'] = post['tag']['name']
            coindesk_sample_data['link_tag'] = self.url.format('/' + str(post['tag']['slug']))
            coindesk_sample_data['published'] = post['date']
            coindesk_sample_data['timestamp'] = datetime.strptime(post['date'], '%Y-%m-%dT%H:%M:%S').timestamp()
            print(coindesk_sample_data)
            if self.coindesk.find_one({'slug_content': coindesk_sample_data['slug_content']}):
                self.update_latest_news(self.coindesk, coindesk_sample_data)
                time.sleep(.1)
            else:
                utils.insert_into_table(self.coindesk, data=coindesk_sample_data)
                self.new_posts.append(coindesk_sample_data['link_content'])
                time.sleep(.1)

    def coindesk_get_raw_content(self, table, data):
        raw_content = data['raw_content']
        utils.show_message('raw_content', 'okgreen', raw_content)
        keyword_ranking = utils.text_ranking(data, raw_content)
        data['keyword_ranking'] = keyword_ranking
        data['raw_data'] = ''
        if table.find_one({'slug_content': data['slug_content']}):
            self.update_latest_news(self.coindesk, data=data)
        sleep(.1)

    def standard_date(self, date, data):
        standard_date = data[date].split(':')[:2]
        standard_date = ':'.join(standard_date)
        return standard_date

    def handle_content(self, post, data):
        if 'articleBody' in post:
            data['raw_content'] = post['articleBody']
            data['keyword_ranking'] = utils.text_ranking(data, data['raw_content'])
            print(f"{color['warning']}{data['keyword_ranking']}{color['endc']}")
            return data['keyword_ranking']
        else:
            # update base one: slug but some post links url in type: index.php?p=637454
            link_post = post['url'].strip()
            slug_content = link_post.split('/')[-1]
            data_ = self.coindesk.find_one({'slug_content': slug_content})

            # print(f"{color['okgreen']}{data_}{color['endc']}")
            if 'subtitle' in data_:
                utils.show_message('empty articleBody | replace articleBody by Subtitle', 'okcyan', data_['subtitle'])
                data['raw_content'] = data_['subtitle']
                data['keyword_ranking'] = utils.text_ranking(data, data['raw_content'])
                return data['keyword_ranking'], data['raw_content']
            elif 'description' in data:
                utils.show_message('empty articleBody | replace articleBody by Description', 'okcyan', data_['description'])
                utils.show_message('description', 'okblue', data_['description'])
                data['raw_content'] = data_['description']
                data['keyword_ranking'] = utils.text_ranking(data, data['raw_content'])
                return data['keyword_ranking'], data['raw_content']
            else:
                utils.show_message('Other key of content. Watch again and!', 'fail', '')
                # delete post
            data['keyword_ranking'] = ''
            data['raw_content'] = ''
            return data['keyword_ranking'], data['raw_content']

    def handle_datetime(self, post, data):
        for date in post:
            if 'date' in date.lower():
                # take datePublished as default timestamp firstly
                if 'datePublished' in post:
                    if post['datePublished']:
                        data['datePublished'] = post['datePublished']
                        data['timestamp'] = datetime.strptime(self.standard_date('datePublished', post), '%Y-%m-%dT%H:%M').timestamp()
                        utils.show_message('datePublished', 'okcyan', data['timestamp'])
                        return data['timestamp']
                    else:
                        if post[date]:
                            data[date] = post[date]
                            data['timestamp'] = datetime.strptime(self.standard_date(date, post), '%Y-%m-%dT%H:%M').timestamp()
                            utils.show_message(date, 'okcyan', data['timestamp'])
                            return data['timestamp']

    def handle_links(self, data):
        data['link_content'] = self.url.format(str(data['link_content']))
        data['link_tag'] = self.url.format(str(data['link_tag']))
        data['link_author'] = self.url.format(str(data['link_author']))

    def handle_link_img(self, post, data):
        if type(post['thumbnailUrl']) == list:
            data['link_img'] = post['thumbnailUrl'][0]
        else:
            data['link_img'] = post['thumbnailUrl']


class CoinTelegraphScraperPipeline(object):
    def __init__(self):
        self.url = 'https://cointelegraph.com/news/{}'

    def close_spider(self, spider):
        print(f"{color['warning']}CoinTeleGraph Crawl Completed!{color['endc']}")

    def process_item(self, item, spider):
        print(f"{color['okblue']}Cointelegraph Pipeline handling...{color['endc']}\n")
        # return item

    # def
