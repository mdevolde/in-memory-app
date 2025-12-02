from pymemcache.client.base import Client  # type: ignore
import json
from typing import Dict, Any, Optional, List

from backend_interface import BackendInterface


class MemcachedBackend(BackendInterface):
    def __init__(self, host: str = "localhost", port: int = 11211):
        self.client = Client((host, port))

    def insert_event(self, event_id: str, event: Dict[str, Any]) -> None:
        self.client.set(event_id, json.dumps(event))

    def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        val = self.client.get(event_id)
        if val is None:
            return None
        return json.loads(val)

    def query_events_by_user(self, user_id: int) -> List[Dict[str, Any]]:
        results = []
        return results  # type: ignore

    def clear(self) -> None:
        self.client.flush_all()
