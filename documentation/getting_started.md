# Getting Started
The operating software is developed using Micropython on the ESP-32 microcontroller platform with SIMcom SIM800C GSM and a PN532 based NFC boards. The reference display is a 240x135 lCD module based on the ST7789 display driver chip. A generic 58mm thermal printer supporting a UART interface can be used for receipt printing. Development kits for all of these components are widely available.
# Hardware Components
The reference design is based on the following components. 
## ESP32 Micropython development boards
A number of boards ESP-32 development boards are available.The ESP32-DevKitC V4 described [here](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/hw-reference/esp32/get-started-devkitc.html#get-started-esp32-devkitc-board-front) is suitable.
## SIM800C
This is a 2G GSM GPRS Quad Band module suitable for IoT use.
## PN532 Module
The PN532 is the most popular NFC chip, that can read and write to tags and cards.
## ST7789 DisplayModule
This is a 240x135 LCD display that can display 65K colors.
## Thermal Printer
The reference design uses and standard 58mm mini thermal printer available from many suppliers.
## Single Cell Lithium Ion Battery Charger/5V Converter Module
This module is used to charge the lithium ion rechargeable battery and supply power to the other components.
## Lithium Ion Battery
The reference design is powered by a lithium ion 3.7V 5000mAh battery.
# Software
## Setting Up a Development System
### Introduction
The software for the reference system is based on Micropython. The easiest path is to get started is to obtain a development board that can be connect to a PC, and using a terminal program to run the Micropython REPL. This document describes this process.
### Getting Micropython
Instructions for obtaining and flashing Micropython for the ESP32 can be found [here](https://docs.micropython.org/en/latest/esp32/tutorial/intro.html).
### Uploading Modules
* A list of tools that can be used to develop and upload modules can be found [here](https://randomnerdtutorials.com/micropython-ides-esp32-esp8266/).
* Instructions for using the command line Adafruit Micropython Tool ampy can be found [here](https://pypi.org/project/adafruit-ampy/).
* Instructions on using the Thonny development environment can be found [here](https://randomnerdtutorials.com/getting-started-thonny-micropython-python-ide-esp32-esp8266/).
### Using the Micropython REPL
The Micropthon REPL (Read Evaluate Print Loop) is a useful tool for learning Micropython and for developing and testing modules. A free tool that can be used for this, available for PCs running both Windows and Linux is [putty](https://www.putty.org/). Downloads are can be found [here](https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html). A short introduction on how to use MicroPython from the REPL can be found [here](https://docs.micropython.org/en/latest/esp8266/tutorial/repl.html). Micropython documentation including tutorials for different platforms can be found [here](https://docs.micropython.org/en/latest/index.html).
## Running in a Production Setting
TBW
### Compiling Micropython
TBW
### ESP32 Flash Encryption and Secure Boot
The Flash Encryption feature of the ESP32 allows encryption of the contents of the off chip flash memory. This means that the contents will not be accessible by any means of a direct connection to the controller. By this means certain information like passwords and key only readable by the application can be stored. The procedure to do this can be found [here](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/security/flash-encryption.html).
