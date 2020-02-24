# demo program for "WiFi Manager" which also posts to an Adafruit IO feed
# from https://learn.adafruit.com/adafruit-airlift-bitsy-add-on-esp32-wifi-co-processor/internet-connect
# and https://learn.adafruit.com/adafruit-io-basics-temperature-and-humidity/python-code 
# and https://learn.adafruit.com/adafruit-si7021-temperature-plus-humidity-sensor/circuitpython-code
# note this requires the secrets.py file to be setup with wifi credentials and adafruit io
# 
# this version is commented appropriately for ItsyBitsy M4
# ----------------------------------------------------------------------------------------
import time
import board
import busio
import adafruit_si7021
 
# Create library object using our Bus I2C port
i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_si7021.SI7021(i2c)
 
 
while True:
    print("\nTemperature: %0.1f C" % sensor.temperature)
    print("Humidity: %0.1f %%" % sensor.relative_humidity)
    time.sleep(2)