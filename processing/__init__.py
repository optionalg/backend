import calendar
import datetime

SHORT_PERIOD = datetime.timedelta(days=7)
SHORT_INTERVAL_LENGTH = datetime.timedelta(hours=1)
LONG_INTERVAL_LENGTH = datetime.timedelta(days=1)

MINING_TOPIC_KEY = "TrendingTopic"
MINING_REGION_KEY = "Woeid"
MINING_TEXT_KEY = "text"
MINING_ID_KEY = "id"
MINING_TIMESTAMP_KEY = "timestamp_ms"


def get_short_term_start():
    # TODO: check daylight saving time issues
    now = datetime.datetime.utcnow()
    period_start = (now - SHORT_PERIOD).date()
    period_timestamp = calendar.timegm(period_start.timetuple())
    return datetime.datetime.fromtimestamp(period_timestamp)


def get_long_intervals_between(start, end):
    assert (datetime.timedelta(days=1).seconds % LONG_INTERVAL_LENGTH.seconds == 0), \
        "LONG_INTERVAL_LENGTH must fit an integer number of times into a day"
    intervals = []
    start_day = start.date()
    current_start = start_day
    while current_start + LONG_INTERVAL_LENGTH <= end:
        intervals.append((current_start, current_start + LONG_INTERVAL_LENGTH))
        current_start += LONG_INTERVAL_LENGTH
    return intervals


def get_short_intervals():
    start = get_short_term_start()
    intervals = []
    current_start = start
    while current_start < datetime.datetime.now():
        intervals.append((current_start, current_start + SHORT_INTERVAL_LENGTH))
        current_start += SHORT_INTERVAL_LENGTH
    return intervals


class Tweet:
    def __init__(self, tweet_obj):
        self.text = tweet_obj["text"]
        self.tweet_id = tweet_obj["tweet_id"]
        self.sentiment = tweet_obj["sentiment"]
        self.woeid = tweet_obj["woeid"]
        self.timestamp = tweet_obj["timestamp"]
        self.topic = tweet_obj["topic"]

    @classmethod
    def load_raw_tweet(cls, tweet_obj):
        arr = dict()
        arr["text"] = tweet_obj[MINING_TEXT_KEY]
        arr["tweet_id"] = tweet_obj[MINING_ID_KEY]
        # TODO: compute sentiment
        arr["sentiment"] = None
        # TODO: compute woeid
        arr["woeid"] = None
        arr["timestamp"] = int(tweet_obj[MINING_TIMESTAMP_KEY]) // 1000
        arr["topic"] = tweet_obj[MINING_TOPIC_KEY]
        return Tweet(arr)

    def get_dict(self):
        return {
            "text": self.text,
            "tweet_id": self.tweet_id,
            "sentiment": self.sentiment,
            "woeid": self.woeid,
            "timestamp": self.timestamp,
            "topic": self.topic
        }
