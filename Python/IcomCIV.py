
class IcomCIV:
    import serial

    def __init__(self, app):
        self.app = app
        self.app.debug("Connecting to COM4")
        self.serial_port = self.serial.Serial('COM4', baudrate=9600, timeout=0.1)
        if (self.serial_port):
            self.app.debug("Connected to COM4")
        
    def sendSerial(self, msg):
        self.app.debug(f"CAT: {msg}")
        self.serial_port.write(msg)

    def getFreqHz(self):
        while self.serial_port.read():
            pass
        requestFrequency = b'\xfe\xfe\x88\xe0\x03\xfd'
        self.sendSerial(requestFrequency)
        resp = self.serial_port.read_until(expected = b'\x00\xfd')
        if(resp == requestFrequency):
            return False
        self.app.debug(f"CAT: Icom responded with {resp}")
        return int("".join(f"{(b >> 4) & 0x0F}{b & 0x0F}" for b in reversed(resp[11:16])))

    def setFreqHz(self, freqHz):
        s = f"{freqHz:09d}"
        self.app.debug(f"CAT: {s}")
        self.sendSerial(b'\xfe\xfe\x88\xe0\x00')
        for b in [16*int(s[7])+int(s[8]),16*int(s[5])+int(s[6]),16*int(s[3])+int(s[4]),16*int(s[1])+int(s[2]), int(s[0])]:
            self.sendSerial(bytes([b]))
        self.sendSerial(b'\xfd')

    def setMode(self, mode):
        if(mode == 'USB'):
            self.sendSerial(b'\xfe\xfe\x88\xe0\x01\x01\x03\xfd')
        elif(mode == 'USB-D'):
            self.sendSerial(b'\xfe\xfe\x88\xe0\x26\x00\x01\x01\x01\xfd')
                

#icom = IcomCIV()
#icom.setUSBD();
#icom.setFreqHz(14123450)


