import datetime
import getopt
import re
import sys

import pymongo
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
import asyncio

mongoClient = pymongo.MongoClient("mongodb://root:password@localhost:27017/")
myDatabase = mongoClient["twitterdata"]

twCollection = myDatabase['tw']
userCollection = myDatabase['user']

# Remove 1st argument from the
# list of command line arguments
argumentList = sys.argv[1:]

# Options
options = "d:u:t:"

long_options = ["day", "url", "token"]
url = ''
token = ''
day = 0
try:
    # Parsing argument
    arguments, values = getopt.getopt(argumentList, options, long_options)
    # checking each argument
    for currentArgument, currentValue in arguments:
        if currentArgument in ("-d", "--day"):
            day = int(currentValue)
        if currentArgument in ("-t", "--token"):
            token = currentValue
        if currentArgument in ("-u", "--url"):
            url = currentValue
except getopt.error as err:
    # output error, and return with an error code
    print(str(err))


async def get_tw_from_date(x):
    print("Check data on ", x)
    month = x.strftime("%b")
    day_string = x.strftime("%a")
    d = x.strftime("%d")
    year = x.year.__str__()
    pat = re.compile(
        r'(?=.*\b{0}\s\b)(?=.*\b\s{1}\s\b)(?=.*\b\s{2}\s\b)(?=.*\b{3}\b)'.format(day_string, month, d, year))
    print(r'(?=.*\b{0}\s\b)(?=.*\b\s{1}\s\b)(?=.*\b\s{2}\s\b)(?=.*\b{3}\b)'.format(day_string, month, d, year))
    top_tws = twCollection.find({"created_at": pat, "favorite_count": {"$gt": 1}}) \
        .sort([("retweet_count", -1), ("favorite_count", -1), ("reply_count", -1)]) \
        # .limit()
    await push_data_to_dhunt(top_tws)


def tweet_without_user():
    print("Tweet without user")
    transport = AIOHTTPTransport(url=url, headers={'Authorization': 'Bearer ' + token})

    # Create a GraphQL client using the defined transport
    client = Client(transport=transport, fetch_schema_from_transport=True)
    while True:
        query = gql(
            """
            query {
              tweetWithoutUser{
                id
              }
            }
            """
        )
        result = client.execute(query)
        if result["tweetWithoutUser"]:
            for id_search in result["tweetWithoutUser"]:
                tw = twCollection.find_one({"id_str": id_search["id"]})
                print(id_search)
                push_data_to_dhunt(tw)
        else:

            break


async def push_data_to_dhunt(top_tws):
    for tw in top_tws:
        transport = AIOHTTPTransport(url=url, headers={'Authorization': 'Bearer ' + token})

        # Create a GraphQL client using the defined transport
        # client = Client(transport=transport, fetch_schema_from_transport=True)

        # Provide a GraphQL query

        # Execute the query on the transport
        tw.pop("_id", None)
        user_data = userCollection.find_one({"id_str": tw["user_id_str"]})
        user_data.pop("_id", None)
        params = {"tweetData": tw, "userData": user_data}
        async with Client(
                transport=transport, fetch_schema_from_transport=True,
        ) as session:
            # Execute single query
            query = gql(
                """
                mutation  submitTweet($tweetData : JSONObject!,$userData : JSONObject!){
                  submitTweet(tweetData : $tweetData,userData : $userData) {
                    id
                    item{
                        id
                    }
                  }
                }
                """
            )

            await session.execute(query, variable_values=params)


async def main(day_in):
    today = datetime.date.today()
    yesterday = today
    task1 = asyncio.create_task(get_tw_from_date(yesterday))

    day_in = day_in + 1
    yesterday = today - datetime.timedelta(days=day_in)
    task2 = asyncio.create_task(get_tw_from_date(yesterday))

    day_in = day_in + 1
    yesterday = today - datetime.timedelta(days=day_in)
    task3 = asyncio.create_task(get_tw_from_date(yesterday))

    await task1
    await task2
    await task3

asyncio.run(main(day))
