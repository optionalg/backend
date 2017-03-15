# Import the necessary methods from tweepy library
import _thread
import html
import json
import subprocess
import time

from tweepy import API
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener

from main import app

# sample woeid code for countries USA, UK, Brazil, Canada, India
# woeidList = ['23424977','23424975','23424768', '23424775', '23424848']
woeidList = ['23424975']  # Used to fetch trending topics
streaming_regions = [{
    "name": "South West England",
    "bounding_box": [-5.71, 49.71, -0.62, 53.03]
}, {
    "name": "South East England",
    "bounding_box": [-0.56, 50.77, 1.83, 53.07]
}, {
    "name": "Central UK",
    "bounding_box": [-5.38, 53.09, 0.53, 55.15]
}, {
    "name": "Northern UK",
    "bounding_box": [-7.48, 55.21, -0.35, 61.05]
}, {
    "name": "Northern Ireland",
    "bounding_box": [-10.5359, 53.2586, -5.2823, 55.2102]
}, {
    "name": "Southern Ireland",
    "bounding_box": [-10.83, 51.22, -5.57, 53.27]
}]

TrendingTopics = []
# count = 0;
startTime = time.time()


# timeLimit = 60  # 1/2 hour limit

# This is a basic listener that just prints received tweets to stdout.
class StdOutListener(StreamListener):
    # On every tweet arrival
    def on_data(self, data):
        global startTime, TrendingTopics
        if ((time.time() - startTime) < (60 * 15)):
            # Convert the string data to pyhton json object.
            data = json.loads(html.unescape(data))
            # Gives the content of the tweet.
            tweet = data['text']
            # print(json.dumps(tweet))
            # If tweet content contains any of the trending topic.
            if any(topic in json.dumps(tweet) for topic in TrendingTopics):
                # Add trending topic and original bounding box as attribute
                # data['TrendingTopic'] = topic
                print(json.dumps(tweet))
                # data['QueriedBoundingBox'] = location[0]
                # Convert the json object again to string
                dataObj = json.dumps(data)
                # Appending the data in tweetlondon.json file
                with open('tweetlocation.json', 'a') as tf:
                    tf.write(dataObj)
                    # prints on console
            return True
        else:
            startTime = time.time();
            return False

    def on_error(self, status):
        print(status)


def stream_tweets_for_region(name, bounding_box, keys):
    global TrendingTopics
    print("Streaming tweets for {}".format(name))
    consumer_key = keys['CONSUMER_KEY']
    consumer_secret = keys['CONSUMER_SECRET']
    access_token = keys['ACCESS_TOKEN']
    access_secret = keys['ACCESS_SECRET']
    # print("\n ########################################## Data mining for location : ", location, "started ########################################## \n")
    # print(startTime)
    count = 0
    # This handles Twitter authetification and the connection to Twitter Streaming API
    l = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)

    api = API(auth)
    stream = Stream(auth, l)

    while True:
        count = count + 1
        # This runs every an hour
        print(
            '\n ****************************************** Tweet Collection for next {0} hours started ************************************************************** \n'.format(
                count / 2))
        print(count)

        # for country in location:
        for country in woeidList:
            trends1 = api.trends_place(country)
            data = trends1[0]
            # grab the trends
            trends = data['trends']
            # grab the name from each trend
            TrendingTopics = [trend['name'] for trend in trends[:10]]
            # put all the names together with a ' ' separating them
            # trendsName = ' '.join(names)
            # print("\n &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&& Trending topic for this time are &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
            print(TrendingTopics, "\n")
            # Stream the tweets for given location coordinates
            stream.filter(locations=bounding_box)

    # # send data to s3 every 5th hour
    # # only one thread is required to write data to s3 bucket
    if (count % 5 == 0 and count != 0 and location[1] == 49.71):
        # This runs the system command of transfering file to s3 bucket
        proc = subprocess.Popen(["aws", "s3", "cp", "tweetlocation.json", "s3://sentiment-bristol"],
                                stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        print("program output:", out)


def start_mining():
    _thread.start_new_thread(start_threads, ())


def start_threads():
    try:
        min_length = min(len(streaming_regions), len(app.config['MINING_KEYS']))
        for region, keys in zip(streaming_regions[:min_length], app.config['MINING_KEYS'][:min_length]):
            _thread.start_new_thread(stream_tweets_for_region, (region['name'], region['bounding_box'], keys))
            time.sleep(10)
    except:
        print("Error: unable to start the thread")

    while 1:
        pass


if __name__ == '__main__':
    start_mining()
