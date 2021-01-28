# Household Temperature/Humidity Logger

<table>
<tr>
<td><img width="420" src="https://github.com/dnkorte/log_temp_humid/blob/master/documentation/sample_dashboard_temps.jpg" alt="sample dashboard showing temperatures from multiple units" /></td>
<td><img width="420" src="https://github.com/dnkorte/log_temp_humid/blob/master/documentation/sample_dashboard_humidities.jpg" alt="sample dashboard showing humidities from multiple units" /></td>
</tr>
<tr>
<td><img width="420" src="https://github.com/dnkorte/log_temp_humid/blob/master/documentation/pic_box_front.jpg" alt="picture of box front showing NeoPixel status light" /></td>
<td><img width="420" src="https://github.com/dnkorte/log_temp_humid/blob/master/documentation/pic_box_back.jpg" alt="pic of box back showing sensor" /></td>
</tr>
<tr>
<td><img width="420" src="https://github.com/dnkorte/log_temp_humid/blob/master/documentation/pic_inside_box.jpg" alt="picture of box innards" /></td>
<td><img width="420" src="https://github.com/dnkorte/log_temp_humid/blob/master/PCB/pcb_render.png" alt="PCB render" /></td>
</tr>
</table>

Temperature/humidity logger for household rooms; sends data to AdafruitIO via Wifi

Background Reference Info:

* from https://learn.adafruit.com/adafruit-airlift-bitsy-add-on-esp32-wifi-co-processor/internet-connect
* and https://learn.adafruit.com/adafruit-io-basics-temperature-and-humidity/python-code 
* and https://learn.adafruit.com/adafruit-si7021-temperature-plus-humidity-sensor/circuitpython-code

NOTE: needs the following files on the ItsyBitsy
* config.py (edit to reflect correct info for your device/environment)
* secrets.py (standard for you)
* log_temp_humid_wx_neopixel.py  (renamed as code.py)

the following library files (in lib/ folder:
* adafruit_bus_device (folder)
* adafruit_esp32spi (folder)
* adafruit_io (folder)
* adafruit_ahtx0.mpy
* adafruit_dotstar.mpy
* adafruit_requests.mpy (IMPORTANT: use 5.3.1 version as 6.x versions have bug)
* neopixel.mpy
    


