from machine import Pin

def buttons_init():
    buttons = {}
    buttons['t2'] = Pin(35, Pin.IN)
    buttons['t3'] = Pin(4, Pin.IN)
    buttons['t1'] = Pin(2, Pin.IN)
    #buttons['t3'] = Pin(35, Pin.IN)
    #buttons['t1'] = Pin(4, Pin.IN)
    #buttons['t2'] = Pin(2, Pin.IN)

    return buttons 


def get_buttons_touched(buttons):
    buttons_touched = [buttons[button].value() for button in buttons]

    return buttons_touched

