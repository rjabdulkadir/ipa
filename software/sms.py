"""SMS

Defines functions for SMS communication

Variables:
    SUCCESS {int} -- success
    FAILURE {int} -- failure
    uart {[type]} -- UART object
    sms_text {str} -- SMS text
    destination_number {str} -- destination phone number
"""

import time
from machine import UART

SUCCESS = 1
FAILURE = 0

uart = UART(1, baudrate=9600, bits=8, parity=None, stop=1, rx=27, tx=14)
sms_text = ''
destination_number = ''


def init_sms(text, phone_number):
    """Initiate SMS

    This function initiates a text message
    by take the text and destination phone
    number before the call to the send_sms
    method.

    Arguments:
        text {str} -- text string to send
        phone_number {str} -- destination phone number

    Returns:
        int -- 0 on failure, 1 on success
    """
    global sms_text, destination_number
    sms_text = text
    destination_number = phone_number
    if sms_text == '' or destination_number == '':
        return FAILURE
    return SUCCESS


def send_at_command(commandString, waiting_time=0):
    """Runs all AT Commands and returns a byte string.

    This takes a mandatory command_string and optional waiting_time parameters

    Arguments:
        command_string {str} -- AT Command string with proper closing marks

    Keyword Arguments:
        waiting_time {int|float} -- waiting time for the command execution (default: {0})

    Returns:
        str -- byte string
    """
    uart.write(commandString)
    time.sleep(waiting_time)
    replyString = b''
    replyChar = uart.read(1)
    while (replyChar):
        replyString = replyString + replyChar
        replyChar = uart.read()
    return replyString


def read_sms(index=None):
    """Read SMS

    This function reads (a) text message(s) from the
    device and returns if any. If index is passed as
    an argument then it will try to get the SMS at that
    index.

    Keyword Arguments:
        index {int} -- SMS index (default: {None})

    Returns:
        bytestr -- all or a single text message depending on
                    argument index
    """
    set_cmgf_mode()
    msg = ''
    if index is None:
        msg = send_at_command('AT+CMGL="ALL"\r\n', 2)
    else:
        msg = send_at_command('AT+CMGR=%s\r\n' % index, 0.5)
    return msg


def set_cmgf_mode(mode=1):
    """Set SMS mode

    This function sets the SMS mode

    Keyword Arguments:
        mode {int} -- SMS access mode (default: {1})
    """
    send_at_command('AT+CMGF=%s\r\n' % mode, 0.1)


def get_cmgf_mode():
    """Get SMS mode

    This function is used to get the current SMS access mode.

    Returns:
        bytestr -- a byte sting of current CMGF mode
    """
    mode = send_at_command('AT+CMGF?\r\n', 0.1)
    return mode


def send_sms():
    """Send SMS

    This method gets the variables set in init_sms
    and tries to send to the destination.

    Returns:
        int -- 0 on failure, 1 on success
    """
    # set cmgf mode to 1
    try:
        set_cmgf_mode()
        print(sms_text, destination_number)
        # command to serial port uart.write('AT+CMGS="%s"\r' % destination_number)
        # uart.write('AT+CMGS="%s"\r' % destination_number)
        send_at_command('AT+CMGS="%s"\r' % destination_number, 0.2)
        # command to serial port uart.write('%s' % sms_text)
        send_at_command('%s' % sms_text, 0.2)
        # command to serial port uart.write('\x1a')
        send_at_command('\x1a', 4)
        # command to serial port uart.write('\r\n')
        send_at_command('\r\n', 1)
        return SUCCESS
    except Exception as e:
        return FAILURE

