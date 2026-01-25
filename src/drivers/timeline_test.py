import random
import time

from src.api.twitter_mysql import TwitterMySQL
from src.api.dbutils import get_connection

def get_candidate_users(limit: int = 200_000):
    sql = "SELECT DISTINCT follower_id FROM follows LIMIT %s"
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(sql, (limit,))
        return [row[0] for row in cur.fetchall()]

def main(iterations: int = 50_000, progress_every: int = 5_000, seed: int = 42):
    random.seed(seed)
    api = TwitterMySQL()

    users = get_candidate_users()
    if not users:
        raise RuntimeError("No users found in follows. Did you load follows.csv?")

    # ONE connection for the entire benchmark
    with get_connection() as conn:
        # Warmup
        for _ in range(50):
            api.get_home_timeline_conn(conn, random.choice(users))

        t0 = time.perf_counter()
        for i in range(1, iterations + 1):
            u = random.choice(users)
            _ = api.get_home_timeline_conn(conn, u)

            if i % progress_every == 0:
                elapsed = time.perf_counter() - t0
                print(f"{i:,} timeline calls in {elapsed:.2f}s  ({i/elapsed:.2f} calls/sec)")

        elapsed = time.perf_counter() - t0
        print(f"\nDONE: {iterations:,} getHomeTimeline calls in {elapsed:.2f}s => {iterations/elapsed:.2f} calls/sec")

if __name__ == "__main__":
    main()