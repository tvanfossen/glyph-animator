"""Abstract base class for all algorithms in the pipeline."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

TInput = TypeVar("TInput")
TOutput = TypeVar("TOutput")


class Algorithm(ABC, Generic[TInput, TOutput]):
    """Base class for provably correct mathematical algorithms.

    Every concrete algorithm must declare:
    - proof_reference: path to its proof document in docs/proofs/
    - complexity: Big-O complexity string
    - error_bound: worst-case error description
    - execute(): the computation itself

    Constructor parameters ARE the generation knobs — they map to
    tunable values in the proof document's YAML frontmatter.
    """

    @property
    @abstractmethod
    def proof_reference(self) -> str:
        """Path to the proof document, e.g. 'docs/proofs/01_bezier_evaluation.md'."""

    @property
    @abstractmethod
    def complexity(self) -> str:
        """Big-O complexity, e.g. 'O(1) per segment'."""

    @property
    @abstractmethod
    def error_bound(self) -> str:
        """Worst-case error description."""

    @abstractmethod
    def execute(self, input_data: TInput) -> TOutput:
        """Run the algorithm on input_data and return the result."""
