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


# Display menu pixmap
def show_menu_item(spi_display, fbuf, menu_title_code, menu_item_no, x_pos=0, y_pos=0):
    menu_title = menu_items[menu_title_code][0]
    menu_item = menu_items[menu_items[menu_title_code][1][menu_item_no]][0]
    menu_pixmap = menu_items[menu_items[menu_title_code][1][menu_item_no]][2][0]
    menu_x = menu_items[menu_items[menu_title_code][1][menu_item_no]][5][0]
    menu_y = menu_items[menu_items[menu_title_code][1][menu_item_no]][5][1]
    menu_w = menu_items[menu_items[menu_title_code][1][menu_item_no]][5][2]
    menu_h = menu_items[menu_items[menu_title_code][1][menu_item_no]][5][3]
    menu_pixmap_mode = menu_items[menu_items[menu_title_code][1][menu_item_no]][2][1]
    print('menu key: ', menu_title_code, 'x: ', menu_x, 'y: ', menu_y, 'w: ', menu_w, 'h: ', menu_h)

    # Display menu pixmap
    fbuf_pixmap = get_fbuf(menu_pixmap)
    len_menu_item = len(menu_items[menu_items[menu_title_code][1][menu_item_no]])
    if menu_items[menu_items[menu_title_code][1][menu_item_no]][8]:
        print('Clear/No Clear: ', menu_items[menu_items[menu_title_code][1][menu_item_no]][8])
        fbuf.fill_rect(0, 0, 134, 240, 0xffff)
    if len_menu_item != 11:
        fbuf.blit(fbuf_pixmap, menu_x, menu_y)
    print('Menu item length: ', len_menu_item)
    if len_menu_item == 11:
        for fbuffs in menu_items[menu_items[menu_title_code][1][menu_item_no]][10]:
            print('Pixmap file: ', fbuffs[0], fbuffs[1], fbuffs[2])
            fbuf_pixmap = get_fbuf(fbuffs[0])
            fbuf.blit(fbuf_pixmap, fbuffs[1], fbuffs[2])
            #show_pixbuffer(spi_display, fbuf, 0, 0, 135, 240)
    if not menu_items[menu_items[menu_title_code][1][menu_item_no]][6]:
        pix_buff = get_fbuf('bitmaps_compressed/Failed_action-565rfs.bmp.zip')
        #fbuf.fill_rect(20, 20, 95, 200, 0x8888)
        fbuf.blit(pix_buff, 8, 145)
    show_pixbuffer(spi_display, fbuf, 0, 0, 135, 240)



# Display indicator icon
def show_indicator(display, indicator_file='star-565.bmp', x_pos=113, y_pos=219):
    with open(indicator_file, 'rb') as f:
        f.read(138)
        f_data = f.read()
        icon_fbuf = framebuf.FrameBuffer(bytearray(f_data), 20, 20, framebuf.RGB565)
    show_pixbuffer(icon_fbuf, menu_x, menu_y, 20, 20)


# Display all indicators
def show_indicators(display):
    show_indicator(display, 'icons/cellular-565rf.bmp', 113, 218)
    show_indicator(display, 'icons/wifi-565rf.bmp', 113, 174)
    show_indicator(display, 'icons/battery-okay-565rf.bmp', 113, 130)
    show_indicator(display, 'iconsble-565rf.bmp', 113, 152)
    show_indicator(display, 'icons/etc-swapped-565rf.bmp', 113, 24)
    show_indicator(display, 'icons/etc-logo-swapped-565rf.bmp', 113, 2)
    show_indicator(display, 'icons/prs-data-off-565rf.bmp', 113, 196)


# Show Wi-Fi indicator
def show_wifi_indicator(display, check_wifi_cb, x_pos=113, y_pos=174):
    if check_wifi_cb():
        show_indicator(display, 'icons/wifi-565rf.bmp', x_pos, y_pos)
    else:
        show_indicator(display, 'icons/wifi-off-565rf.bmp', x_pos, y_pos)


# Show battery level indicator
def show_power_indicator(display, check_power_cb, x_pos=113, y_pos=130):
    if check_power_cb():
        show_indicator(display, 'icons/battery-okay-565rf.bmp', x_pos, y_pos)
    else:
        show_indicator(display, 'icons/battery-low-565rf.bmp', x_pos, y_pos)


# Show GPRS data indicator
def show_gprs_indicator(display, check_gprs_cb, x_pos=113, y_pos=196):
    if check_gprs_cb():
        show_indicator(display, 'icons/gprs-data-565rf.bmp', x_pos, y_pos)
    else:
        show_indicator(display, 'icons/gprs-data-off-565rf.bmp', x_pos, y_pos)


# Show mobile network registration indicator
def show_reg_indicator(display, check_reg_cb, x_pos=113, y_pos=218):
    if check_reg_cb():
        show_indicator(display, 'icons/cellular-565rf.bmp', x_pos, y_pos)
    else:
        show_indicator(display, 'icons/cellular-off-565rf.bmp', x_pos, y_pos)


# Show Blue Tooth indicator
def show_ble_indicator(display, check_ble_cb, x_pos=113, y_pos=152):
    if check_ble_cb():
        show_indicator(display, 'icons/ble-565rf.bmp', x_pos, y_pos)
    else:
        show_indicator(display, 'icons/ble-off-565rf.bmp', x_pos, y_pos)

def show_battery_level(display, fbuf, battery_level=100):
    #pix_buff = get_fbuf('bitmaps_compressed/battery0-565rfs.bmp.zip')
    pix_buff = None
    if battery_level >90 and battery_level <= 100:
        pix_buff = get_fbuf('bitmaps_compressed/Small_Battery_100-565rfs.bmp.zip')
    if battery_level >80 and battery_level <= 90:
        pix_buff = get_fbuf('bitmaps_compressed/Small_Battery_80-565rfs.bmp.zip')
    if battery_level >70 and battery_level <= 80:
        pix_buff = get_fbuf('bitmaps_compressed/Small_Battery_60-565rfs.bmp.zip')
    if battery_level >60 and battery_level <= 70:
        pix_buff = get_fbuf('bitmaps_compressed/Small_Battery_40-565rfs.bmp.zip')
    if battery_level >50 and battery_level <= 60:
        pix_buff = get_fbuf('bitmaps_compressed/Small_Battery_20-565rfs.bmp.zip')
    if pix_buff is not None:
        fbuf.blit(pix_buff, 98, 184, 0x0000)
        #show_pixbuffer(display, fbuf, x_pos=102, y_pos=186, width=22, height=44)
        show_pixbuffer(display, fbuf, x_pos=0, y_pos=0, width=135, height=240)

