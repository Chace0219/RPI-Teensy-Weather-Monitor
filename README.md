# RPI-Teensy-Weather-Monitor
RPI &amp; Teensy 3.6 based Weather Monitor Device 

# Wiring
![wiring diagram](https://github.com/Chace0219/RPI-Teensy-Weather-Monitor/blob/master/Wiring_Schematics.png)


# Fucntinoalitiy List
1) RPI Side
- WUnderground Weather API Client using internet IP
- AWS IOT client
- UART CRC32 Master for Arduino ( weather info and position information)

2) Arduino Side
- wehather symbols using stepper motor, ws2812, small water pump
- Serial slave from RPI
