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

note this requires the secrets.py file to be setup with wifi credentials and adafruit io

this version uses TFT display, and requires an M4 class ItsyBitsy
must create lib/ folder and install the following Adafruit libraries:
    adafruit_bus_device (folder)
    adafruit_esp32spi (folder)
    adafruit_display_text (folder)
    adafruit_display_shapes (folder)
    adafruit_st7735r.mpy    ?????
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

spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
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
    except (ValueError, RuntimeError) as e:
        print("Failed to get data, retrying\n", e)
        wifi.reset()
        continue

    response = None
    time.sleep(15)
