from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class BackendInterface(ABC):
    @abstractmethod
    def insert_event(self, event_id: str, event: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def query_events_by_user(self, user_id: int) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def clear(self) -> None:
        """Remove all stored data."""
        pass
