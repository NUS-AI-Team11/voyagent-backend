"""
Abstract base class for all agents.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging
from datetime import datetime

from models.schemas import PlanningContext


class BaseAgent(ABC):
    """Abstract base class for all agents."""

    def __init__(self, name: str, description: str = ""):
        """
        Initialize the agent.

        Args:
            name: agent name
            description: agent description
        """
        self.name = name
        self.description = description
        self.logger = logging.getLogger(self.__class__.__name__)
        self.created_at = datetime.now()

    @abstractmethod
    def process(self, context: PlanningContext) -> PlanningContext:
        """
        Main method for processing the planning context.

        Args:
            context: shared planning context

        Returns:
            updated planning context
        """
        pass

    def validate_input(self, context: PlanningContext) -> bool:
        """
        Validate input data.

        Args:
            context: planning context

        Returns:
            True if valid
        """
        return True

    def log_execution(self, message: str, level: str = "info") -> None:
        """
        Log an execution message.

        Args:
            message: log message
            level: log level
        """
        log_func = getattr(self.logger, level.lower(), self.logger.info)
        log_func(f"[{self.name}] {message}")

    def __str__(self) -> str:
        return f"{self.name} - {self.description}"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.name}>"
