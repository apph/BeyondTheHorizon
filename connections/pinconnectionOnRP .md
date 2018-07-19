## Raspberry
1. - red (3v)
2. - orange (5v) --nope
3. - green 
4. - EMPTY
5. - yellow
6. - brown (GND) nope
7. - white/yellow (date - water temperature)
8. -yellow gps/modem
9. - blue (GND)
10. - white - gps/modem
17. - red (pwd - water temperature)
25. - black (gnd - water temperature)


## BH1750 - Light sensor
1. - empty
2. - green 
3. - yellow 
4. - blue (GND)
5. - red (3v)

## Neo 6m GPS - Modem BOX
1. - orange (5V)
2. - (GND) black
3. - (TX) violet
4. - (RX) grey
5. - EMPTY

## BME280 Temeperature Humidyty preasure
1. - red (3v)
2. - empty
3. - blue (gnd)
4. - yellow
5. - empty
6. - green

## LSM9DS0 Giroscope
1. - empty
2. - red (3v)
3. - blue (gnd)
4. - yellow
5. - green


## FT232 USB converter,
1. - grey VCC
2. - black (GND)
3. - violet (txd)
4. - green (rxd)
5. - blue (rts)
6. - brown (cts)


## Modem site
1. - orange VCC
2. - black (GND)
3. - yellow (txd)
4. - green (rxd)
5. - white (rts)
6. - blue (cts)


## Connection 2 Box
The second box have a bit diffrent configuration, which means GPS is in box together with sensors LSM9DS0 and BME280.
This approach have been chose in case GPS 1 will fail. Of course putting GPS to the senesor box will affect the meaurements as gps produce some heat, although we need to remember that box 2 is a spare box uses in case of failure.
The changes of pin connection in box two is as follow.
 
### Neo 6m GPS - Sensor BOX
1. - orange (5V)
2. - black (GND)
3. - white (TX) 
4. - brown (RX) 
5. - EMPTY
