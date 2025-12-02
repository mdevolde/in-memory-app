from dataclasses import dataclass
from typing import Dict, Any
import time
import uuid


@dataclass
class Event:
    event_id: str
    user_id: int
    event_type: str
    timestamp: float

    @staticmethod
    def new(user_id: int, event_type: str) -> "Event":
        """
        Creates a new event with a unique ID and current timestamp.
        """
        return Event(
            event_id=uuid.uuid4().hex,
            user_id=user_id,
            event_type=event_type,
            timestamp=time.time(),
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the event to a dictionary
        for storage in Memcached or SingleStore.
        """
        return {
            "event_id": self.event_id,
            "user_id": self.user_id,
            "event_type": self.event_type,
            "timestamp": self.timestamp,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Event":
        """
        Rebuilds an event from a dict.
        """
        return Event(
            event_id=data["event_id"],
            user_id=data["user_id"],
            event_type=data["event_type"],
            timestamp=data["timestamp"],
        )
