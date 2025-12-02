import time
import random
import uuid
from typing import Dict, Any


EVENT_TYPES = ["login", "logout", "page_view", "purchase", "click"]


def generate_event(user_id: int | None = None,
                   event_type: str | None = None) -> Dict[str, Any]:
    """
    Generates a simple and consistent event.
    Used in the CLI and in the benchmark.

    :param user_id: explicit user id (otherwise generated randomly)
    :param event_type: explicit type (otherwise chosen randomly)
    """

    event: Dict[str, Any] = {
        "event_id": uuid.uuid4().hex,
        "user_id": user_id if user_id is not None else random.randint(1, 10000),
        "event_type": event_type if event_type else random.choice(EVENT_TYPES),
        "timestamp": time.time(),
    }

    return event


def generate_events_batch(n: int) -> list[Dict[str, Any]]:
    """
    Generates a batch of N events, useful for benchmarks
    requiring local pre-loading before insertion.

    :param n: number of events
    """
    return [generate_event() for _ in range(n)]
