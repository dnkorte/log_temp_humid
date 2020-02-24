# temperature/humidity logger for household rooms; sends data to AdafruitIO via Wifi
# 
# MIT License
# 
# Copyright (c) 2020 Don Korte
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# 

"""
temperature/humidity logger for household rooms; sends data to AdafruitIO via Wifi
Author(s):  Don Korte
Repository: https://github.com/dnkorte/log_temp_humid

Background References:
    from https://learn.adafruit.com/adafruit-airlift-bitsy-add-on-esp32-wifi-co-processor/internet-connect
    and https://learn.adafruit.com/adafruit-io-basics-temperature-and-humidity/python-code 
    and https://learn.adafruit.com/adafruit-si7021-temperature-plus-humidity-sensor/circuitpython-code
    https://learn.adafruit.com/adafruit-1-3-and-1-54-240-x-240-wide-angle-tft-lcd-displays

note this requires the secrets.py file to be setup with wifi credentials and adafruit io

this version uses TFT display, and requires an M4 class ItsyBitsy
must create lib/ folder and install the following Adafruit libraries:
    adafruit_bus_device (folder)
    adafruit_esp32spi (folder)
    adafruit_display_text (folder)
    adafruit_display_shapes (folder)
    adafruit_st7789.mpy    
    adafruit_dotstar.mpy
    adafruit_requests.mpy
    adafruit_si7021.mpy
    neopixel.mpy

ItsyBitsy pin connections:
    to TFT (1.8in TFT http://www.adafruit.com/products/358):
        SCK /   SCK
        MOSI /  MOSI
        10:     CS
        9:      Reset
        7:      DC
    to I2C (for si7021 sensor):
        SDA  (blue)
        SCL (yellow)

    (Note also TFT requires power, ground, and backlight from power rails)
    (Note also ItsyBitsy requires Vbat and Gnd, and it also supplies 3v power to power rails
"""


import time
import board
import busio
from digitalio import DigitalInOut
import neopixel
from adafruit_esp32spi import adafruit_esp32spi
from adafruit_esp32spi import adafruit_esp32spi_wifimanager
import adafruit_dotstar
import adafruit_si7021
import displayio
import terminalio
from adafruit_display_text import label
from adafruit_st7789 import ST7789

DISPLAY_WIDTH = 240
DISPLAY_HEIGHT = 135

# Release any resources currently in use for the displays
displayio.release_displays()
 
spi = board.SPI()
tft_cs = board.D10
tft_dc = board.D7
tft_reset = board.D9
 
display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=tft_reset)
 
# note "rowstart=XXX" is because the ST7789 driver can handle up to 320x240 displays
# we want to use only the rightmost part of that (to suit our width) 
# per guide, for a 240px wide display we would normally use "rewstart=80"
display = ST7789(display_bus, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, rowstart=(320-DISPLAY_WIDTH))
 
# Make the display context
splash = displayio.Group(max_size=10)
display.show(splash)
 
color_bitmap = displayio.Bitmap(DISPLAY_WIDTH, DISPLAY_HEIGHT, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0x00FF00 # Bright Green
 
bg_sprite = displayio.TileGrid(color_bitmap,
                               pixel_shader=color_palette,
                               x=0, y=0)
splash.append(bg_sprite) 

# Draw a smaller inner rectangle
inner_bitmap = displayio.Bitmap((DISPLAY_WIDTH-40), (DISPLAY_HEIGHT-40), 1)
inner_palette = displayio.Palette(1)
inner_palette[0] = 0xAA0088 # Purple
inner_sprite = displayio.TileGrid(inner_bitmap,
                                  pixel_shader=inner_palette,
                                  x=20, y=20)
splash.append(inner_sprite)
 
# Draw a label
text_group = displayio.Group(max_size=10, scale=2, x=40, y=60)
text = "Temp/Humidity"
text_area = label.Label(terminalio.FONT, text=text, color=0xFFFF00)
text_group.append(text_area) # Subgroup for text scaling
splash.append(text_group)
 
# Create library object using our Bus I2C port
i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_si7021.SI7021(i2c)

print("ESP32 SPI webclient test")

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

# If you have an ItsyBitsy Airlift:
esp32_cs = DigitalInOut(board.D13)
esp32_ready = DigitalInOut(board.D11)
esp32_reset = DigitalInOut(board.D12)

# note the next line is not needed here because it was already initialized during display init
# spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)

"""Use below for Most Boards"""
# status_light = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.2) # Uncomment for Most Boards

"""Uncomment below for ItsyBitsy M4"""
# status_light = dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1, brightness=0.2)
status_light = adafruit_dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1, brightness=0.2)

# Uncomment below for an externally defined RGB LED
# import adafruit_rgbled
# from adafruit_esp32spi import PWMOut
# RED_LED = PWMOut.PWMOut(esp, 26)
# GREEN_LED = PWMOut.PWMOut(esp, 27)
# BLUE_LED = PWMOut.PWMOut(esp, 25)
# status_light = adafruit_rgbled.RGBLED(RED_LED, BLUE_LED, GREEN_LED)

wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, secrets, status_light)

counter = 0

while True:
    try:
        print("Posting temp / humidity data...", end='')
        data = counter
        feed = 'temperature-1'
        payload = {'value':sensor.temperature}
        response = wifi.post(
            "https://io.adafruit.com/api/v2/"+secrets['aio_username']+"/feeds/"+feed+"/data",
            json=payload,
            headers={"X-AIO-KEY":secrets['aio_key']})
        print(response.json())
        response.close()

        feed = 'humidity-1'
        payload = {'value':sensor.relative_humidity}
        response = wifi.post(
            "https://io.adafruit.com/api/v2/"+secrets['aio_username']+"/feeds/"+feed+"/data",
            json=payload,
            headers={"X-AIO-KEY":secrets['aio_key']})
        print(response.json())
        response.close()
        counter = counter + 1
        print("OK")

        outputMsg = "{0:.0f} F {1:.0f} pct RH".format(((sensor.temperature*1.8)+32), sensor.relative_humidity)
        # text_area.text = sensor.temperature
        text_area.text = outputMsg

    except (ValueError, RuntimeError) as e:
        print("Failed to get data, retrying\n", e)
        wifi.reset()
        continue

    response = None
    time.sleep(15)
