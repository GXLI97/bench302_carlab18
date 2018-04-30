import serial
import time

try:
    ser = serial.Serial(
    port='/dev/serial0',
    baudrate=115200,
    timeout=0.5
    )
    print("success!")
except:
    ser = serial.Serial(
    port='/dev/ttyACM1',
    baudrate=115200,
    timeout=0.5
    )

time.sleep(1)

ser.write(b'\r\r')

time.sleep(2)

res=ser.read(100)
print(res.decode("utf-8"), end='', flush=True)
time.sleep(0.5)

print()
print("Printing distances for the next 10 seconds...")
time.sleep(0.5)
timeout = time.time() + 10

ser.write(b'lec\r')
res=ser.read(4)
print(res.decode("utf-8"),end='',flush=True)

while True:
    res=ser.read(37)
    if len(res)>0:
        print(res.decode("utf-8"), end='', flush=True)
    if time.time() > timeout:
        ser.write(b'lec\r')
        ser.close()
        break
