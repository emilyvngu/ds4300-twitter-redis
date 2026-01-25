from src.api.dbutils import get_connection

def main():
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT DATABASE();")
        print("Connected to DB:", cur.fetchone()[0])

if __name__ == "__main__":
    main()