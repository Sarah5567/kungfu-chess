from abc import ABC, abstractmethod
from typing import Any

class Handler(ABC):
    """
    Abstract base class for all handlers that process client messages.
    """

    @abstractmethod
    def handle(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Process a message from a client.

        Args:
            data (dict): The input message from the client.

        Returns:
            dict: The response message to be sent back to the clients.
        """
        pass
