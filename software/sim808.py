"""
Functions for GSM connectivity.
"""

from machine import UART, Pin
import time

def init_sim808():
    """
    activates the module and returns a UART object.

    Parameters:
    None

    Returns:
    gsm_uart (uart): The UART object used to communicate with the module.
    """
    dtr_pin = Pin(13, Pin.OUT)
    gsm_uart = UART(1, baudrate=9600, bits=8, parity=None, stop=1, rx=27, tx=14)
    gsm_uart.write(b'at+csclk=1\r\n')
    time.sleep_ms(1500)
    dtr_pin.value(0)
    time.sleep_ms(1000)
    return gsm_uart


def pwr_on():
    """ Turns on the module.
    """
    pwr_pin = Pin(25, Pin.OUT)
    pwr_pin.value(1)
    time.sleep_ms(100)
    pwr_pin.value(0)
    time.sleep_ms(1200)
    pwr_pin.value(1)


def pwr_off():
    """ power off the module by pulling down
    the PWRKEY pin for at least 1.5 second
    and release.
    """
    pwr_pin = Pin(25, Pin.OUT)
    pwr_pin.value(0)
    time.sleep_ms(1600)
    pwr_pin.value(1)
    time.sleep_ms(100)


def activate_gsm(gsm_uart):
    """
    Activate mobile network connectivity.

    Parameters:
    gsm_uart (uart): The GSM module UART interface.

    Returns:
    result (string): The result of the AT command to activate the module.
    """
    gsm_uart.write(b'at+csclk=1\r\n')
    time.sleep_ms(500)
    dtr_pin = Pin(13, Pin.OUT)
    dtr_pin.value(0)
    time.sleep(0.1)
    gsm_uart.write(b'at+cfun=1\r\n')
    time.sleep(0.1)
    gsm_uart.write(b'at+cfun=1,1\r\n')
    time.sleep(0.1)
    result = gsm_uart.read()
    time.sleep_ms(100)
    return result


def deactivate_gsm(gsm_uart):
    """
    Deactivate mobile network connectivity (and set to low power mode).

    Parameters:
    gsm_uart (uart): The GSM module UART interface.

    Returns:
    result (string): The result of the AT command to deactivate the module.
    """
    dtr_pin = Pin(13, Pin.OUT)
    gsm_uart.write(b'at+csclk=1\r\n')
    time.sleep_ms(1500)
    gsm_uart.write(b'at+cfun=4\r\n')
    time.sleep_ms(1500)
    dtr_pin.value(1)
    time.sleep_ms(300)
    result = gsm_uart.read()
    return result


def get_power_status(gsm_uart):
    """
    Get information on the charge of the connected battery.

    Parameters:
    gsm_uart (uart): The GSM module UART interface.

    Returns:
    result (tuple): The values - charging status, charge level, voltage (mV).
    """
    #gsm_uart.write(b'at+cfun=0\r\n')
    time.sleep_ms(100)
    result = gsm_uart.read()
    dtr_pin = Pin(13, Pin.OUT)
    dtr_pin.value(0)
    #time.sleep_ms(100)
    battery_level = None
    while battery_level == None:
        gsm_uart.write(b'at+cbc\r\n')
        time.sleep_ms(100)
        result = gsm_uart.read(32)
        try:
            data_offset_pos = result.find(b':')
            charging_status = int(result[data_offset_pos + 2: data_offset_pos + 3])
            charge_level = int(result[data_offset_pos + 4: data_offset_pos + 6])
            charge_mv = int(result[data_offset_pos + 7: data_offset_pos + 11])
            battery_level =  charging_status, charge_level, charge_mv
        except:
            battery_level = 0, 0, 0
    return battery_level


def get_gprs_status(gsm_uart):
    """
    Query the status of the GPRS mobile network connection.

    Parameters:
    gsm_uart (uart): The GSM module UART interface.

    Returns:
    (boolean): The status of the GPRS connection.
    """
    gsm_uart.write(b'at+cgatt?\r\n')
    time.sleep_ms(100)
    result = gsm_uart.read()
    try:
        if b'+CGATT: 1' in result:
            return True
        else:
            return False
    except:
        return False


def get_registration_status(gsm_uart):
    """
    Query the status of the mobile network registration.

    Parameters:
    gsm_uart (uart): The GSM module UART interface.

    Returns:
    (boolean): The registration status.
    """
    gsm_uart.write(b'at+creg?\r\n')
    time.sleep_ms(500)
    result = gsm_uart.read()
    try:
        if (b'+CREG: 1,1' in result) or (b'+CREG: 0,1' in result):
            return True
        else:
            return False
    except:
        return False


def register_network(gsm_uart, timeout=10):
    """
    Register on the mobile network.

    Parameters:
    gsm_uart (uart): The GSM module UART interface.
    timeout (int): Number of attempts to register.

    Returns:
    result (boolean): The status of the registration attempt.
    """
    t = 0
    result = get_registration_status(gsm_uart)
    time.sleep(0.1)
    # print('Reg status: ', result)
    while not result and t < timeout:
        # print('Registering... ')
        gsm_uart.write(b'at+cfun=1\r\n')
        time.sleep(1)
        result = get_registration_status(gsm_uart)
        time.sleep(1)
        # print('Reg status: ', result)
        t += 1
        if result:
            gsm_uart.write(b'at+cfun=1,1\r\n')
            time.sleep(5)
    #if not result:
        # print('REGISTRATION FAILED!')
    return result

