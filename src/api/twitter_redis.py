from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
import os
import time
import redis


@dataclass(frozen=True)
class Tweet:
    # dataclass for Tweet data
    tweet_id: int
    user_id: int
    tweet_ts: str
    tweet_text: str


class TwitterRedis:
    """
    Redis-backed implementation of the Twitter API
    - on each postTweet, copy tweet (or reference) into each follower's home timeline so getTimeline is fast
    """

    def __init__(self, r: Optional[redis.Redis] = None):
        """
        Create a Redis client
        Otherwise, read connection settings from .env
        """
        if r is None:
            host = os.getenv("REDIS_HOST", "127.0.0.1")
            port = int(os.getenv("REDIS_PORT", "6379"))
            db = int(os.getenv("REDIS_DB", "0"))
            self.r = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        else:
            self.r = r

        # to limi how many tweets we keep per home timeline to control memory usage
        self.max_home = int(os.getenv("HOME_MAX", "1000"))

    # same shape as the MySQL API
    def post_tweet(self, user_id: int, tweet_text: str) -> int:
        # global tweet id
        tweet_id = int(self.r.incr("tweet:id"))
        # we;re using a millisecond timestamp so ordering is stable and consistent
        ts_ms = int(time.time() * 1000)

        # store tweet once - no duplicate text
        self.r.hset(f"tweet:{tweet_id}", mapping={
            "tweet_id": str(tweet_id),
            "user_id": str(user_id),
            "ts_ms": str(ts_ms),
            "text": tweet_text
        })

        # fan-out on write: push reference to each follower's home timeline
        followers = self.r.smembers(f"followers:{user_id}")
        # include self so you see your own tweets
        followers.add(str(user_id))

        pipe = self.r.pipeline(transaction=False)
        for fid in followers:
            home_key = f"home:{fid}"
            # add tweet_id reference into the home timeline, score = timestamp
            pipe.zadd(home_key, {str(tweet_id): ts_ms})
            # keep only most recent max_home items
            pipe.zremrangebyrank(home_key, 0, -(self.max_home + 1))
        pipe.execute()

        return tweet_id

    def get_home_timeline(self, user_id: int, limit: int = 10) -> List[Tweet]:
        """
        Return the user's home timeline: the most recent tweets from users they follow
        """
        # get most recent tweet_ids
        tweet_ids = self.r.zrevrange(f"home:{user_id}", 0, limit - 1)
        if not tweet_ids:
            return []

        # get tweet hashes in a pipeline
        pipe = self.r.pipeline(transaction=False)
        for tid in tweet_ids:
            pipe.hgetall(f"tweet:{tid}")
        rows = pipe.execute()

        # convert redis hashes into Tweet objects
        out: List[Tweet] = []
        for d in rows:
            if not d:
                continue
            out.append(Tweet(
                tweet_id=int(d["tweet_id"]),
                user_id=int(d["user_id"]),
                tweet_ts=d["ts_ms"],
                tweet_text=d["text"]
            ))
        return out

    # ---- professor-style aliases (camelCase) ----
    def postTweet(self, user_id: int, tweet_text: str) -> int:
        return self.post_tweet(user_id, tweet_text)

    def getTimeline(self, user_id: int, limit: int = 10) -> List[Tweet]:
        return self.get_home_timeline(user_id, limit)

    def close(self):
        """
        Close redis connection/pool
        Different from MySQL - there is no self.db
        """
        try:
            self.r.close()
        except Exception:
            pass