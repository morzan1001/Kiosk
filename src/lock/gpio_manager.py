from src.logmgr import logger
from src.lock import GPIOController

gpio_controller = None

def initialize_gpio(chip="/dev/gpiochip4", line_number=4):
    global gpio_controller
    try:
        logger.debug(f"Initializing GPIOController with chip {chip} and line {line_number}")
        gpio_controller = GPIOController(chip, line_number)
        logger.info("GPIO started successfully")
        gpio_controller.deactivate() # Close Lock by default
    except Exception as e:
        logger.error("Error starting GPIO: ", e)
        raise

def get_gpio_controller():
    global gpio_controller
    if gpio_controller is None:
        logger.error("GPIO Controller is not initialized")
    return gpio_controller

def cleanup_gpio():
    global gpio_controller
    if gpio_controller:
        try:
            gpio_controller.cleanup()
            logger.info("GPIO cleanup done")
        except Exception as e:
            logger.error(f"Error during GPIO cleanup: {e}")