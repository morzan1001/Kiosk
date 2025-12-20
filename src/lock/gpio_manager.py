from src.lock.lock import GPIOController
from src.logmgr import logger

GPIO_CONTROLLER = None


def initialize_gpio(chip="/dev/gpiochip0", line_number=4):
    global GPIO_CONTROLLER
    try:
        logger.debug(
            f"Initializing GPIOController with chip {chip} and line {line_number}"
        )
        GPIO_CONTROLLER = GPIOController(chip, line_number)
        logger.info("GPIO started successfully")
        GPIO_CONTROLLER.deactivate()  # Close Lock by default
    except Exception as e:
        logger.error("Error starting GPIO: ", e)
        raise


def get_gpio_controller() -> GPIOController:
    if GPIO_CONTROLLER is None:
        logger.error("GPIO Controller is not initialized")
    return GPIO_CONTROLLER


def cleanup_gpio():
    if GPIO_CONTROLLER:
        try:
            GPIO_CONTROLLER.cleanup()
            logger.info("GPIO cleanup done")
        except Exception as e:
            logger.error(f"Error during GPIO cleanup: {e}")
