"""WIFI

Defines functions for WIFI related tasks
"""
import network
import time


def wifi_isconnected():
    """Check wifi connection

    This function checks if wifi is connected
    returning a boolean for it.

    Returns:
        bool -- True/False
    """
    sta_if_check = network.WLAN(network.STA_IF)
    return sta_if_check.isconnected()


def wifi_scan(iface):
    """Scan wifi

    This functions scans for wifi connection
    points and retuns a list of ESSIDs

    Arguments:
        iface {obj} -- network.WIFI STA_IF interface object

    Returns:
        list -- list of ESSIDs
    """
    if not iface.active():
        iface.active(True)
    return iface.scan()


def do_wifi_disconnect(iface, deactivate=False):
    """Disconnects connected wifi

    This function does what the name actually indicates

    Arguments:
        iface {obj} -- network.WIFI STA_IF interface object

    Keyword Arguments:
        deactivate {bool} -- deactivate wifi capabilities (default: {False})

    Raises:
        e -- Any or network exception
    """
    try:
        iface.disconnect()
        if deactivate:
            iface.active(False)
    except Exception as e:
        pass


def do_wifi_connect(essid, passwd):
    """Connect to the given wifi ESSID

    This function stands for what the name indicates.
    It takes the essid and passwword to try and connect
    to that node in the network.

    Arguments:
        essid {str} -- ESSID
        passwd {str} -- wifi password

    Raises:
        e -- Any or network exception
    Return:
        network interface object
    """
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    print('connecting to network...')
    tries = 0
    while not sta_if.isconnected() and tries < 10:
        tries += 1
        print('Attempting network connection... ', tries)
        try:
            sta_if.active(True)
            sta_if.connect(essid, passwd)
            print('network config:', sta_if.ifconfig())
        except:
            sta_if.disconnect()
            sta_if.active(False)
        time.sleep(1)
    return sta_if

