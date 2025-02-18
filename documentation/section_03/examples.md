## Example snippets

# Read keys

```
import time
import buttons

# initialize button pins
button_obj = buttons.buttons_init()

# read keys
while True:
    # get the pin value for each buttons
    touched_buttons = buttons.get_buttons_touched(button_obj)
    # if a pin is touched its value cange from 0 to 1 
    for index, value in enumerate(touched_buttons):
        if value == 1:
            print(f'key {index} touched.')
    # scan every 300 millisecond
    time.sleep(0.3)
```

# Display bitmap

```
import ui_lcd

# Initialize LCD
display, fbuf = ui_lcd.display_init()

# initialize lcd backlight
display_pwm = ui_lcd.backlight_init()
# adjust brightness
display_pwm.duty(512)

# set bmp information
image_fbuf = ui_lcd.get_fbuf('ADC_RandD.bmp.zip')
x_pos, y_pos, width, height = 0, 0, 134, 240

# display the bitmap
ui_lcd.show_pixbuffer(display, image_fbuf, x_pos, y_pos, width, height)
```

# Send GSM/GPRS AT commands

```
import time
import sim808


gsm_uart = sim808.init_sim808()

# simple function to meke sending at commands easy
def send_at(command, delay=1):
    gsm_uart.write(command + '\r\n')
    time.sleep(delay)
    if gsm_uart.any():
        print(gsm_uart.read().decode())
```

# Send SMS via GSM

```
# turn module on
sim808.pwr_on()

# activate module
sim808.activate_gsm(gsm_uart)

# register module to network
sim808.register_network(gsm_uart)


# simple example function to send sms
def send_sms(phone_number, message):
    send_at('AT+CMGF=1')  # Set SMS mode to text
    send_at(f'AT+CMGS="{phone_number}"')
    gsm_uart.write(message + "\x1A")  # End SMS with CTRL+Z
    time.sleep(3)
    if gsm_uart.any():
        print(gsm_uart.read().decode())

# example usage
send_sms('+251....', 'Hello, this is a test message.')

```

# Receive SMS via GSM

- Make sure to turn on and initialize module properly

```
# simple example function to read sms inbox
def read_sms():
    send_at('AT+CMGF=1')  # Set SMS mode to text
    gsm_uart.write('AT+CMGL="ALL"\r\n') # read all messages
    time.sleep(3)
    if gsm_uart.any():
        response = gsm_uart.read().decode()
        print("Received SMS:", response)

# Example Usage
read_sms()
```

# Send HTTPS GET/POST requests via GPRS

 - Make sure to turn on and initialize module properly

```
# simple example function to send http request
def https_request(method, url, auth=None, data=None):
    # Initialize GPRS
    send_at('AT+SAPBR=3,1,"Contype","GPRS"\r\n')
    send_at('AT+SAPBR=3,1,"APN","ETC"\r\n')
    send_at('AT+SAPBR=1,1\r\n')
    send_at('AT+SAPBR=2,1\r\n')

    
    send_at('AT+HTTPINIT\r\n') # init http
    send_at('AT+HTTPPARA="CID",1\r\n')  # Set bearer profile identifier
    send_at(f'AT+HTTPPARA="URL","{url}"\r\n')
    send_at( 'AT+HTTPPARA="USERDATA", "Connection: keep-alive"\r\n')
    if auth is not None:
        send_at('AT+HTTPPARA="USERDATA", "Authorization:Basic %s"\r\n'%auth)
    
    send_at('AT+HTTPSSL=1\r\n')  # set ssl for https

    if method == "POST":
        send_at('AT+HTTPPARA="CONTENT","application/json"')
        send_at(f'AT+HTTPDATA={len(data)},10000')  # Specify data length
        gsm_uart.write(data)
        time.sleep(2)
        send_at('AT+HTTPACTION=1\r\n')  # 1 for POST
    else:
        send_at('AT+HTTPACTION=0\r\n')  # 0 for GET

    time.sleep(10)
    response = send_at('AT+HTTPREAD\r\n')  # Read server response
    
    send_at('AT+HTTPTERM\r\n')  # Terminate HTTP session
    
    return response


# Example Usage

get_url = 'https://httpbin.org/ip'
post_url = 'https://httpbin.org/post'
post_data = '{"title":"test","body":"hello","userId":1}'

print("GET Request:")
print(https_request("GET", get_url))

print("POST Request:")
print(https_request("POST", post_url, data=post_data))

```


=======
TBW
>>>>>>> dbe10596ad652aefabe3a65599ea73bc4d3468e3
