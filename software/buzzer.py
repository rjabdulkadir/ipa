"""
Functions to activate and deactivate the buzzer.
"""

from machine import Pin
import time

def init_buzzer():
    """
    Assign a ESP32 pin to the buzzer.

    Parameters:
    None

    Returns:
    buzzer (Pin): The pin object assigned to the buzzer.
    """
    buzzer = Pin(33, Pin.OUT, Pin.PULL_DOWN)
    buzzer.value(0) # initialize buffer to off
    return buzzer

def buzzer_on(buzzer):
    """
    Turn buzzer on.

    Parameters:
    buzzer (Pin): The pin assigned to the buzzer.

    Returns:
    None
    """
    buzzer.value(1)

def buzzer_off(buzzer):
    """
    Turn buzzer off.

    Parameters:
    buzzer (Pin): The pin assigned to the buzzer.

    Returns:
    None
    """
    buzzer.value(0)

def buzz(buzzer, buzz_length=100):
    """
    Turn on the buzzer for a specified period of time.

    Parameters:
    buzzer (Pin): The pin assigned to the buzzer.
    buzz_length (int): The duration the buzzer with be on in milliseconds.

    Returns:
    None
    """
    buzzer.value(1)
    time.sleep_ms(buzz_length)
    buzzer.value(0)

