from machine import Pin
import time

def init_buzzer():
    buzzer = Pin(33, Pin.OUT, Pin.PULL_DOWN)
    buzzer.value(0)

    return buzzer

def buzzer_on(buzzer):
    buzzer.value(1)

def buzzer_off(buzzer):
    buzzer.value(0)

def buzz(buzzer, buzz_length=100):
    buzzer.value(1)
    time.sleep_ms(buzz_length)
    buzzer.value(0)

