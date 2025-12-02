from singlestoredb import connection
from typing import Dict, Any, List, Optional
from backend_interface import BackendInterface


class SingleStoreBackend(BackendInterface):
    def __init__(
        self,
        host: str = "localhost",
        port: int = 3306,
        user: str = "root",
        password: str = "test",
        database: str = "test",
    ):
        self.conn = connection.connect(
            host=host, port=port, user=user, password=password, database=database
        )
        self.init_schema()

    def init_schema(self) -> None:
        with self.conn.cursor() as cur:
            cur.execute("""
              CREATE TABLE IF NOT EXISTS events (
                event_id VARCHAR(50) PRIMARY KEY,
                user_id INT,
                event_type VARCHAR(50),
                event_ts DOUBLE
              );
            """)
            self.conn.commit()

    def insert_event(self, event_id: str, event: Dict[str, Any]) -> None:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO events(event_id, user_id, event_type, event_ts)
                VALUES (%s, %s, %s, %s)
            """,
                (
                    event["event_id"],
                    event["user_id"],
                    event["event_type"],
                    event["timestamp"],
                ),
            )
        self.conn.commit()

    def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT event_id, user_id, event_type, event_ts FROM events WHERE event_id=%s",
                (event_id,),
            )
            row = cur.fetchone()  # type: ignore

        if row is None:
            return None

        return {
            "event_id": row[0],  # type: ignore
            "user_id": row[1],  # type: ignore
            "event_type": row[2],  # type: ignore
            "timestamp": row[3],  # type: ignore
        }

    def query_events_by_user(self, user_id: int) -> List[Dict[str, Any]]:
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT event_id, user_id, event_type, event_ts FROM events WHERE user_id = %s",
                (user_id,),
            )
            rows = cur.fetchall()  # type: ignore

        return [
            {
                "event_id": r[0],  # type: ignore
                "user_id": r[1],  # type: ignore
                "event_type": r[2],  # type: ignore
                "timestamp": r[3],  # type: ignore
            }
            for r in rows  # type: ignore
        ]

    def clear(self) -> None:
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM events;")
        self.conn.commit()
