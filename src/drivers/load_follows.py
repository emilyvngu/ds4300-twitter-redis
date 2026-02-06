import csv
from src.api.dbutils import DBUtils

CSV_PATH = "data/follows.csv"

def main():
    """
    Load the follow graph from follows.csv into the MySQL FOLLOWS table

    Each row represents: follower_id follows followee_id
    """
    db = DBUtils.from_env()
    sql = "INSERT INTO FOLLOWS (follower_id, followee_id) VALUES (%s, %s)"

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        
        # Insert rows one at a time
        for row in reader:
            db.insert_one(sql, (int(row["follower_id"]), int(row["followee_id"])))

    db.close()

