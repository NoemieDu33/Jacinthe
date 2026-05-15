from picozero import pico_led
import network
import socket
import time
import machine
from ssd1306 import SSD1306_I2C
from TB6612FNG import Motor
import utime

pico_led.on()




frequency = 50

BIN2 = 19 # 
BIN1 = 20 # 
STBY = 22 #
AIN1 = 21 #
AIN2 = 18 #
PWMA = 27
PWMB = 26
ofsetA = 1
ofsetB = 1

motor = Motor(BIN2,BIN1,STBY,AIN1,AIN2,PWMA,PWMB,ofsetA,ofsetB)

i2c = machine.I2C(sda=machine.Pin(16), scl=machine.Pin(17))
i2c.scan()
oled = SSD1306_I2C(128, 64, i2c)
oled.text("Not connected!",2,2,1)
oled.show()

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid="Jacinthe", password="MASCARPONE")

print("IP:", ap.ifconfig())

x = 0
y = 0

def apply_deadzone(v, dz=0.08):
    if abs(v) < dz:
        return 0
    return v

def set_motors(x, y):

    #x = apply_deadzone(x)
    #y = apply_deadzone(y)

    #left = y + x
    #right = y - x

    #left = max(-1, min(1, left))
    #right = max(-1, min(1, right))
    
    length = 100
    width = 50
    
    a = 61 + int(x*(width//2))
    b = 30 - int(y*(width//2))
    
    print(x, y, a, b)
    
    
    oled.fill(0)
    oled.ellipse(64,32,(width//2)+6, (width//2)+6,1)
    
    oled.text('x', a, b,1)

    oled.show()
    
    if abs(x)>0.3 or abs(y)>0.3:
        if x>0.3 and x<0.7:
            motor.forward(32000)
        elif x>=0.7:
            motor.forward(65000)
        elif x<-0.3 and x>-0.7:
            motor.backward(32000)
        elif x<-0.7:
            motor.backward(64000)
        else:
            if y>0.3 and y<0.7:
                motor.right(32000)
            elif y>=0.7:
                motor.right(65000)
            elif y<-0.3 and y>-0.7:
                motor.left(32000)
            elif y<-0.7:
                motor.left(64000)
    else:
        motor.stop()
        


html = open("index.html").read()  # ou coller si tu préfères

addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)
#s.settimeout(1)


while True:

    cl, addr = s.accept()
    req = cl.recv(1024).decode()


    # ========= PAGE HTML =========
    if "GET / HTTP" in req:

        cl.send("HTTP/1.1 200 OK\r\n")
        cl.send("Content-Type: text/html\r\n")
        cl.send("Connection: close\r\n\r\n")

        cl.sendall(html) # sendall -> send

    # ========= JOYSTICK =========
    elif "GET /move?" in req:

        qs = req.split("/move?")[1].split(" ")[0]

        params = {}

        for p in qs.split("&"):
            k, v = p.split("=")
            params[k] = float(v)

        x = params["x"]
        y = params["y"]

        set_motors(x, y)

        cl.send("HTTP/1.1 200 OK\r\n")
        cl.send("Content-Type: text/plain\r\n")
        cl.send("Connection: close\r\n\r\n")
        cl.send("OK")



    cl.close()


