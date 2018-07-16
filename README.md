# BeyondTheHorizon 
To run scripts soem liblaries need to be added:
1. "apscheduler" - to install it please call:
    ```bash
    sudo pip install apscheduler
    ```
## Water Temperature Sensor
To run the water sensor some actions are reqiuerd:
1. Run 1-wire interface
2. wlthermsensor liblaries need to be installed, to install it please call:
```bash
sudo pip install w1thermsensor
```
3. Require modules FileUtil, LoggerUtil, water-temperature

## GPS 
To run the GPS sensor some actions are reqiuerd:
1. sudo pip install pynmea2

## Light Sensor
To run the Light sensor some actions are reqiuerd:
1. Run the IC2 interface in the configuration 
```bash
sudo raspi-config
```
2. Connect pins according to http://www.pibits.net/code/raspberry-pi-bh1750-light-sensor.php

## BME280 - temeperature 
1. Download library from https://github.com/adafruit/Adafruit_Python_BME280
2. Follow instrucitons from README file to install library
3. Copy Adafruit_BME280.py script to the directory where is located script using this library

## LSM9DS0 - giroscope
1. Download library from https://github.com/jckw/Adafruit_LSM9DS0
2. Rename LSM9DS0.py to Adafruit_LSM9DS0.py (it is located in Adafruit_LSM9DS0 directory)
2. Copy Adafruit_LSM9DS0.py file from Adafruit_LSM9DS0 directory to the place where is located script using this library


## LIST OF SCRIPTS plus name of script file with results
1. BME280.py - bme280
2. GPS.py - gps
3. lightSensor.py - light
4. LSM9DS0.py - lsm9ds0
5. Rfid.py - rfid
6. watterTemperature.py - waterTemp


## Bind USB Device Under static Name
You should not have to write your own udev rules, because udev already makes links like /dev/serial/by-id/usb-Arduino__www.arduino.cc__xxxx_xxxxxxxxxxxxxxxxxxxx-if00. These include the serial number, so they even work if you have two Arduinos and need to keep them separate.

```

