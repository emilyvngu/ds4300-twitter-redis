import csv
from src.api.twitter_redis import TwitterRedis

CSV_PATH = "data/follows.csv"

def main():
    api = TwitterRedis()
    r = api.r

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        first = f.readline()
        f.seek(0)
        has_header = any(ch.isalpha() for ch in first)

        if has_header:
            reader = csv.DictReader(f)
            for row in reader:
                keys = list(row.keys())
                follower = str(int(row[keys[0]]))
                followee = str(int(row[keys[1]]))
                r.sadd(f"followees:{follower}", followee)
                r.sadd(f"followers:{followee}", follower)
                r.sadd("users", follower)
        else:
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