import serial

serial = serial.Serial("/dev/ttyS0",baudrate=9600)

print "Read data"

code = ''

while True:
    data = serial.read()
    if data == '\r':
         print(code)
         code = ''
    else:
         code = code + data
