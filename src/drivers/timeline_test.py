from src.api.dbutils import DBUtils
from src.api.twitter_mysql import TwitterMySQL
import random
import time

def main(iterations: int = 50_000, progress_every: int = 5_000, seed: int = 42):
    random.seed(seed)

    # Create ONE DBUtils + API, and reuse the same connection for the whole benchmark
    db = DBUtils.from_env()
    api = TwitterMySQL(db)

    users = get_candidate_users()
    if not users:
        db.close()
        raise RuntimeError("No users found in follows. Did you load follows.csv?")

    conn = db.con  # <-- persistent connection from DBUtils

    try:
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

    finally:
        db.close()

if __name__ == "__main__":
    main()