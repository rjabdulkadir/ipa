""" Printer driver module.

Defines core printer functions.
"""

import time
from machine import Pin, UART


def combine_lists(lists):
    """ Used to combile two lists of bytarrays together.

    Parameters:
        lists (list): list of lists to combine

    Returns:
        combined_list (list): the merged list
    """
    combined_list = []
    for i in range(len(lists)):
        combined_element = bytearray()
        for lst in lists:
            if i < len(lst):
                combined_element += lst[i]
        combined_list.append(combined_element)
    return combined_list


class Printer:
    """ Main printer class

    """
    def __init__(self, uart_port, pwr_pin, rx_pin, tx_pin,
                                tx_buf=256, rx_buf=256, tout=0, tcout=0):
        self.uart_port = uart_port
        self.rx_pin = rx_pin
        self.tx_pin = tx_pin
        self.tx_buf = tx_buf
        self.rx_buf = rx_buf
        self.tout = tout
        self.tcout = tcout
        self.pwr_pin = Pin(pwr_pin, Pin.OUT, Pin.PULL_DOWN, value=0)
        self.uart = UART(self.uart_port, 115200, rx=rx_pin, tx=tx_pin,
                        txbuf=tx_buf, rxbuf=rx_buf,
                        timeout=tout, timeout_char=tcout)

    def init_uart(self, delay = 100):
        """ initialize uart assigned for printer.

        Parameters:
            delay (int): delay in ms to wait after init.

        Returns: None
        """
        self.uart = UART(self.uart_port, 115200, rx=self.rx_pin, tx=self.tx_pin,
                        txbuf=self.tx_buf, rxbuf=self.rx_buf,
                        timeout=self.tout, timeout_char=self.tcout)
        time.sleep_ms(delay)

    def printer_on(self):
        """ Turn on printer."""
        self.pwr_pin.value(0)
        time.sleep_ms(100)
        self.pwr_pin.value(1)

    def printer_off(self):
        """ Turn off printer."""
        self.pwr_pin.value(0)
        time.sleep_ms(100)
        self.pwr_pin.value(1)
        time.sleep_ms(100)
        self.pwr_pin.value(0)
        time.sleep_ms(100)
        self.pwr_pin.value(1)

    def online_status(self):
        """
        # function that returns true if printer is online else returns false.
        # bit 3 of the response byte indicate offline/online status.
        # if the bit is set it means offline so returns False.

        Returns:
            status (bool): True if paper is online else False.
        """
        self.uart.read()
        self.uart.write(b'\x10\x04\x01')
        time.sleep_ms(200)
        response = self.uart.read()
        if response is not None:
            stat = ord(response) & 0b00001000
        else:
            stat = 1
        return stat==0

    def check_paper(self, timeout=100, independent = False):
        """
        # bit 5 and 6 of the response byte indicate paper in/out status.
        # if the bits are set it means no paper so returns False.

                Ex. b'\x09\x50\x02'

        Parameters:
            timeout (int): time out in ms to wait after sending cmd.
            independent (bool): if true turn printer on first.

        Returns:
            status (bool): True if paper is present else False.
        """
        if independent:
            self.printer_on()
        self.uart.read()
        self.uart.write(b'\x10\x04\x04')
        time.sleep_ms(timeout)
        response = self.uart.read()
        if response is not None:
            stat = ord(response) & 0b01100000
        else:
            stat = 1
        if independent:
            self.printer_off()
        return stat==0

    def init_printer(self):
        """
        Clears the data in the print buffer and resets
        the printer mode to the mode that was in effect
        when the power was turned on.
        """
        self.uart.write(b'\x1b\x40')

    def config_printer_head(self, header):
        """ sets print concentration by changing this 3 values
            0-255 Max printing dots, Unit(8dots), Default:9(80 dots)
            3-255 Heating time, Unit(10us),Default:80(800us)
            0-255 Heating interval, Unit(10us)，Default:2(20us)

        Parameters:
            header (bytes): Ex. b'\x09\x50\x02'

        Returns:None
        """
        self.uart.write(b'\x1b\x37' + header)

    def set_Line_spacing(self, val=33):
        """
        Default line spacing is 32
        (char height of 24, line spacing of 8)
        Sets the line spacing to [n×0.125 mm].

        Parameters:
            val (int): line spacing

        Returns:None
        """
        if val < 24: val = 24
        self.uart.write(b'\x1b\x33' + bytes([val]))

    def underline(self, weight=1):
        """set Underline weights

        Parameters:
            weight (int):
                0 -- no underline
                1 -- normal underline
                2 -- thick underline

        Returns:None
        """
        self.uart.write(b'\x1b\x2d' + bytes([weight]))

    def set_print_Size(self, print_size='NORMAL'):
        """ set print sizes

        Parameters:
            print_size (str):
                Large -- double width and height
                Medium-- double height
                Small -- standard width and height

        Returns:None
        """
        val = print_size.upper()
        if val == 'LARGE':self.uart.write(b'\x1d\x21\x11')
        if val == 'MEDIUM':self.uart.write(b'\x1d\x21\x01')
        if val == 'NORMAL':self.uart.write(b'\x1d\x21\x00')

    def justify(self, position):
        """ Justify print position

        Parameters:
            position (str): print position

        Returns:None
        """
        val = position.upper()
        if val == 'CENTER':self.uart.write(b'\x1b\x61\x01')
        if val == 'RIGHT':self.uart.write(b'\x1b\x61\x02')
        if val == 'LEFT':self.uart.write(b'\x1b\x61\x00')

    def white_black_reverse(self, mode):
        """ Change printing mode to black on white or reverse.

        Parameters:
            mode (str):
                off-- turn off black on white or reverse mode
                on-- turn on black on white or reverse mode

        Returns:None
        """
        val = mode.upper()
        if val == 'ON':self.uart.write(b'\x1d\x42\x01')
        if val == 'OFF':self.uart.write(b'\x1d\x42\x00')

    def set_small_font_size(self):
        """ Sets font size to 9x17 """
        self.uart.write(b'\x1b\x21\x01')

    def set_normal_font_size(self):
        """ Sets font size to 12x24 """
        self.uart.write(b'\x1b\x21\x00')

    def print_downloaded_bit_image(self, mode):
        """mods to print downloaded bit image are

        Parameters:
            mode (str):
                Normal
                Double_width
                Double_height

        Returns:None
        """
        print_mode = mode.upper()
        if print_mode == 'NORMAL':self.uart.write(b'\x1d\x2f\x00')
        if print_mode == 'DOUBLE_WIDTH':self.uart.write(b'\x1d\x2f\x01')
        if print_mode == 'DOUBLE_HEIGHT':self.uart.write(b'\x1d\x2f\x10')

    def emphasize(self, mode):
        """ Turns bold mode on/off

        Parameters:
            mode (str):
                off-- turn off bold mode
                on-- turn on bold mode

        Returns:None
        """
        val = mode.upper()
        if val == 'ON':self.uart.write(b'\x1b\x45\x01')
        if val == 'OFF':self.uart.write(b'\x1b\x45\x00')

    def print_line(self, *args):
        """ Prints a line with given Parameters

        Parameters:
            args (str/bytes): printable data

        Returns:None
        """
        for arg in args:
            self.uart.write(arg)

    def set_udc(self, value):
        """ set user defind character mode

        Parameters:
            value (str):
                off-- turn off user defind character mode
                on-- turn on user defind character mode

        Returns:None
        """
        val = value.upper()
        if val == 'ON':self.uart.write(b'\x1b\x25\x01')
        if val == 'OFF':self.uart.write(b'\x1b\x25\x00')

    def test_page(self):
        """ prints the printer's test page.
        """
        self.uart.write(b'\x12\x54')

    def feed(self, n=1):
        """ Feeds newline*n

        Parameters:
            n (int): n number of newlines

        Returns:None
        """
        self.uart.write(b'\r\n'*n)

    def set_left_space(self, nL, nH):
        """ Sets left space with given values

        Parameters:
            nL (int):  lower byte
            nh (int): higher byte

        Returns:None
        """
        self.uart.write(b'\x1d\x4c' + bytes([nL])  + bytes([nH]))

    def set_tab_position(self):
        """ Sets the curser position"""
        self.uart.write('\x1b\x44\x08\x10\x18\x00')

    def print_string(self, string, font_dict, latin):
        """ Prints string using based on user defined
            font files (local or latin).

        Parameters:
            string (str): the string to be printed
            font_dict (dict): font file dictionary
            latin (bool): latin language or geez language

        Returns:None
        """
        if latin:
            self.uart.write(string)
            return
        self.uart.write(b'\x1b\x25\x01')
        bm=b''
        bm_len = 0
        for x in string:
            uc = ord(x)
            try:
                bmp=font_dict[uc]
            except KeyError:
                bmp=font_dict[32]
            bm += b'\x0c' + bmp
            if len(bmp) > 36:
                bm_len += 2
            else:
                bm_len += 1
        ascii_start = 0x30
        ascii_end = ascii_start + bm_len
        udf_bytes = bytes(range(ascii_start, ascii_end))
        start_end = bytes([ascii_start, ascii_end - 1])
        udc_str = b'\x1b\x26\x03' + start_end + bm
        self.uart.write(udc_str)
        self.uart.write(udf_bytes)
        self.uart.write(b'\x1b\x25\x00')

    def print_bitmap(self, row, row_length, *bmp_list, multiple=False, delay = 30):
        """ Prints bitmap user defined charecters.

        Parameters:
            row: the number of rows the bitmap has
            row_length: the length of a single row
            bmp_list tuple of bmp_lists: the list containing the bitmap data.
            multiple (bool): multiple bitmap files or single file
            delay (int): delay in ms to wait after turning UDC mode on.

        Returns:
            None
        """
        if multiple:
            new_list = combine_lists(bmp_list)
            bmp_list = new_list
        else:
            bmp_list = bmp_list[0]
        try:
            self.uart.write(b'\x1b\x25\x01')
            if row > 1 : self.uart.write(b'\x1b\x33\x00')
            time.sleep_ms(delay)
            row_end = len(bmp_list)-1
            ascii_start = 0x30
            ascii_end = ascii_start + row_length
            udf_bytes = bytes(range(ascii_start, ascii_end))
            start_end = bytes(chr(ascii_start), 'ascii') + bytes(chr(ascii_end - 1), 'ascii')
            for x in range(row):
                udc_str = b'\x1b\x26\x03' + start_end + bmp_list[x]
                self.uart.write(udc_str)
                self.uart.write(udf_bytes)
                if x != row_end: self.uart.write('\r\n')
            self.uart.write(b'\x1b\x25\x00')
        except Exception as err:
            print("couldn't print bitmap:",err)

    def print_qrcode(self, data, size=5):
        """ Prints qrcode using printers built in mode.

        Parameters:
            data (bytestr): text string
            size (int): qr code size

        Returns:
            None
        """
        if len(data) < 6:
            raise ValueError("Invalid data length, minumium data length is 6")
        qr_len = bytes(chr(len(data)+3), 'utf-8')
        self.print_line(b'\x1d\x28\x6b\x03\x00\x31\x43' + bytes(chr(size), 'utf-8'))
        self.print_line(b'\x1d\x28\x6b\x03\x00\x31\x45\x30')
        self.print_line(b'\x1d\x28\x6b' + qr_len + b'\x00\x31\x50\x30' + data)
        self.print_line(b'\x1d\x28\x6b\x03\x00\x31\x52\x30')
        self.print_line(b'\x1d\x28\x6b\x03\x00\x31\x51\x30')

    def barcode_chr(self, msg):
        """1:Abovebarcode 2:Below 3:Both 0:Not printed

        Parameters:
            msg (bytestr): barcode data

        Returns:
            None
        """
        self.uart.write(chr(29))
        self.uart.write(chr(72))
        self.uart.write(msg)

    def barcode_height(self, msg):
        """Set height Value 1-255 Default 50

        Parameters:
            msg (bytestr): barcode data

        Returns:
            None
        """
        self.uart.write(chr(29))
        self.uart.write(chr(104))
        self.uart.write(msg)

    def barcode_width(self, width = 2):
        """Set width # Value 2,3 Default 2

        Parameters:
            width (int): barcode width

        Returns:
            None
        """
        self.uart.write(chr(29))
        self.uart.write(chr(119))
        self.uart.write(chr(width))

    def barcode(self, msg, code_sys, chr_no):
        """ Print barcode

        # CODE SYSTEM, NUMBER_OF_CHARACTERS
        # 65=UPC-A    11,12    #71=CODEBAR    >1
        # 66=UPC-E    11,12    #72=CODE93    >1
        # 67=EAN13    12,13    #73=CODE128    >1
        # 68=EAN8    7,8    #74=CODE11    >1
        # 69=CODE39    >1    #75=MSI        >1
        # 70=I25        >1 EVEN NUMBER

        Parameters:
            msg (bytestr): barcode data
            code_sys (int): standard code system
            chr_no (int): standard chr_no

        Returns:
            None
        """
        self.uart.write(chr(29))
        self.uart.write(chr(107))
        self.uart.write(chr(code_sys))
        self.uart.write(chr(chr_no))
        self.uart.write(msg)
