import time
import struct
import binascii
import re
import ota_upgrade
from machine import Pin
from machine import UART
from sim808 import *
import pttconfigure



def send_at_command(serialPort: UART, commandString: str, waitTime: int) -> bytes:
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


def set_ssl(uart: UART) -> bytes:
    ssl_status = send_at_command(uart, 'AT+CIPSSL=1', 1)
    return ssl_status


def extract_http_payload(file_data):
    # get content length from between Content-Length and Keep-Alive strings
    try:
        """
        cl_start_pos = file_data.find(b'Content-Length')
        #cl_end_pos = file_data.find(b'Access-Control-Allow-Origin')
        cl_end_pos = file_data.find(b'Connection')
        content_length = int(file_data[cl_start_pos:cl_end_pos][16:-2])
        len_file_data = len(file_data)
        print('CL Start: ', cl_start_pos, 'Cl End: ', cl_end_pos,
              'Cont Len: ', content_length, 'Data len: ', len_file_data)
        #file_data_payload = file_data[len_file_data - content_length - 10:-10]
        file_data_payload = file_data[len_file_data - content_length:]
        """
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
    dtr_pin = Pin(13, Pin.OUT)
    dtr_pin.value(0)
    time.sleep(0.2)
    init_status = send_at_command(uart, 'at+cfun=1', 1)
    return init_status


def init_simcom_gprs(serialPort, timeout=5):
    #attach_status = send_at_command(serialPort, 'at+cgatt?', 1)
    #print('Attach status: ', attach_status)
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
        auth=True, username='wurii', password='dumbbell', keep_alive=True,
        empty_read_count=100):
    connect_wait = 0
    result = b''
    while connect_wait < 50 and b'>' not in result:
        print('Connecting to HTTP server...')
        result = send_at_command(serialPort, b'at+cipsend', 1)
        connect_wait += 1
        time.sleep(0.2)
    if result == b'':
        return b''
    serialPort.write(b'GET ' + url_path + b' HTTP/1.0\r\n')
    if keep_alive:
        serialPort.write('Connection: keep-alive\r\n')
    #if auth:
    #    auth_string = str(binascii.b2a_base64(username + ':' + password)[:-1], 'ascii')
        #serialPort.write('Authorization: Basic aXRyYWNrOml0cmFjaw==\r\n')
    #    serialPort.write('Authorization: Basic ' + auth_string + '\r\n')
    serialPort.write('\r\n\r\n\x1a')
    time.sleep(0.5)
    httpResult = serialPort.read(128)
    time.sleep(0.1)
    http_data = b''
    empty_read_counts = 0
    while empty_read_counts < empty_read_count:
        print('HTTP Result: ', httpResult)
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


def init_simcom_ntp(serialPort, ip_address='time.google.com', port='123'):
    result = send_at_command(
        serialPort, 'at+cipstart="UDP","' + ip_address + '","' + port + '"', 10)
    print('at+cipstart="TCP","' + ip_address + '","' + port + '"')
    return result


def send_simcom_ntp_query(serialPort):
    result = send_at_command(serialPort, b'at+cipsend', 1)
    time.sleep(1)
    REF_TIME_1970 = 2208988800
    ntp_request = b'\x1b' + 47 * b'\0'
    serialPort.write(ntp_request)
    time.sleep(1)
    ntp_data = serialPort.read(1024)
    time.sleep(3)
    print('NTP Data: ', ntp_data)
    if ntp_data:
        t = struct.unpack('!12I', ntp_data)[10]
        t -= REF_TIME_1970
    return t


def get_vouchers(uart, operator='ethiotelecom'):
    username=pttconfigure.get_conf_param('server_auth_user_name')
    password=pttconfigure.get_conf_param('server_auth_password')
    url_path=pttconfigure.get_conf_param('purchase_download_url')
    device_id=pttconfigure.get_conf_param('device_id')
    device_pass=pttconfigure.get_conf_param('device_password')
    connect_status = b''
    http_data = b''
    http_request = url_path + b'?IMEI=' + device_id + b'&PASSWORD=' + device_pass
    network_register_status = register_network(uart, timeout=5)
    print('Registration Status: ', network_register_status)
    if not network_register_status:
        return None
    time.sleep(3)
    data_connect_status = init_simcom_gprs(uart)
    print('Data Connect Status: ', data_connect_status)
    ssl_status = set_ssl(uart)
    print('SSL Status: ', ssl_status)
    if data_connect_status is not None:
        connect_status = init_simcom_http(uart)
        print('Connect Status: ', connect_status)
    #if b'CONNECT' in connect_status:
    if connect_status:
        http_data = send_simcom_http_query(uart, url_path=http_request, keep_alive=False)
        print('HTTP Data: ', http_data)
    return http_data


def send_order(uart, order_request):
    connect_status = b''
    http_data = b''
    network_register_status = register_network(uart, timeout=5)
    print('Registration Status: ', network_register_status)
    if not network_register_status:
        return None
    time.sleep(3)
    data_connect_status = init_simcom_gprs(uart)
    print('Data Connect Status: ', data_connect_status)
    ssl_status = set_ssl(uart)
    print('SSL Status: ', ssl_status)
    if data_connect_status is not None:
        connect_status = init_simcom_http(uart)
        print('Connect Status: ', connect_status)
    #if b'CONNECT' in connect_status:
    if connect_status:
        http_data = send_simcom_http_query(uart, url_path=order_request)
        print('HTTP Data: ', http_data)
    return http_data


def get_ntp_time(uart):
    network_register_status = register_network(uart, timeout=5)
    print('Registration Status: ', network_register_status)
    time.sleep(3)
    data_connect_status = init_simcom_gprs(uart)
    print('Data Connect Status: ', data_connect_status)
    if data_connect_status != None:
        send_at_command(uart, 'AT+SAPBR=1,1', 1)
        send_at_command(uart, 'AT+CNTPCID=1', 1)
        print('NTP bear profile...')
        #send_at_command(uart, 'AT+CNTP="0.africa.pool.ntp.org", 12', 1)
        send_at_command(uart, 'AT+CNTP="time.google.com", 12', 1)
        print('Set NTP service...')
        send_at_command(uart, 'AT+CNTP', 1)
        print('Sync NTP time...')
        ntp_time = send_at_command(uart, 'AT+CCLK?', 1)
        return ntp_time
    return None


def parse_ntp_time(ntp_time):
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


def upgrade_gprs(uart):
    username=pttconfigure.get_conf_param('server_auth_user_name')
    password=pttconfigure.get_conf_param('server_auth_password')
    url_path=pttconfigure.get_conf_param('upgrade_download_url')
    device_id=pttconfigure.get_conf_param('device_id'),
    device_pass=pttconfigure.get_conf_param('device_password')
    connect_status = b''
    http_data = b''
    file_data = b''
    file_hash = b''
    upgrades_success = False
    network_register_status = register_network(uart, timeout=5)
    print('Registration Status: ', network_register_status)
    if not network_register_status:
        return None
    time.sleep(3)
    data_connect_status = init_simcom_gprs(uart)
    print('Data Connect Status: ', data_connect_status)
    ssl_status = set_ssl(uart)
    print('SSL Status: ', ssl_status)
    if data_connect_status is not None:
        connect_status = init_simcom_http(uart)
        print('Connect Status: ', connect_status)
    #if b'CONNECT' in connect_status:
    if connect_status:
        http_data = send_simcom_http_query(uart,
            url_path=url_path + 'upgraded_files.txt', 
            auth=True, username='wurii', password='dumbbell')
        print('HTTP data: ', http_data)
        file_data = http_data.split(b'\r\n')[-1:][0]
        print('File data: ', file_data)
        print('Upgraded files: ', file_data)
        http_data = send_simcom_http_query(uart,
            url_path=url_path + 'upgraded_files.txt.sha1', 
            auth=True, username='wurii', password='dumbbell')
        file_hash = http_data.split(b'\r\n')[-1:][0]
        print('Upgraded files hash: ', file_hash)
    if ota_upgrade.check_integrity(file_data, file_hash):
        print('Lets continue...')
        files_list = file_data.split(b'\n')[:-1]
        all_good = True
        for file_name in files_list:
            print('File name: ', file_name)
            http_data = send_simcom_http_query(uart,
                url_path=url_path + str(file_name, 'ascii'),
                auth=True, username='wurii', password='dumbbell')
            content_length_match = re.search('Content-Length: \d+', http_data)
            content_length =  int(content_length_match.group(0).split(b':')[1])
            file_data = http_data[-content_length:]
            #file_data = http_data[http_data.find(b'Keep-Alive\r\n\r\n') + 14:]
            print('Retrieved file: ', http_data)
            http_data = send_simcom_http_query(uart,
                url_path=url_path + str(file_name + b'.sha1', 'ascii'),
                auth=True, username='wurii', password='dumbbell')
            content_length_match = re.search('Content-Length: \d+', http_data)
            content_length =  int(content_length_match.group(0).split(b':')[1])
            file_hash = http_data[-content_length:]
            #file_hash = http_data[http_data.find(b'Keep-Alve\r\n\r\n') + 14:]
            print('Retrieved file: ', http_data)
            if ota_upgrade.check_integrity(file_data, file_hash):
                print('Hooooooooray!!!!!')
                print('Writing: ', file_name + '.new')
                fh = open(file_name + '.new', 'w')
                fh.write(file_data)
                fh.close()
            else:
                print('Nooooooooooo!!!!!')
                all_good = False
                break
        if all_good:
			upgrades_success = ota_upgrade.apply_upgrades(files_list)
	return upgrades_success


def get_account(uart, rfid_tag_sn):
    get_account_url = pttconfigure.get_conf_param('get_account_url')
    full_account_path = get_account_url + rfid_tag_sn
    connect_status = b''
    http_data = b''
    network_register_status = register_network(uart, timeout=5)
    print('Registration Status: ', network_register_status)
    if not network_register_status:
        return None
    time.sleep(3)
    data_connect_status = init_simcom_gprs(uart)
    print('Data Connect Status: ', data_connect_status)
    ssl_status = set_ssl(uart)
    print('SSL Status: ', ssl_status)
    if data_connect_status is not None:
        connect_status = init_simcom_http(uart)
        print('Connect Status: ', connect_status)
    #if b'CONNECT' in connect_status:
    time.sleep(1)
    if connect_status:
        http_data = send_simcom_http_query(uart, url_path=full_account_path,
                empty_read_count=20, keep_alive=False)
        print('HTTP Data: ', http_data)
    return http_data


def confirm_order_download(uart, confirm_url):
    connect_status = b''
    http_data = b''
    network_register_status = register_network(uart, timeout=5)
    print('Registration Status: ', network_register_status)
    if not network_register_status:
        return None
    time.sleep(3)
    data_connect_status = init_simcom_gprs(uart)
    print('Data Connect Status: ', data_connect_status)
    ssl_status = set_ssl(uart)
    print('SSL Status: ', ssl_status)
    if data_connect_status is not None:
        connect_status = init_simcom_http(uart)
        print('Connect Status: ', connect_status)
    #if b'CONNECT' in connect_status:
    if connect_status:
        http_data = send_simcom_http_query(uart, url_path=confirm_url)
        print('HTTP Data: ', http_data)
    return http_data

