import serial
import struct
import tkinter as tk

def bcd_to_freq(bcd):
    # Converts 5 bytes of CI-V BCD to integer Hz
    return int("".join(f"{(b >> 4) & 0x0F}{b & 0x0F}" for b in reversed(bcd)))

def read_civ(serial_port, callback):
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
                    callback(freq)
            buffer.clear()

# Tkinter GUI
root = tk.Tk()
label = tk.Label(root, font=("Courier", 20))
label.pack()

def update_freq_display(freq):
    mhz = freq / 1e8
    label.config(text=f"{mhz:.3f} MHz")

# Set up serial port to CI-V (adjust as needed)
ser = serial.Serial('COM4', 9600, timeout=0.1)

# Launch reader in a thread
import threading
threading.Thread(target=read_civ, args=(ser, update_freq_display), daemon=True).start()

root.mainloop()
