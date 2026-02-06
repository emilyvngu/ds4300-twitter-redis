# DS4300 Twitter Backend – MySQL (HW1) + Redis (HW2)

This project implements and benchmarks a simplified Twitter backend using two storage approaches:

- **HW1 (MySQL / RDBMS):** relational tables + SQL join for timelines  
- **HW2 (Redis):** key–value storage with a precomputed home timeline (“fan-out on write”)

The goal is to measure how each backend performs under basic Twitter-style read and write workloads at scale (reported in **API calls/sec**).

---

## MySQL (HW1)

### Schema
The MySQL database consists of two tables:
- **TWEET** (`tweet_id`, `user_id`, `tweet_ts`, `tweet_text`)
- **FOLLOWS** (`follower_id`, `followee_id`)

Indexes are included to support faster timeline queries (joins + ordering).

### Data Loading
- `data/follows.csv` is loaded into the `FOLLOWS` table.
- Tweets are loaded from `data/tweet.csv` **one at a time** (no batch inserts) until **1,000,000 tweets** are inserted.
- Tweet IDs and timestamps are assigned by MySQL (`AUTO_INCREMENT`, `NOW()`).

### API
Implemented in `src/api/twitter_mysql.py` (`TwitterMySQL`):
- `postTweet(user_id, tweet_text)` inserts a tweet into MySQL.
- `getTimeline(user_id)` returns the 10 most recent tweets from users the given user follows (SQL join + sort).

### Benchmarking
- **postTweet throughput:** measures single-tweet insert performance (calls/sec)
- **getHomeTimeline throughput:** measures timeline query performance after tweets are loaded  
Timeline benchmarks reuse a single DB connection to avoid measuring connection overhead.

---

## Redis (HW2)

### Storage Model (Keys + Data Structures)
Redis stores the same information using key categories and native data structures:

- `tweet:id` → **STRING counter** used to generate unique `tweet_id` values (`INCR`)
- `tweet:<tweet_id>` → **HASH** storing the tweet fields (`tweet_id`, `user_id`, `ts_ms`, `text`)
- `followers:<user_id>` → **SET** of users who follow this user
- `followees:<user_id>` → **SET** of users this user follows
- `users` → **SET** of user ids used for benchmarking user sampling
- `home:<user_id>` → **SORTED SET (ZSET)** of tweet_id references, scored by timestamp (newest first)

### Design Choice: References vs. Full Tweet Copies
For timelines, I store **tweet_id references** inside `home:<user_id>` instead of copying full tweet text into every timeline. This reduces storage duplication while still allowing fast reads by fetching the 10 tweet hashes for a timeline request.

### Fan-out on Write (Fast Reads)
Redis uses a “fan-out on write” approach:
- On `postTweet`, the tweet is stored once (`tweet:<tweet_id>`), then the tweet ID is inserted into each follower’s home timeline (`home:<follower_id>`).
- On `getTimeline`, the API reads the 10 newest tweet IDs from `home:<user_id>` and looks up the tweet hashes to return tweet objects.

### Data Loading
- `data/follows.csv` is loaded into Redis sets (`followers:*`, `followees:*`, and `users`).
- Tweets are loaded via the Redis API (`postTweet`) so that home timelines are created as tweets are posted.

### API
Implemented in `src/api/twitter_redis.py` (`TwitterRedis`):
- `postTweet(user_id, tweet_text)` stores tweet data and updates followers’ home timelines.
- `getTimeline(user_id)` returns the 10 most recent tweets from the user’s Redis home timeline.

### Benchmarking
- **postTweet throughput:** measures tweet write speed while performing fan-out updates
- **getTimeline throughput:** measures timeline read speed from precomputed home timelines

---

## Results
Performance is reported in **API calls per second** for:
- `postTweet`
- `getTimeline` (MySQL timeline join vs. Redis home timeline)

---

## Tools / Environment
- **Python**
- **MySQL** (HW1)
- **Redis** + **Redis CLI (`redis-cli`)** (HW2)
- VS Code, Git/GitHub

---

## Notes
Performance depends on indexing (MySQL), fan-out cost (Redis writes), one-at-a-time inserts, caching effects, and hardware limits. Redis generally shifts work from reads to writes (writes become heavier; reads become faster due to precomputed timelines).