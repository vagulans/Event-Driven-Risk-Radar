from abc import ABC, abstractmethod
from typing import List

from edrr.models.events import Event


class EventSource(ABC):
    """Abstract base class for all event sources."""

    @abstractmethod
    async def fetch_events(self) -> List[Event]:
        """Fetch events from this source.
        
        Returns:
            List of Event objects from this source.
        """
        pass

    @abstractmethod
    def get_source_name(self) -> str:
        """Get the name of this event source.
        
        Returns:
            A string identifying this source.
        """
        pass
