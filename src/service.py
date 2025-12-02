from typing import Dict, Any, List
from backend_interface import BackendInterface


def add_event(backend: BackendInterface, event: Dict[str, Any]) -> None:
    """
    Inserts an event via the chosen backend.
    """
    backend.insert_event(event["event_id"], event)


def get_event_by_id(backend: BackendInterface, event_id: str) -> Dict[str, Any] | None:
    """
    Retrieves an event by its ID.
    """
    return backend.get_event(event_id)


def get_user_events(backend: BackendInterface, user_id: int) -> List[Dict[str, Any]]:
    """
    Retrieves all events for a user.
    """
    return backend.query_events_by_user(user_id)


def clear_backend(backend: BackendInterface) -> None:
    """
    Clears all stored data — useful for benchmarks.
    """
    backend.clear()