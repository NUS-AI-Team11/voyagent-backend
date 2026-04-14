"""
Abstract base class for all agents.
"""

from abc import ABC, abstractmethod
from typing import Any
import logging
from datetime import datetime
import time

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
        raise NotImplementedError("Subclasses must implement process()")

    def validate_input(self, context: PlanningContext) -> bool:
        """
        Validate input data.

        Args:
            context: planning context

        Returns:
            True if valid
        """
        return True

    def pre_process(self, context: PlanningContext) -> None:
        """Optional hook executed before process()."""

    def post_process(self, context: PlanningContext) -> None:
        """Optional hook executed after process()."""

    def execute(self, context: PlanningContext) -> PlanningContext:
        """
        Unified execution wrapper for all agents.

        This method standardizes validation, timing, logging, and error handling
        while keeping process() focused on business logic.
        """
        start_time = time.perf_counter()

        initial_error_count = len(context.errors)

        try:
            if not self.validate_input(context):
                context.add_error(f"{self.name}: input validation failed")
                self.log_execution("Input validation failed", level="error")
                return context

            self.pre_process(context)
            context = self.process(context)
            self.post_process(context)

            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            has_new_errors = len(context.errors) > initial_error_count
            status = "failed" if has_new_errors else "success"
            self._record_run_metadata(context, status, elapsed_ms)
            if has_new_errors:
                self.log_execution(f"Completed with errors in {elapsed_ms} ms", level="error")
            else:
                self.log_execution(f"Completed in {elapsed_ms} ms")

        except Exception as exc:
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            context.add_error(f"{self.name}: execution failed - {str(exc)}")
            self._record_run_metadata(context, "failed", elapsed_ms, str(exc))
            self.log_execution(f"Execution failed in {elapsed_ms} ms: {str(exc)}", level="error")

        return context

    def _record_run_metadata(
        self,
        context: PlanningContext,
        status: str,
        elapsed_ms: float,
        error: str = "",
    ) -> None:
        """Append agent run metadata into shared context."""
        if "agent_runs" not in context.metadata:
            context.metadata["agent_runs"] = []

        context.metadata["agent_runs"].append(
            {
                "agent": self.name,
                "status": status,
                "elapsed_ms": elapsed_ms,
                "timestamp": datetime.now().isoformat(),
                "error": error,
            }
        )

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
