from src.api.dbutils import DBUtils
from src.api.twitter_mysql import TwitterMySQL
import random
import time

def get_candidate_users(limit: int = 200_000):
    """
    Return a list of follower_ids to sample from during the benchmark.
    """
    # Create a short DB connection just to fetch candidate users
    db = DBUtils.from_env()
    df = db.execute(f"SELECT DISTINCT follower_id FROM FOLLOWS LIMIT {limit}")
    db.close()
    return df["follower_id"].tolist()

def main(iterations: int = 50_000, progress_every: int = 5_000, seed: int = 42):
    # Make random sampling
    random.seed(seed)

    # Create ONE DBUtils + API, and reuse the same connection for the whole benchmark
    db = DBUtils.from_env()
    api = TwitterMySQL(db)

    # Get list of users to randomly sample from
    users = get_candidate_users()

    # If no users exist, the benchmark isn't meaningful
    if not users:
        db.close()
        raise RuntimeError("No users found in follows. Did you load follows.csv?")

    conn = db.con  # <-- persistent connection from DBUtils

    try:
        # Warmup
        for _ in range(50):
            api.get_home_timeline_conn(conn, random.choice(users))

        #start timer
        t0 = time.perf_counter()

        # Choose a random follower_id each iteration, execute the timeline query, and print running throughout 
        for i in range(1, iterations + 1):
            u = random.choice(users)
            _ = api.get_home_timeline_conn(conn, u)

            if i % progress_every == 0:
                elapsed = time.perf_counter() - t0
                print(f"{i:,} timeline calls in {elapsed:.2f}s  ({i/elapsed:.2f} calls/sec)")

        # Final throughput
        elapsed = time.perf_counter() - t0
        print(f"\nDONE: {iterations:,} getHomeTimeline calls in {elapsed:.2f}s => {iterations/elapsed:.2f} calls/sec")

    finally:
        db.close()

if __name__ == "__main__":
    main()