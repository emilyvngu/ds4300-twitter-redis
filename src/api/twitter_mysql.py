from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional

from src.api.dbutils import DBUtils


@dataclass(frozen=True)
class Tweet:
    tweet_id: int
    user_id: int
    tweet_ts: str
    tweet_text: str


class TwitterMySQL:
    def __init__(self, db: Optional[DBUtils] = None):
        self.db = db if db is not None else DBUtils.from_env()

    # ---- your existing API (snake_case) ----
    def post_tweet(self, user_id: int, tweet_text: str) -> int:
        sql = """
            INSERT INTO TWEET (user_id, tweet_ts, tweet_text)
            VALUES (%s, NOW(), %s)
        """
        cur = self.db.con.cursor()
        try:
            cur.execute(sql, (user_id, tweet_text))
            self.db.con.commit()
            return cur.lastrowid
        finally:
            cur.close()

    def get_home_timeline(self, user_id: int, limit: int = 10) -> List[Tweet]:
        sql = """
            SELECT t.tweet_id, t.user_id, t.tweet_ts, t.tweet_text
            FROM FOLLOWS f
            JOIN TWEET t ON t.user_id = f.followee_id
            WHERE f.follower_id = %s
            ORDER BY t.tweet_ts DESC
            LIMIT %s
        """
        cur = self.db.con.cursor()
        try:
            cur.execute(sql, (user_id, limit))
            rows = cur.fetchall()
        finally:
            cur.close()

        return [Tweet(r[0], r[1], str(r[2]), r[3]) for r in rows]

    def get_home_timeline_conn(self, conn, user_id: int, limit: int = 10):
        sql = """
            SELECT t.tweet_id, t.user_id, t.tweet_ts, t.tweet_text
            FROM FOLLOWS f
            JOIN TWEET t ON t.user_id = f.followee_id
            WHERE f.follower_id = %s
            ORDER BY t.tweet_ts DESC
            LIMIT %s
        """
        cur = conn.cursor()
        try:
            cur.execute(sql, (user_id, limit))
            return cur.fetchall()
        finally:
            cur.close()

    # ---- professor-style aliases (camelCase) ----
    def postTweet(self, user_id: int, tweet_text: str) -> int:
        return self.post_tweet(user_id, tweet_text)

    def getTimeline(self, user_id: int, limit: int = 10) -> List[Tweet]:
        return self.get_home_timeline(user_id, limit)

    def close(self):
        self.db.close()