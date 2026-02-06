import random
import time
from src.api.twitter_redis import TwitterRedis

def get_candidate_users(limit: int = 200_000):
    """
    Return a list of user_ids to sample from during the benchmark
    - since load_follows_redis.py populated a Redis set named 'users'
    """
    api = TwitterRedis()
    users = list(api.r.smembers("users"))
    api.close()

    # convert to ints + cap
    users = [int(u) for u in users][:limit]
    return users

def main(iterations: int = 50_000, progress_every: int = 5_000, seed: int = 42):
    # Make random sampling
    random.seed(seed)

    api = TwitterRedis()

    # Get list of users to randomly sample from
    users = get_candidate_users()

    # If no users exist, the benchmark isn't meaningful
    if not users:
        api.close()
        raise RuntimeError("No users found in Redis set 'users'. Did you run load_follows_redis.py?")

    try:
        # Warmup
        for _ in range(50):
            api.get_home_timeline(random.choice(users))

        #start timer
        t0 = time.perf_counter()

        # Choose a random follower_id each iteration, execute the timeline query, and print running throughout 
        for i in range(1, iterations + 1):
            u = random.choice(users)
            _ = api.get_home_timeline(u)

            if i % progress_every == 0:
                elapsed = time.perf_counter() - t0
                print(f"{i:,} timeline calls in {elapsed:.2f}s  ({i/elapsed:.2f} calls/sec)")

        # Final throughput
        elapsed = time.perf_counter() - t0
        print(f"\nDONE: {iterations:,} getTimeline calls in {elapsed:.2f}s => {iterations/elapsed:.2f} calls/sec")

    finally:
        api.close()

if __name__ == "__main__":
    main()