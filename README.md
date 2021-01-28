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
    
### Bill of Materials

| Description | Supplier | Notes |
| ----------- | -------- | ----- | 
| [Adafruit ItsyBitsy M4](https://www.adafruit.com/product/3800) | Adafruit | [Guide](https://learn.adafruit.com/introducing-adafruit-itsybitsy-m4) |
| [Airlift Itsy](https://www.adafruit.com/product/4363) | Adafruit | [Guide](https://learn.adafruit.com/adafruit-airlift-bitsy-add-on-esp32-wifi-co-processor) |
| [AHT20 Temp/Humidity Sensor](https://www.adafruit.com/product/4566) | Adafruit | [Guide](https://learn.adafruit.com/adafruit-aht20) |
| [NeoPixel Jewel](https://www.adafruit.com/product/2226) | Adafruit | [Guide](https://learn.adafruit.com/adafruit-neopixel-uberguide) |
| [5v Power Block with 2.1mm barrel plug](https://www.adafruit.com/product/276) | Adafruit | |
| [Panel Mount 2.1mm barrel jack](https://www.adafruit.com/product/610) | Adafruit | |
| [JST SH 4-pin connector](https://www.adafruit.com/product/4208) | Adafruit | can be hand soldered to PCB, carefully... |
| [JST SH 4-pin cable](https://www.adafruit.com/product/4210) | Adafruit | . |
| [M3 Threaded Insert](https://www.mcmaster.com/94459A130/) | McMaster-Carr | 8 pcs (lid-to-box, PCB-to-box) |
| M3 screws 6mm | | 8 pcs (lid-to-box, PCB to lid) |
| M3 screws 12mm | | 2 pcs (NeoPixel Jewel) |
| M2.5 screws 6mm | | 4 pcs (sensor-to-box) |
| 470 ohm 1/2 w resistor, axial | | for NeoPixel Jewel |
| 470 uF electrolytic capacitor | | for NeoPixel Jewel |
| Dupont-style pin and post connectors | | for NeoPixel and power, can solder direct if desired |



