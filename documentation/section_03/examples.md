## Example snippets

# Read Keys

```python
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

# Display Bitmap

```python
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
# Send SMS
```python
import sim808
import sms

gsm_uart = sim808.init_sim808()
gsm_status = sim808.register_network(gsm_uart, timeout=10)
if gsm_status:
	sms.send_sms('Hi there!', '555896345')
else:
	print('Unable to register on the mobile network')
```
# Receive SMS
```python
import sim808
import sms

gsm_uart = sim808.init_sim808()
gsm_status = sim808.register_network(gsm_uart, timeout=10)
if gsm_status:
	message = sms.read_sms()
	print(message)
else:
	print('Unable to register on the mobile network')
```
# Send HTTPS GET/POST
```python
import sim808
import gprs

# get gsm uart interface
gsm_uart = sim808.init_sim808()

# turn module on
sim808.pwr_on()

# activate module
sim808.activate_gsm(gsm_uart)

# register module to network
status = sim808.register_network(gsm_uart)
print('registered to ntk: ', status)

# Example Usage
get_url = 'https://httpbin.org/ip'
post_url = 'https://httpbin.org/post'
post_data = '{"title":"test","body":"hello","userId":1}'

print("GET Request:")
print(gprs.https_request(gsm_uart, "GET", get_url))

print("POST Request:")
print(gprs.https_request(gsm_uart, "POST", post_url, data=post_data))

```

