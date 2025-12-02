from pymemcache.client.base import Client  # type: ignore
import json
import time
from typing import Dict, Any, Optional

client = Client(("localhost", 11211))


def store_event(event_id: str, event: Dict[str, Any]) -> None:
    client.set(event_id, json.dumps(event))


def get_event(event_id: str) -> Optional[Dict[str, Any]]:
    val = client.get(event_id)
    if val is None:
        return None
    return json.loads(val)


if __name__ == "__main__":
    e: Dict[str, Any] = {"user_id": 123, "type": "login", "timestamp": time.time()}
    store_event("evt1", e)
    print(get_event("evt1"))
