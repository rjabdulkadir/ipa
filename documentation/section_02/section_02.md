
## Using the REPL

The Read Evaluate Print Loop (REPL) allows you to enter a Python command which is then evaluated by the interpreter and the result of the evaluation printed out. The REPL is very useful to check out Python commands or short pieces of code. 

```
>>> # addition
>>> 1 + 1
2
>>> # division
>>> 3 / 2
1.5
>>> # function definition
>>> def my_cube (x):
		return x * x * x
>>> my_cube(3)
27
>>> # ESP32 module
>>> import esp32
>>> esp32.mcu_temperature
33
>>> # connect to an access point
>>> import network
>>> wlan = network.WLAN(network.WLAN.IF_STA) # create station interface
>>> wlan.active(True)       # activate the interface
True
>>> wlan.scan()             # scan for access points
[(b'your_ssid'), ...]
>>> wlan.isconnected()      # check if the station is connected to an AP
False
>>> wlan.connect('your_ssid', 'your_key') # connect to an AP (replace your_ssid and your_key with those of you WiFi network)
>>> wlan.isconnected()
True
>>> wlan.config('mac')      # get the interface's MAC address
b'a MAC address'        # will return the MAC address of the WiFi interface 
>>> wlan.ipconfig('addr4')  # get the interface's IPv4 addresses
('ip address', 'netmask')   # will return a tuple with the ip address and netmask

# send an HTTP GET request and retrieve a web page
>>> import requests
>>> result = requests.get('http://www.google.com')
>>> result.text
'<!doctype html><html itemscope="" itemtype="http://schema.org/WebPage"...lots of HTTP markup
```
Micropython implements much of Python 3.4. However not all functionality and libraries are implemented. On the other hand different board or microcontroller specific functions are incorporated as shown above. Full details are available on the Micropython documentation pages.





