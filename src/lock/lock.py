import gpiod
from gpiod.line import Direction, Value

class GPIOController:
    """Initialize the GPIOController with a specific chip and line number."""
    def __init__(self, chip, line_number):
        self.chip = chip
        self.line_number = line_number
        self.request = None
        self.request_line()

    def request_line(self):
        self.request = gpiod.request_lines(
            self.chip,
            consumer="Kiosk-Lock",
            config={
                self.line_number: gpiod.LineSettings(
                    direction=Direction.OUTPUT, 
                    output_value=Value.INACTIVE
                )
            }
        )

    def activate(self):
        """Set the GPIO line to HIGH (active)."""
        self.request.set_value(self.line_number, Value.ACTIVE)

    def deactivate(self):
        """Set the GPIO line to LOW (inactive)."""
        self.request.set_value(self.line_number, Value.INACTIVE)

    def cleanup(self):
        """Release the control of the GPIO line."""
        if self.request:
            self.request.release()