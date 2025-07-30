from abc import ABC, abstractmethod
from typing import Any

from shared.Piece import Piece


class Handler(ABC):
    """
    Abstract base class for all handlers that process client messages.
    """

    @abstractmethod
    def handle(self, params: dict[str, Any]) -> dict[str, Any] | None:
        """
        Process a message from a client.

        Args:
            :param pieces:
            :param params:
        Returns:
            dict: The response message to be sent back to the clients.

        """
        pass
