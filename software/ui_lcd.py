# LCD User interface module

from machine import Pin, SPI, PWM
import lcd 
import framebuf
import zlib
from menus_lcd import *

# Initialize LCD
def display_init():
    # Set SPI parameters
    spi=SPI(2, baudrate=40000000, polarity=1, sck=Pin(18), mosi=Pin(23), miso=Pin(19))
    # Set LCD parameters and initialize
    display=lcd.ST7789(spi, 135, 240, reset=Pin(19, Pin.OUT), dc=Pin(5, Pin.OUT))
    display.init()
    
    # Define frame buffer object for RGB565 format buffers
    fbuf = framebuf.FrameBuffer(bytearray(135 * 240 * 2), 135, 240, framebuf.RGB565)
    display.fill(0x0000) # Fill white background

    return display, fbuf


# initialize lcd backlight
def backlight_init():
    bl_pwm = PWM(Pin(15))
    bl_pwm.freq(1000)
    bl_pwm.duty(1023)
    return bl_pwm


# Get a framebuffer object from a bmp file
def get_fbuf(pixmap_file, compressed=True):
    try:
        with open(pixmap_file, 'rb') as f:
            data = bytearray(f.read())
            if compressed:
                data = zlib.decompress(data) # Decompress if compressed parameter True
        data_width = int.from_bytes(data[0x12:0x16], 'little') # Get width from file header
        data_height = int.from_bytes(data[0x16:0x1a], 'little') # Get height from file header
        data_pixels = data[138:] # Get pixel data after 138 header bytes
        pixmap_buffer = framebuf.FrameBuffer(data_pixels, data_width, data_height, framebuf.RGB565)
        return pixmap_buffer
    except:
        print('Pixmap file: ', pixmap_file, ' not found!')
        return None



# Display buffer
def show_pixbuffer(display, fbuf, x_pos=0, y_pos=0, width=135, height=240):
    display.blit_buffer(fbuf, x_pos, y_pos, width, height)
