This project implements and benchmarks a simplified Twitter backend using MySQL. The goal is to measure how well a relational database handles basic Twitter-style workloads at scale.

Schema

The database uses two tables:
	•	TWEET (tweet_id, user_id, tweet_ts, tweet_text)
	•	FOLLOWS (follower_id, followee_id)

Indexes are added to support fast joins and timeline queries.

Data Loading
	•	follows.csv is loaded into the FOLLOWS table.
	•	Tweets are loaded from tweets.csv, one at a time (no batch inserts), until 1,000,000 tweets are inserted.
	•	Tweet IDs and timestamps are assigned by the database.

API

The core API is implemented in TwitterMySQL:
	•	postTweet(user_id, tweet_text) inserts a single tweet.
	•	getTimeline(user_id) returns the 10 most recent tweets from users that the given user follows.

All SQL is encapsulated in the API layer.

Benchmarking

Two benchmarks are run:
	•	postTweet throughput: measures single-tweet insert performance (calls/sec).
	•	getHomeTimeline throughput: measures timeline query performance after 1M tweets are loaded.

Timeline benchmarks reuse a single database connection to avoid connection overhead.

Results

Throughput is reported in API calls per second for:
	•	postTweet
	•	getHomeTimeline

Notes

Performance is affected by indexing, transaction overhead from one-at-a-time inserts, caching effects, and hardware limitations.
