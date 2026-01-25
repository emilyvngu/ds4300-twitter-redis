class TwitterMySQLAPI:
    def post_tweet(self, user_id, tweet_text):
        ...
    def get_home_timeline(self, user_id):
        ...

if __name__ == "__main__":
    api = TwitterMySQLAPI()
    api.post_tweet(1, "catch me outside how bout that")
    print("tweet inserted")