"""Base protocol for custom imageplot layers."""
from __future__ import annotations

from abc import ABC, abstractmethod
from matplotlib.axes import Axes


class Layer(ABC):
    """An object that knows how to draw itself on Matplotlib axes."""

    @abstractmethod
    def draw(self, ax: Axes):
        """Draw the layer and return the created Matplotlib artist(s)."""
