import time
import tweepy
from tweepy import auth
import urllib3
import json
import datetime
import os

from dataclasses import dataclass
from typing import List
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener

urllib3.disable_warnings()

@dataclass
class Tweet:
    id: int
    date: datetime.datetime
    text: str
    user: str
    retweet_count: int
    fav: int
    location: str
    hashtags: List[str]
    mentions: List[str]

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date.isoformat(),
            "text": self.text,
            "user": self.user,
            "retweet_count": self.retweet_count,
            "favorites_count": self.fav,
            "location": self.location,
            "hashtags": self.hashtags,
            "mentions": self.mentions
        }

    def to_json(self):
        return json.dumps(self.to_dict())

class TwitterMonitor:
    def __init__(self):
        ckey = "6vdnk3y7M0RK8TM8WJgbRBrEt"
        csecret = "lRwAr1g9qo9PAjWNuxI7voj67xXQFVYksuJCZKDjfVXkp8N3n3"
        atoken = "292013960-Brz5aGHJ5Czv2Gx8t2SHBuC2PUFhIid25TMJVInq"
        asecret = "2iB6wVnRvs4myXHSX61bKrjgXlxzwwKpU8tdE87NDXWwJ"

        self.file_path = os.path.dirname(os.path.realpath(__file__))

        self.tags: List[str] = []
        
        auth = tweepy.AppAuthHandler(ckey, csecret)
        self.api = tweepy.API(auth)        
        return

    def add_tags(self, tags: List[str]):
        for tag in tags:
            self.tags.append(tag)
        return self

    def create_cursor(self):
        self.cursor = tweepy.Cursor(self.api.search, q=self.tags, count=100, lang="en").items()
        return self

    def rate_limiter(self):
        while True:
            try:
                yield self.cursor.next()
            except tweepy.RateLimitError:
                time.sleep(15 * 60)

    def monitor(self):
        count = 0
        for tweet in self.rate_limiter():
            tw = Tweet(
                    id=tweet.id,
                    date=tweet.created_at,
                    text=tweet.text,
                    user=tweet.user.screen_name,
                    retweet_count=tweet.retweet_count,
                    fav=tweet.favorite_count,
                    hashtags=tweet.entities.get('hashtags'),
                    mentions=tweet.entities.get('user_mentions'),
                    location=tweet.user.location
                )
            
            with open(os.path.join(self.file_path, "tweets", f"{tw.id}.json"), 'w') as jsonfile:
                json.dump(tw.to_dict(), jsonfile, indent=4)

            count +=1
            if count > 100:
                break
        return

TwitterMonitor()\
    .add_tags(["#Kabul", "#Afghanistan"])\
    .create_cursor()\
    .monitor()