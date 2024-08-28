import gpiod

class GPIOController:
    """Initialize the GPIOController with a specific chip and line number."""
    def __init__(self, chip, line_number):
        self.chip = gpiod.chip(chip)
        self.line_number = line_number
        self.line = self.chip.get_line(self.line_number)
        config = gpiod.line_request()
        config.consumer = 'Kiosk-Lock'
        config.request_type = gpiod.line_request.DIRECTION_OUTPUT
        self.line.request(config)

    def activate(self):
        """Set the GPIO line to HIGH (active)."""
        self.line.set_value(1)

    def deactivate(self):
        """Set the GPIO line to LOW (inactive)."""
        self.line.set_value(0)  

    def cleanup(self):
        """Release the control of the GPIO line."""
        self.line.release() 
