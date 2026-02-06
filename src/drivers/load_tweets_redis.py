import csv
import time
from src.api.twitter_redis import TwitterRedis

CSV_PATH = "data/tweet.csv"

def main(max_tweets=1_000_000, progress_every: int = 10_000):
    """
    Load tweets from a CSV file into the database by calling the Twitter API
    It does this one at a time

    """
    api = TwitterRedis()

    n = 0

    #timer start
    t0 = time.perf_counter()

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        # DictReader auto-handles headers; if there is no header,
        # it will treat first row as header (bad). So we detect.
        first_line = f.readline()
        f.seek(0)

        # If the first line contains letters, it’s probably a header
        has_header = any(ch.isalpha() for ch in first_line)  # crude but effective
        reader = csv.DictReader(f) if has_header else csv.reader(f)

        # Read and insert rows one by one:
        for row in reader:
            try:
                if has_header:
                    # take first column as user_id, second column as tweet text (works even if header names vary)
                    keys = list(row.keys())
                    user_id = int(row[keys[0]])
                    tweet_text = row[keys[1]]
                else:
                    user_id = int(row[0])
                    tweet_text = row[1]

                if tweet_text is None:
                    continue

                tweet_text = tweet_text.strip()
                if not tweet_text:
                    continue

                # One-at-a-time insert (required by assignment)  [oai_citation:1‡twitter_rdb (1).pdf](sediment://file_000000000910722f908413d6fc77d46b)
                api.post_tweet(user_id, tweet_text)

                n += 1
                if n % progress_every == 0:
                    elapsed = time.perf_counter() - t0
                    print(f"Inserted {n:,} tweets in {elapsed:.2f}s  ({n/elapsed:.2f} calls/sec)")

                # Stop once we reach the max tweet target
                if n >= max_tweets:
                    break

            except Exception as e:
                # skip malformed rows safely
                continue

    # Final result
    elapsed = time.perf_counter() - t0
    print(f"\nDONE: Inserted {n:,} tweets in {elapsed:.2f}s => {n/elapsed:.2f} postTweet calls/sec")

if __name__ == "__main__":
    main()