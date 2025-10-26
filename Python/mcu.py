import serial

def connect_arduino(app):
    app.debug("Connecting to Arduino")
    app.arduino = serial.Serial(port='COM7', baudrate=9600, timeout=0.1)
    while not app.arduino.isOpen():
        time.sleep(0.5)

def send_command(app, c):
    if c:
        s = f"<{c}>"
        app.debug("Commanding Arduino: " + s)
        app.arduino.write(s.encode('UTF-8'))
