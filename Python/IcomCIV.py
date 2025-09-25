import serial
import struct
import threading

<<<<<<< Updated upstream
def bcd_to_freq(bcd):
    # Converts 5 bytes of CI-V BCD to integer Hz
    return int("".join(f"{(b >> 4) & 0x0F}{b & 0x0F}" for b in reversed(bcd)))
=======
class IcomCIV:
    import serial

    def __init__(self):
        self.serial_port = self.serial.Serial('COM4', 9600, timeout=0.1)

    def getFreqHz(self):
        while self.serial_port.read():
            pass
        self.serial_port.write(b'\xfe\xfe\x88\xe0\x03\xfd')
        self.buffer = bytearray()
        while True:
            self.buffer += self.serial_port.read()
            if(self.buffer[-2:] == b'\x00\xfd' ):
                break
        return int("".join(f"{(b >> 4) & 0x0F}{b & 0x0F}" for b in reversed(self.buffer[11:16])))

    def setFreqHz(self, freqHz):
    #    while self.serial_port.read():
     #       pass
        s = f"{freqHz:09d}"
        print(s)
        self.serial_port.write(b'\xfe\xfe\x88\xe0\x00')
        for b in [16*int(s[7])+int(s[8]),16*int(s[5])+int(s[6]),16*int(s[3])+int(s[4]),16*int(s[1])+int(s[2]), int(s[0])]:
            self.serial_port.write(bytes([b]))
        self.serial_port.write(b'\xfd')

    def setMode(self, mode):
        if(mode == 'USB'):
            self.serial_port.write(b'\xfe\xfe\x88\xe0\x01\x01\x03\xfd')
        elif(mode == 'USB-D'):
            self.serial_port.write(b'\xfe\xfe\x88\xe0\x26\x00\x01\x01\x01\xfd')
                

#icom = IcomCIV()
#icom = IcomCIV()
#icom.setUSBD();

#icom.setFreqHz(14123450)


>>>>>>> Stashed changes

def read_civ(app, serial_port, callback):
    buffer = bytearray()
    while True:
        byte = serial_port.read()
        if not byte:
            continue
        buffer += byte
        if byte == b'\xfd':
            if buffer.startswith(b'\xfe\xfe') and len(buffer) >= 10:
                cmd = buffer[4]
                if cmd == 0x00:
                    # This is a frequency broadcast
                    freq_bytes = buffer[4:9]
                    freq = bcd_to_freq(freq_bytes)
                    callback(app, freq/100)
            buffer.clear()

def connectIcom(app, catMonitor):
    # Set up serial port to CI-V
    ser = serial.Serial('COM4', 9600, timeout=0.1)
    print("Connected to Icom")
    # Launch reader in a thread
    threading.Thread(target=read_civ, args=(app, ser, catMonitor), daemon=True).start()
    print("Launched read_civ")

