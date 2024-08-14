"""
Functions related to GPRS connectivity.
"""

import time
import struct
import binascii
import re
from machine import Pin
from machine import UART
from sim808 import *
import pttconfigure


def send_at_command(serialPort: UART, commandString: str, waitTime: int) -> bytes:
    """
    Sends AT commands to the GPRS module and returns the result.

    Paramenters:
    serialPort (uart): The UART interface to the GSM/GPRS module.
    commandString (string): The AT command string.
    waitTime (int): The time to wait between sending the AT command
                    and reading the reply.

    Returns:
    replyString (string): The reply to the AT command.
    """
    serialPort.write(bytes(commandString, 'ascii') + b'\r\n')
    time.sleep(waitTime)
    replyString: bytes = b''
    replyChar: bytes  = serialPort.read(1)
    time.sleep_ms(20)
    while(replyChar != b"") and (replyChar != None):
        replyString = replyString + replyChar
        replyChar = serialPort.read()
        time.sleep_ms(20)
    return replyString


def set_ssl(uart):
    """
    Configures the module to communicate over SSL.

    Paramenters:
    uart (uart): The UART interface to the GSM/GPRS module.

    Returns:
    ssl_status (string): The result of the At command to set SSL connectivity.
    """
    ssl_status = send_at_command(uart, 'AT+CIPSSL=1', 1)
    return ssl_status


def extract_http_payload(file_data):
    """
    Extracts the HTTP content from the reponse.

    Parameters:
    file_data (string): The reponse from an HTTP request.

    Returns:
    file_data_payload (string): The extracted HTTP data.
    """
    # get content length from between Content-Length and Keep-Alive strings
    try:
        s_1 = re.search(b'Content-Length: [0-9]+\r\n', file_data)
        s_2 = re.search('[0-9]+', s_1.group(0))
        data_offset = int(s_2.group(0))
        if b'CLOSED' in file_data:
            file_data_payload = file_data[-data_offset-10:-10]
        else:
            file_data_payload = file_data[-data_offset:-1]

        return file_data_payload
    except:
        return None


def init_simcom(uart):
    """
    Activate the GSM/GPRS module.

    Parameters:
    uart (uart): The UART interface to the GSM/GPRS module.

    Returns:
    init_status (string): The result of the command to activate.
    """
    dtr_pin = Pin(13, Pin.OUT)
    dtr_pin.value(0)
    time.sleep(0.2)
    init_status = send_at_command(uart, 'at+cfun=1', 1)
    return init_status


def init_simcom_gprs(serialPort, timeout=5):
    """
    Activate mobile data on the GSM/GPRS module.

    Parameters:
    serialPort (uart): The UART interface to the GSM/GPRS module.
    timeout (int): Maximum time (sec) to wait for activation.

    Returns:
    gprs_ib_obj (string): ip address if successful (none otherwise).
    """
    gprsStatus = send_at_command(serialPort, 'at+cifsr', 1)
    gprs_ip_obj = re.search('\w*\.\w*\.\w*\.\w*', gprsStatus)
    t = 0
    while gprs_ip_obj is None and t < timeout:
        send_at_command(serialPort, 'at+cstt="ETC"', 1)
        send_at_command(serialPort, 'at+ciicr', 1)
        gprsStatus = send_at_command(serialPort, 'at+cifsr', 1)
        print('GPRS Status: ', gprsStatus)
        gprs_ip_obj = re.search('\w*\.\w*\.\w*\.\w*', gprsStatus)
        time.sleep(1)
        t += 1
    return gprs_ip_obj


def init_simcom_http(serialPort, connection_attempts=10,
        ip_address=pttconfigure.get_conf_param('server_ip_address'), port='443'):
    """
    Initialize an HTTPS session.

    Parameters:
    serialPort (uart): The UART interface to the GSM/GPRS module.
    connection_attempts (int): Number of tries to initiate the session.
    ip_address (string): The server ip address (or host name).
    port (string): The port to connect (443 is standard https port).

    Returns:
    (boolean): Success or faliure of the attempt.
    """
    serialPort.read()
    no_tries = 0
    result = b''
    while no_tries < connection_attempts and ((b'CONNECT OK' not in result) and (b'ALREADY CONNECT' not in result)):
        print('Connecting to server...', result)
        result = send_at_command(
            serialPort, 'at+cipstart="TCP","' + str(ip_address, 'ascii') + '","' + port + '"', 2)
        no_tries += 1
    print('at+cipstart="TCP","' + str(ip_address, 'ascii') + '","' + port + '"')
    #return result
    if no_tries == connection_attempts:
        return False
    return True


def send_simcom_http_query(serialPort,
        url_path='/ayer_admin/order', 
        keep_alive=True,
        empty_read_count=100):
    """
    Sends an HTTPS request.

    Parameters:
    serialPort (uart): The UART interface to the GSM/GPRS module.
    url_parth (string): The url path for the request.
    keep_alive (bool): Include/Not-include keep-alive request in the http header.
    empty_read_count (int): number of empty data reads before terminating the request.

    Returns:
    http_data (string): The data returned by the server for the HTTPS request.
    """
    connect_wait = 0
    result = b''
    while connect_wait < 50 and b'>' not in result:
        # print('Connecting to HTTP server...')
        result = send_at_command(serialPort, b'at+cipsend', 1)
        connect_wait += 1
        time.sleep(0.2)
    if result == b'':
        return b''
    serialPort.write(b'GET ' + url_path + b' HTTP/1.0\r\n')
    if keep_alive:
        serialPort.write('Connection: keep-alive\r\n')
    serialPort.write('\r\n\r\n\x1a')
    time.sleep(0.5)
    httpResult = serialPort.read(128)
    time.sleep(0.1)
    http_data = b''
    empty_read_counts = 0
    while empty_read_counts < empty_read_count:
        # print('HTTP Result: ', httpResult)
        httpResult = serialPort.read(128)
        if httpResult is None:
            empty_read_counts = empty_read_counts + 1
        if httpResult is not None:
            http_data = http_data + httpResult
            if b'CLOSED' in http_data:
                break
            empty_read_counts = 0
        time.sleep(0.1)
    return http_data


def get_ntp_time(uart):
    """
    Get the Network Time Protocol (NTP) time.

    Parameters:
    uart (uart): The UART interface to the GSM/GPRS module.

    Returns:
    ntp_time (string): The NTP date and time.
    """
    network_register_status = register_network(uart, timeout=5)
    #print('Registration Status: ', network_register_status)
    time.sleep(3)
    data_connect_status = init_simcom_gprs(uart)
    #print('Data Connect Status: ', data_connect_status)
    if data_connect_status != None:
        send_at_command(uart, 'AT+SAPBR=1,1', 1)
        send_at_command(uart, 'AT+CNTPCID=1', 1)
        #print('NTP bear profile...')
        #send_at_command(uart, 'AT+CNTP="0.africa.pool.ntp.org", 12', 1)
        send_at_command(uart, 'AT+CNTP="time.google.com", 12', 1)
        #print('Set NTP service...')
        send_at_command(uart, 'AT+CNTP', 1)
        #print('Sync NTP time...')
        ntp_time = send_at_command(uart, 'AT+CCLK?', 1)
        return ntp_time
    return None


def parse_ntp_time(ntp_time):
    """
    Extract date and time parameters from datetime string.

    Parameters:
    ntp_time (string): Datetime string returned by NTP request.

    Returns:
    (tuple): Separated date and time values.
    """
    try:
        ntp_date_time = ntp_time.split(b'"')[1]
        ntp_year = int(ntp_date_time[0:2]) + 2000
        ntp_month = int(ntp_date_time[3:5])
        ntp_day_of_month = int(ntp_date_time[6:8])
        ntp_day_of_week = 0
        ntp_hour = int(ntp_date_time[9:11])
        ntp_minute = int(ntp_date_time[12:14])
        ntp_second = int(ntp_date_time[15:17])
        ntp_millisecond = 0
        return ntp_year, ntp_month, ntp_day_of_month, ntp_day_of_week, ntp_hour, ntp_minute, ntp_second, ntp_millisecond
    except:
        return None
