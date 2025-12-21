"""
GPIO Controller Module.
Provides hardware control for the kiosk lock mechanism.
"""

from typing import Optional

import gpiod
from gpiod.line import Direction, Value


class GPIOController:
    """
    Controller for GPIO-based lock mechanism.

    Attributes:
        chip: The GPIO chip device path.
        line_number: The GPIO line number to control.
    """

    def __init__(self, chip: str, line_number: int) -> None:
        """
        Initialize the GPIOController with a specific chip and line number.

        Args:
            chip: GPIO chip device path (e.g., '/dev/gpiochip0').
            line_number: GPIO line number to control.
        """
        self.chip: str = chip
        self.line_number: int = line_number
        self.request: Optional[gpiod.LineRequest] = None
        self.request_line()

    def request_line(self) -> None:
        """Request control of the GPIO line."""
        self.request = gpiod.request_lines(
            self.chip,
            consumer="Kiosk-Lock",
            config={
                self.line_number: gpiod.LineSettings(
                    direction=Direction.OUTPUT, output_value=Value.INACTIVE
                )
            },
        )

    def activate(self) -> None:
        """Set the GPIO line to HIGH (active)."""
        if self.request:
            self.request.set_value(self.line_number, Value.ACTIVE)

    def deactivate(self) -> None:
        """Set the GPIO line to LOW (inactive)."""
        if self.request:
            self.request.set_value(self.line_number, Value.INACTIVE)

    def cleanup(self) -> None:
        """Release the control of the GPIO line."""
        if self.request:
            self.request.release()
            self.request = None
