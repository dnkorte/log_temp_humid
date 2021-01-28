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
    and https://learn.adafruit.com/adafruit-aht20  
    and https://learn.adafruit.com/adafruit-si7021-temperature-plus-humidity-sensor/circuitpython-code
    and https://learn.adafruit.com/adafruit-io-basics-airlift/circuitpython
    https://github.com/adafruit/Adafruit_CircuitPython_ESP32SPI/blob/master/examples/esp32spi_localtime.py (json + get_)
    https://github.com/adafruit/Adafruit_CircuitPython_ESP32SPI/blob/master/examples/esp32spi_aio_post.py  (adafruit io)
    https://github.com/adafruit/Adafruit_CircuitPython_ESP32SPI/blob/master/adafruit_esp32spi/adafruit_esp32spi_wifimanager.py
    https://circuitpython.readthedocs.io/en/5.3.x/docs/library/network.html  (background; not used)

Open Weather API
    https://learn.adafruit.com/weather-display-matrix/code-the-weather-display-matrix
    https://home.openweathermap.org/users/sign_up    log in and get API key
    https://learn.adafruit.com/weather-display-matrix/code-the-weather-display-matrix  open-weather info


note this requires the secrets.py file to be setup with wifi credentials and adafruit io

IMPORTANT NOTE, for development purposes, be aware that you cannot upload new code when it is 
    waiting on communication with ESP Wifi -- not sure about the details of this yet,
    but it works better if you only "upload" while it flashing green imalive bubble...

must create lib/ folder and install the following Adafruit libraries:
    adafruit_bus_device (folder)
    adafruit_esp32spi (folder)
    adafruit_io (folder)
    adafruit_ahtx0.mpy
    adafruit_dotstar.mpy
    adafruit_requests.mpy (IMPORTANT: use 5.3.1 version as 6.x versions have bug)
    neopixel.mpy

ItsyBitsy pin connections:
    to I2C (for si7021 sensor):
        SDA  (blue)
        SCL (yellow)

    (Note also ItsyBitsy requires Vbat and Gnd, and it also supplies 3v power to power rails

Note in Open Weather Cities List
    {
    "id": 4993022,
    "name": "Flushing",
    "state": "MI",
    "country": "US",
    "coord": {
        "lon": -83.851067,
        "lat": 43.06308
    }

    ===========================================================================
    = NOTE this works reliably on CP 5.3.1, but fails consistently on CP 6.0
    = due to failure in adafruit_requests library
    = currently running 5.3.1 on original box (MBR) and office box
    ===========================================================================

    ERROR MESSAGE WHEN USING adafruit_requests.mpy at 6.0 library not present for 5.3
          Traceback (most recent call last):
          File "code.py", line 173, in <module>
          File "adafruit_io/adafruit_io.py", line 574, in send_data
          File "adafruit_io/adafruit_io.py", line 523, in _post
          File "adafruit_esp32spi/adafruit_esp32spi_wifimanager.py", line 244, in post
          File "adafruit_requests.py", line 641, in post
          File "adafruit_requests.py", line 540, in request
          File "adafruit_requests.py", line 537, in request
          File "adafruit_requests.py", line 458, in _send_request
          File "adafruit_requests.py", line 449, in _send
          File "adafruit_esp32spi/adafruit_esp32spi_socket.py", line 82, in send
          File "adafruit_esp32spi/adafruit_esp32spi.py", line 710, in socket_write
        RuntimeError: Failed to send 4 bytes (sent 0)

        ALSO
        Socket missing recv_into. Using more memory to be compatible

    Adafruit CircuitPython 5.3.1 on 2020-07-13; Adafruit ItsyBitsy M4 Express with samd51g19
    See thread: https://discord.com/channels/327254708534116352/537365702651150357/772675662859206666
    and note: https://discord.com/channels/327254708534116352/537365702651150357/773692880229367858
    and note: https://github.com/adafruit/Adafruit_CircuitPython_Requests/issues/34

    Traceback (most recent call last):
      File "code.py", line 238, in <module>
      File "adafruit_io/adafruit_io.py", line 568, in send_data
      File "adafruit_io/adafruit_io.py", line 519, in _post
      File "adafruit_esp32spi/adafruit_esp32spi_wifimanager.py", line 221, in post
      File "adafruit_requests.py", line 296, in post
      File "adafruit_requests.py", line 251, in request
      File "adafruit_requests.py", line 192, in request
      File "adafruit_esp32spi/adafruit_esp32spi_socket.py", line 75, in connect
      File "adafruit_esp32spi/adafruit_esp32spi.py", line 752, in socket_connect
      File "adafruit_esp32spi/adafruit_esp32spi.py", line 651, in socket_open
      File "adafruit_esp32spi/adafruit_esp32spi.py", line 325, in _send_command_get_response
      File "adafruit_esp32spi/adafruit_esp32spi.py", line 308, in _wait_response_cmd
      File "adafruit_esp32spi/adafruit_esp32spi.py", line 295, in _wait_response_cmd
      File "adafruit_esp32spi/adafruit_esp32spi.py", line 277, in _check_data
    RuntimeError: Expected 01 but got 00


"""

import time
import board
import busio
import sys
from digitalio import DigitalInOut
from adafruit_esp32spi import adafruit_esp32spi
from adafruit_esp32spi import adafruit_esp32spi_wifimanager
from adafruit_io.adafruit_io import IO_HTTP, AdafruitIO_RequestError
import adafruit_requests    
import adafruit_ahtx0
import adafruit_dotstar
import neopixel
 
# Create library object using our Bus I2C port
i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_ahtx0.AHTx0(i2c)


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

# setup user NeoPixel 
# note on my ItsyBitsy mount boards NeoPixel power comes from Vbatt pin
# so NeoPixel does not light if powered by USB alone   
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (173, 9, 0)

pixels = neopixel.NeoPixel(board.D5, 1, 
    brightness=0.2, auto_write=False, pixel_order=neopixel.GRB)

# setup pins for ItsyBitsy Airlift:
esp32_cs = DigitalInOut(board.D13)
esp32_ready = DigitalInOut(board.D11)
esp32_reset = DigitalInOut(board.D12)

spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)

# setup onboard status light for ItsyBitsy M4
status_light = adafruit_dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1, brightness=0.2)

# then initialize wife manager
wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, secrets, status_light)

# Create an instance of the Adafruit IO HTTP client
aio_username = secrets["aio_username"]
aio_key = secrets["aio_key"] 
io = IO_HTTP(aio_username, aio_key, wifi)

print("initiating connection to adafruit io")
want_local_feed = True

# setup connection to temperature feed
pixels.fill(YELLOW)   # flash YELLOW/RED to say initializing Adafruit IO Temperature
pixels.show()
time.sleep(0.5)
pixels.fill(RED)
pixels.show()
time.sleep(0.5)
pixels.fill(BLACK)
pixels.show()
try:
    # Get the 'temperature' feed from Adafruit IO
    temperature_feed = io.get_feed(config['feed_T'])
    print("successfully setup temperature feed", temperature_feed["key"])
except AdafruitIO_RequestError:
    # If no 'temperature' feed exists, create one
    #temperature_feed = io.create_new_feed(config['feed_T'])
    want_local_feed = False


# setup connection to humidity feed
pixels.fill(YELLOW)   # flash YELLOW/BLUE to say initializing Adafruit IO Temperature
pixels.show()
time.sleep(0.5)
pixels.fill(BLUE)
pixels.show()
time.sleep(0.5)
pixels.fill(BLACK)
pixels.show()
try:
    # Get the 'humidity' feed from Adafruit IO
    humidity_feed = io.get_feed(config['feed_H'])
    print("successfully setup humidity feed", humidity_feed["key"])
except AdafruitIO_RequestError:
    # If no 'humidity' feed exists, create one
    # humidity_feed = io.create_new_feed(config['feed_H'])
    want_local_feed = False



pixels.fill(YELLOW)   # flash YELLOW/GREEN to say checking weather channels
pixels.show()
time.sleep(0.5)
pixels.fill(GREEN)
pixels.show()
time.sleep(0.5)
pixels.fill(BLACK)
pixels.show()

want_weather_feed = True
try:
    weather_location = config['weather_location']
except:
    want_weather_feed = False

if want_weather_feed:
    try:
        weather_feed_T = io.get_feed(config['feed_T_outdoor'])
    except:
        want_weather_feed = False

    try:
        weather_feed_H = io.get_feed(config['feed_H_outdoor'])
    except:
        want_weather_feed = False


if want_weather_feed:
    print("Will post weather data from:", weather_location)

    UNITS = "imperial"  # or optionally "metric"
 
    # Set up from where we'll be fetching data
    DATA_SOURCE = (
        "http://api.openweathermap.org/data/2.5/weather?q=" + weather_location + "&units=" + UNITS
    )
    DATA_SOURCE += "&appid=" + secrets["openweather_token"]

else:
    print("Will NOT be collecting weather information")

 
"""
# NOTE we run the main loop once each 15 seconds and log data to screen
# but we only log to adafruit.io every 2 minutes (30 readings/hr; 720/day)
# (so we log once every 8 cycles)
"""

sample_loop_start_time = time.monotonic() - 999
weather_loop_start_time = time.monotonic() - 999
imalive_loop_start_time = time.monotonic()
working_ok = True

while True:

    if (time.monotonic() > (sample_loop_start_time + 120)) and want_local_feed:
        sample_loop_start_time = time.monotonic()

        tempF = (sensor.temperature*1.8) + 32
        humidity = sensor.relative_humidity


        pixels.fill(RED)    # set pixels RED to say "sending temperature"
        pixels.show()
        if (True):
            # use adafruit_io higher level driver to interact with adafruit io
            print("sending to temperature feed; temp=", tempF, " time:",time.monotonic())
            try:
                io.send_data(temperature_feed["key"], tempF)
                working_ok = True
            except (RuntimeError) as e:
                sys.print_exception(e)
                working_ok = False
        else:
            # use lower level direct calls to interact with adafruit io (keep as example)
            feed = config['feed_T']
            payload = {'value':tempF}
            response = wifi.post(
                "https://io.adafruit.com/api/v2/"+secrets['aio_username']+"/feeds/"+feed+"/data",
                json=payload,
                headers={"X-AIO-KEY":secrets['aio_key']})
            print(response.json())
            response.close()

        pixels.fill(BLUE)    # set pixels BLUE to say "sending humidity"
        pixels.show()
        print("sending to humidity feed; humidity=", humidity, " time:",time.monotonic())
        try:
            io.send_data(humidity_feed["key"], humidity)
            working_ok = True
        except (RuntimeError) as e:
            sys.print_exception(e)  
            working_ok = False          

        print("local data send complete", time.monotonic())
        pixels.fill(BLACK)    # set pixels OFF
        pixels.show()


    # only query the weather every 10 minutes (and on first run)
    if (time.monotonic() > (weather_loop_start_time + 600)) and want_weather_feed:
        weather_loop_start_time = time.monotonic()
        pixels.fill(YELLOW)    # set pixels YELLOW to say "processing weather data"
        pixels.show()

        try:            
            print("Retrieving data from openweather...")
            response = wifi.get(DATA_SOURCE)
            json = response.json()
            #print("Data from weather feed: ", json)
            outdoor_T = json["main"]["temp"]
            outdoor_H = json["main"]["humidity"]
            print("as extracted, temperature=", outdoor_T, " humidity=", outdoor_H)

            print("sending to outdoor temperature feed; temp=", outdoor_T, " time:",time.monotonic())
            try:
                io.send_data(weather_feed_T["key"], outdoor_T)
                working_ok = True 
            except (RuntimeError) as e:
                sys.print_exception(e)
                working_ok = False      

            print("sending to outdoor humidity feed; humidity=", outdoor_H, " time:",time.monotonic())
            try:
                io.send_data(weather_feed_H["key"], outdoor_H)
                working_ok = True 
            except (RuntimeError) as e:
                sys.print_exception(e)
                working_ok = False                

            print("sent outdoor weather data to Adafruit IO", time.monotonic())

        except (RuntimeError) as e:
            sys.print_exception(e)
            working_ok = False      

        pixels.fill(BLACK)    # set pixels OFF
        pixels.show()


    if time.monotonic() > (imalive_loop_start_time + 4):
        print("i'm alive", time.monotonic(), " will sample at:", (sample_loop_start_time + 120))
        imalive_loop_start_time = time.monotonic()
        if working_ok:
            pixels.fill(GREEN)      # flash NeoPixel GREEN for "alive and happy"
        else:
            pixels.fill(ORANGE)     # flash NeoPixel ORANGE for "alive but troubled"
        pixels.show()
        time.sleep(0.25)
        pixels.fill(BLACK)    # set pixels OFF
        pixels.show()

    time.sleep(0.25)