import random
import time
from src.api.twitter_redis import TwitterRedis

def get_candidate_users(limit: int = 200_000):
    """
    Return a list of user_ids to sample from during the benchmark.
    We assume load_follows_redis.py populated a Redis set named 'users'.
    """
    api = TwitterRedis()
    users = list(api.r.smembers("users"))
    api.close()

    # convert to ints + cap
    users = [int(u) for u in users][:limit]
    return users

def main(iterations: int = 50_000, progress_every: int = 5_000, seed: int = 42):
    random.seed(seed)

    api = TwitterRedis()
    users = get_candidate_users()

    if not users:
        api.close()
        raise RuntimeError("No users found in Redis set 'users'. Did you run load_follows_redis.py?")

    try:
        # Warmup
        for _ in range(50):
            api.get_home_timeline(random.choice(users))

        t0 = time.perf_counter()
        for i in range(1, iterations + 1):
            u = random.choice(users)
            _ = api.get_home_timeline(u)  # or api.getTimeline(u)

            if i % progress_every == 0:
                elapsed = time.perf_counter() - t0
                print(f"{i:,} timeline calls in {elapsed:.2f}s  ({i/elapsed:.2f} calls/sec)")

        elapsed = time.perf_counter() - t0
        print(f"\nDONE: {iterations:,} getTimeline calls in {elapsed:.2f}s => {iterations/elapsed:.2f} calls/sec")

    finally:
        api.close()

if __name__ == "__main__":
    main()