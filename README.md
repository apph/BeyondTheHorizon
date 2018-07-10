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

## BME280
1. Download library from https://github.com/adafruit/Adafruit_Python_BME280
2. Follow instrucitons from README file to install library
3. Copy Adafruit_BME280.py script to the directory where is located script using this library
