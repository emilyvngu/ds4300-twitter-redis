import csv
from src.api.twitter_redis import TwitterRedis

CSV_PATH = "data/follows.csv"

def main():
    """
    Load the follow graph from follows.csv into Redis

    How redis storage model used:
    - followees:<follower_id> = SET of followee_ids that this user follows
    - followers:<followee_id> = SET of follower_ids who follow this user
    - users = SET of user_ids (used for randomly sampling users in benchmarks)
    """
    api = TwitterRedis()
    r = api.r

    # open CSV and detect header row
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        first = f.readline()
        f.seek(0)
        has_header = any(ch.isalpha() for ch in first)

        if has_header:
             # reads rows as dictionaries using header names as keys
            reader = csv.DictReader(f)
            for row in reader:
                # take first two columns regardless of exact header names
                keys = list(row.keys())

                # formatting
                follower = str(int(row[keys[0]]))
                followee = str(int(row[keys[1]]))

                # store both directions of the relationship in Redis sets
                r.sadd(f"followees:{follower}", followee)
                r.sadd(f"followers:{followee}", follower)

                # track users for benchmarking
                r.sadd("users", follower)

        else:
            # no header version:
            reader = csv.reader(f)
            for follower, followee in reader:
                follower = str(int(follower))
                followee = str(int(followee))
                r.sadd(f"followees:{follower}", followee)
                r.sadd(f"followers:{followee}", follower)
                r.sadd("users", follower)

    api.close()

if __name__ == "__main__":
    main()