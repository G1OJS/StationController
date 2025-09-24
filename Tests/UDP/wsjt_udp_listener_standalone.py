import socket
import struct
import time

def get_freq():
    try:
        data, address = sock.recvfrom(1024)
    except Exception as e:              # No data available yet
        return None

    # get message type from byte 11  
    if(data[11] != 1):                  # not a status message
        return None                     

    offset = 22                         # Offset of the 8 frequency bytes in data
    # next line uses struct.unpack to get frequency from the 8 bytes
    # using bigendian format ('>') unsigned long long (8 bytes, 'Q')
    dial_freq = struct.unpack('>Q', data[offset:offset+8])[0]

    return dial_freq


global sock

UDP_PORT = 2237  # Default WSJT-X port
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', UDP_PORT))
sock.setblocking(False)  # Non-blocking

while(True):
    freq = get_freq()
    if(freq != None):
        print(freq)
    time.sleep(0.1)
