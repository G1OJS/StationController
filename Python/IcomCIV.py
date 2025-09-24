import serial
import struct
import threading

def bcd_to_freq(bcd):
    # Converts 5 bytes of CI-V BCD to integer Hz
    return int("".join(f"{(b >> 4) & 0x0F}{b & 0x0F}" for b in reversed(bcd)))

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

