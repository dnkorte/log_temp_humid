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

this checks and displays local room temperature and humidity every 15 seconds,
and logs it to adafruit IO once every 2 minutes.  note that it has a flashing
"i'm alive" indicator on the display that flashes GREEN once per second.
the "i'm alive" strobe turns orange while sending temperature to adafruit io,
and turns blue while sending humidity data to adafruit io.  all values are
logged in english units (farenheit and pct humidity)

Note for simplicity, and to allow the biggest display possible on the limited
screen, both temperature and humidity values are shown as 2 digits only 
(since this is for internal household values, that's probably a pretty 
reasonable limitation most of the time -- could be problematic during a hot
summer with no air conditioning...   the logged values show full range


Background References:
    from https://learn.adafruit.com/adafruit-airlift-bitsy-add-on-esp32-wifi-co-processor/internet-connect
    and https://learn.adafruit.com/adafruit-io-basics-temperature-and-humidity/python-code 
    and https://learn.adafruit.com/adafruit-si7021-temperature-plus-humidity-sensor/circuitpython-code
    https://learn.adafruit.com/adafruit-1-3-and-1-54-240-x-240-wide-angle-tft-lcd-displays

note this requires the secrets.py file to be setup with wifi credentials and adafruit io

IMPORTANT NOTE, for development purposes, be aware that you cannot upload new code when it is 
    waiting on communication with ESP Wifi -- not sure about the details of this yet,
    but it works better if you only "upload" while it flashing green imalive bubble...

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
from adafruit_display_shapes import circle
from adafruit_st7789 import ST7789

DISPLAY_WIDTH = 240
DISPLAY_HEIGHT = 135

# Release any resources currently in use for the displays
displayio.release_displays()
 
spi = board.SPI()
tft_cs = board.D10
tft_dc = board.D7
tft_reset = board.D9
 
display_bus = displayio.FourWire(spi, command=tft_dc, 
    chip_select=tft_cs, reset=tft_reset)
 
# note "rowstart=XXX" is because the ST7789 driver can handle up to 320x240 displays
# we want to use only the rightmost part of that (to suit our width) 
# per guide, for a 240px wide display we would normally use "rewstart=80"
# https://learn.adafruit.com/adafruit-1-14-240x135-color-tft-breakout/circuitpython-displayio-quickstart
# display = ST7789(display_bus, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, rowstart=(320-DISPLAY_WIDTH))
display = ST7789(display_bus, width=DISPLAY_WIDTH, 
    height=DISPLAY_HEIGHT, rowstart=40, colstart=53, rotation=270)



# Create the display context for initial splash screen -------------------------------------
splash = displayio.Group(max_size=4)
display.show(splash)
 
color_bitmap = displayio.Bitmap(DISPLAY_WIDTH, DISPLAY_HEIGHT, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0xED2C00 # Brown Background
 
bg_sprite = displayio.TileGrid(color_bitmap,
                               pixel_shader=color_palette,
                               x=0, y=0)
splash.append(bg_sprite) 


# draw first line of initial splash screen
scale_hello = 3
hello_group = displayio.Group(max_size=10, scale=scale_hello, x=0, y=35)
hello_textbox = label.Label(terminalio.FONT, max_glyphs=24, color=0xFFFFFF)
hello_group.append(hello_textbox) # Subgroup for text scaling
splash.append(hello_group)
outputMsg = "Temp/Humidity"
hello_textbox.text = outputMsg
_, _, textwidth, _ = hello_textbox.bounding_box
scaled_textwidth = textwidth * scale_hello
hello_textbox.x = int((DISPLAY_WIDTH - scaled_textwidth) / (2*scale_hello))

# draw second line of initial splash screen
scale_welcome = 3
welcome_group = displayio.Group(max_size=10, scale=scale_welcome, x=0, y=70)
welcome_textbox = label.Label(terminalio.FONT, max_glyphs=24, color=0xFFFFFF)
welcome_group.append(welcome_textbox) # Subgroup for text scaling
splash.append(welcome_group)
outputMsg = "Logger"
welcome_textbox.text = outputMsg
_, _, textwidth, _ = welcome_textbox.bounding_box
scaled_textwidth = textwidth * scale_welcome
welcome_textbox.x = int((DISPLAY_WIDTH - scaled_textwidth) / (2*scale_welcome))

# draw third line of initial splash screen
scale_prep = 2
prep_group = displayio.Group(max_size=10, scale=scale_prep, x=0, y=110)
prep_textbox = label.Label(terminalio.FONT, max_glyphs=24, color=0xFFFFFF)
prep_group.append(prep_textbox) # Subgroup for text scaling
splash.append(prep_group)
outputMsg = "(preparing)"
prep_textbox.text = outputMsg
_, _, textwidth, _ = prep_textbox.bounding_box
scaled_textwidth = textwidth * scale_prep
prep_textbox.x = int((DISPLAY_WIDTH - scaled_textwidth) / (2*scale_prep))


 
# Create library object using our Bus I2C port
i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_si7021.SI7021(i2c)


# Get basic configuration info from config.py file (the not-super-secret stuff...)
try:
    from config import config
except ImportError:
    print("configuration informaion is kept in config.py, please add them there!")
    raise

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

wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, secrets, status_light)



# Create the display context for normal display screen for operations ----------------------
# ===> note don't actually display it until we get our first datapost finished
# ===> this allows something useful to stay on screen instead of blackness during startup
# ===> note that its ok to repetitively display.show() the data screen during the loop
data_screen = displayio.Group(max_size=16)
# display.show(data_screen)   
 
color_bitmap = displayio.Bitmap(DISPLAY_WIDTH, DISPLAY_HEIGHT, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0x000000 # black background
 
bg_sprite = displayio.TileGrid(color_bitmap,
                               pixel_shader=color_palette,
                               x=0, y=0)
data_screen.append(bg_sprite) 

# create a label for temperature units ("F") label
label1_group = displayio.Group(max_size=1, scale=3, x=int(DISPLAY_WIDTH/2)-18, y=36)
label1_textbox = label.Label(terminalio.FONT, text="F", color=0xFF0000, max_glyphs=4)
label1_group.append(label1_textbox) # Subgroup for text scaling
data_screen.append(label1_group)

# create a label for humidity units ("%") label
label2_group = displayio.Group(max_size=1, scale=3, x=(DISPLAY_WIDTH-20), y=36)
label2_textbox = label.Label(terminalio.FONT, text="%", color=0x0000FF, max_glyphs=8)
label2_group.append(label2_textbox) # Subgroup for text scaling
data_screen.append(label2_group)

# create a label for temperature display number
temperature_disp_group = displayio.Group(max_size=2, scale=8,  x=10, y=int(DISPLAY_HEIGHT-75))
text = "  "
temperature_textbox = label.Label(terminalio.FONT, text=text, color=0xFF0000, max_glyphs=3)
temperature_disp_group.append(temperature_textbox) # Subgroup for text scaling
data_screen.append(temperature_disp_group)

# create a label for humidity display number
xpsn = int(DISPLAY_WIDTH/2)
humidity_disp_group = displayio.Group(max_size=2, scale=8, x=int(DISPLAY_WIDTH/2)+2, y=int(DISPLAY_HEIGHT-75))
text = "  "
humidity_textbox = label.Label(terminalio.FONT, text=text, color=0x0000FF, max_glyphs=3)
humidity_disp_group.append(humidity_textbox) # Subgroup for text scaling
data_screen.append(humidity_disp_group)

# create a small round "ticktock" bubble to give user feedback of aliveness
imalive = circle.Circle(int(DISPLAY_WIDTH/2)-5, (DISPLAY_HEIGHT-15), 10, fill=0x00FF00, outline=0xFF00FF)
data_screen.append(imalive) 

"""
# NOTE we run the main loop once each 15 seconds and log data to screen
# but we only log to adafruit.io every 2 minutes (30 readings/hr; 720/day)
# (so we log once every 8 cycles)
"""

NUMBER_OF_CYCLES_PER_DATALOG = 8
cycles_until_next_log = 1;

while True:
    tempF = (sensor.temperature*1.8) + 32
    humidity = sensor.relative_humidity

    cycles_until_next_log -= 1

    if cycles_until_next_log <= 0:

        cycles_until_next_log = NUMBER_OF_CYCLES_PER_DATALOG
        try:
            # print("Posting temp / humidity data...", end='')
            imalive.fill = 0xff0700     # orange
            # feed = 'temperature-1'
            feed = config['feed_T']
            payload = {'value':tempF}
            response = wifi.post(
                "https://io.adafruit.com/api/v2/"+secrets['aio_username']+"/feeds/"+feed+"/data",
                json=payload,
                headers={"X-AIO-KEY":secrets['aio_key']})
            print(response.json())
            response.close()

            imalive.fill = 0x0000ff     # blue
            # feed = 'humidity-1'
            feed = config['feed_H']
            payload = {'value':humidity}
            response = wifi.post(
                "https://io.adafruit.com/api/v2/"+secrets['aio_username']+"/feeds/"+feed+"/data",
                json=payload,
                headers={"X-AIO-KEY":secrets['aio_key']})
            print(response.json())
            response.close()

        except (ValueError, RuntimeError) as e:
            print("Failed to get data, retrying\n", e)
            wifi.reset()
            continue

        response = None

        #
        # Now DISPLAY the readings every cycle (even when not loggine...)
        # 
        display.show(data_screen)

        outputMsg = "{0:.0f}".format(tempF)
        temperature_textbox.text = outputMsg

        outputMsg = "{0:.0f}".format(humidity)
        humidity_textbox.text = outputMsg


    # this generates the flashing green "i'm alive" strobe and also controls 
    # the 15 second main cycle duration
    
    for i in range(15):
        imalive.fill = 0x000000
        time.sleep(0.5)
        imalive.fill = 0x00FF00
        time.sleep(0.5)
