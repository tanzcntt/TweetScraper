from keybert import KeyBERT
import pymongo
import re
import datetime

mongoClient = pymongo.MongoClient("mongodb://root:password@localhost:27017/")
myDatabase = mongoClient["twitterdata"]

twCollection = myDatabase['tw']
userCollection = myDatabase['user']


def get_tw_from_date(x):
    print("Check data on ", x)
    month = x.strftime("%b")
    day_string = x.strftime("%a")
    day = x.strftime("%d")
    year = x.year.__str__()
    pat = re.compile(
        r'(?=.*\b{0}\s\b)(?=.*\b\s{1}\s\b)(?=.*\b\s{2}\s\b)(?=.*\b{3}\b)'.format(day_string, month, day, year))
    print(r'(?=.*\b{0}\s\b)(?=.*\b\s{1}\s\b)(?=.*\b\s{2}\s\b)(?=.*\b{3}\b)'.format(day_string, month, day, year))
    top_tws = twCollection.find({"created_at": pat, "favorite_count": {"$gt": 1}}) \
        .sort([("retweet_count", -1), ("favorite_count", -1), ("reply_count", -1)]) \
        # .limit(20)
    for tw in top_tws:
        kw_model = KeyBERT('distilbert-base-nli-mean-tokens')
        keywords = kw_model.extract_keywords(tw["full_text"])
        print(tw['full_text'])
        print(keywords)


today = datetime.date.today()
get_tw_from_date(today)
