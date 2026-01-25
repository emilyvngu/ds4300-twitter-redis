from src.api.twitter_mysql import TwitterMySQL

def main():
    api = TwitterMySQL()

    # Post a tweet as ds4300 user_id 1 (pick any int you want)
    new_id = api.post_tweet(1, "catch me outside how bout that")
    print("Inserted tweet_id:", new_id)

    # Fetch timeline for user 1 (will show tweets from accounts user 1 follows)
    timeline = api.get_home_timeline(1)
    print("Timeline length:", len(timeline))
    for t in timeline[:3]:
        print(t)

if __name__ == "__main__":
    main()