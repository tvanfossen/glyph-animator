"""Base class for processing pipelines."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

TInput = TypeVar("TInput")
TOutput = TypeVar("TOutput")

logger = logging.getLogger(__name__)


class PipelineBase(ABC, Generic[TInput, TOutput]):
    """Base class for multi-step processing pipelines.

    Subclasses implement execute() which chains algorithm steps.
    The base provides logging of step transitions.
    """

    @abstractmethod
    def execute(self, input_data: TInput) -> TOutput:
        """Run the full pipeline on input_data."""

    def _log_step(self, step_name: str, detail: str = "") -> None:
        msg = f"[{self.__class__.__name__}] {step_name}"
        if detail:
            msg += f": {detail}"
        logger.info(msg)
