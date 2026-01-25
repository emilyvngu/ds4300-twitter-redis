import csv
from src.api.dbutils import get_connection

CSV_PATH = "data/follows.csv"

def main():
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        with get_connection() as conn:
            cur = conn.cursor()

            count = 0
            for row in reader:
                follower_id = row[list(row.keys())[0]]
                followee_id = row[list(row.keys())[1]]
                
                if not follower_id or not followee_id:
                    continue

                cur.execute(
                    "INSERT IGNORE INTO follows (follower_id, followee_id) VALUES (%s, %s)",
                    (int(follower_id), int(followee_id))
                )

                count += 1
                if count % 10000 == 0:
                    print(f"Inserted {count} follows")

            conn.commit()

    print(f"Done. Inserted {count} follows.")

if __name__ == "__main__":
    main()