# src/api/twitter_mysql.py

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

from src.api.dbutils import get_connection


@dataclass(frozen=True)
class Tweet:
    tweet_id: int
    user_id: int
    tweet_ts: str          # keep as str to avoid datetime parsing overhead
    tweet_text: str


class TwitterMySQL:
    """
    MySQL implementation of the Twitter API required by the assignment.

    - post_tweet: inserts ONE tweet at a time (no batching), and the DB auto-assigns
      tweet_id + timestamp.  [oai_citation:1‡twitter_rdb (1).pdf](sediment://file_000000000910722f908413d6fc77d46b)
    - get_home_timeline: returns 10 most recent tweets posted by users followed by user_id.
       [oai_citation:2‡twitter_rdb (1).pdf](sediment://file_000000000910722f908413d6fc77d46b)
    """

    def post_tweet(self, user_id: int, tweet_text: str) -> int:
        """
        Inserts a tweet (one at a time). Returns the new tweet_id.
        Assumes schema: tweet(tweet_id AUTO_INCREMENT PK, user_id, tweet_ts, tweet_text)
        """
        sql = """
            INSERT INTO tweet (user_id, tweet_ts, tweet_text)
            VALUES (%s, NOW(), %s)
        """
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (user_id, tweet_text))
            conn.commit()
            return cur.lastrowid

    def get_home_timeline(self, user_id: int, limit: int = 10) -> List[Tweet]:
        """
        Home timeline = 10 most recent tweets from people this user follows.  [oai_citation:3‡twitter_rdb (1).pdf](sediment://file_000000000910722f908413d6fc77d46b)
        """
        sql = """
            SELECT t.tweet_id, t.user_id, t.tweet_ts, t.tweet_text
            FROM follows f
            JOIN tweet t
              ON t.user_id = f.followee_id
            WHERE f.follower_id = %s
            ORDER BY t.tweet_ts DESC
            LIMIT %s
        """
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (user_id, limit))
            rows = cur.fetchall()

        return [Tweet(tweet_id=r[0], user_id=r[1], tweet_ts=str(r[2]), tweet_text=r[3]) for r in rows]

    # Optional helpers (nice for debugging / extensions)
    def get_followees(self, user_id: int) -> List[int]:
        sql = "SELECT followee_id FROM follows WHERE follower_id = %s"
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (user_id,))
            return [r[0] for r in cur.fetchall()]

    def get_tweets_by_user(self, user_id: int, limit: int = 10) -> List[Tweet]:
        sql = """
            SELECT tweet_id, user_id, tweet_ts, tweet_text
            FROM tweet
            WHERE user_id = %s
            ORDER BY tweet_ts DESC
            LIMIT %s
        """
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (user_id, limit))
            rows = cur.fetchall()
        return [Tweet(tweet_id=r[0], user_id=r[1], tweet_ts=str(r[2]), tweet_text=r[3]) for r in rows]