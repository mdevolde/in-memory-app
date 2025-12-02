from singlestoredb import connection
from typing import List, Tuple, Any
import time

conn = connection.connect(
    host="localhost", port=3306, user="root", password="test", database="test"
)


def init_schema() -> None:
    with conn.cursor() as cur:
        cur.execute("""
          CREATE TABLE IF NOT EXISTS events (
            event_id VARCHAR(50) PRIMARY KEY,
            user_id INT,
            event_type VARCHAR(50),
            event_ts DOUBLE
          );
        """)
        conn.commit()


def insert_event(event_id: str, user_id: int, event_type: str, ts: float) -> None:
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO events(event_id, user_id, event_type, event_ts) VALUES (%s, %s, %s, %s)",
            (event_id, user_id, event_type, ts),
        )
    conn.commit()


def query_recent_events(since_ts: float) -> List[Tuple[Any, ...]]:
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM events WHERE event_ts >= %s", (since_ts,))
        return cur.fetchall()  # type: ignore


if __name__ == "__main__":
    init_schema()
    insert_event("evt2", 111, "login", time.time())
    print(query_recent_events(time.time() - 3600))
