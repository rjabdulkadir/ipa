"""
Defines functions to get input from touch buttons.
"""

from machine import Pin

def buttons_init():
    """
    Assigns ESP32 pins to touch buttons.

    Parameters:
    None

    Returns:
    buttons (dict): The pin assignments of each button.
    """
    buttons = {}
    buttons['t2'] = Pin(35, Pin.IN)
    buttons['t3'] = Pin(4, Pin.IN)
    buttons['t1'] = Pin(2, Pin.IN)
    #buttons['t3'] = Pin(35, Pin.IN)
    #buttons['t1'] = Pin(4, Pin.IN)
    #buttons['t2'] = Pin(2, Pin.IN)
    return buttons 


def get_buttons_touched(buttons):
    """
    Determines which buttons have been touched.

    Parameters:
    buttons (dict): The pins assigned to each touch button.

    Returns:
    buttons_touched (dict): The values for each button (1 if touched 0 if not)
    """
    buttons_touched = [buttons[button].value() for button in buttons]
    return buttons_touched

