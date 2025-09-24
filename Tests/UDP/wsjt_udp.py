import socket
import struct

UDP_PORT = 2237  # Default WSJT-X port

class WSJTX_UDP:
    def __init__(self, port=UDP_PORT):
        self.port = port
        self.addr = ('127.0.0.1', self.port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', self.port))
        self.sock.setblocking(False)  # Non-blocking

        self.client_id = "MyAntennaCtrl".encode('utf-8')
        self.client_id_padded = self.client_id + b'\x00' * (16 - len(self.client_id))

    def get_frequency(self):
        try:
            data, _ = self.sock.recvfrom(1024)
        except BlockingIOError:
            return None  # No data available yet

        if len(data) < 32 or data[11] != 1:
            return None  # Not a WSJT-X status message

        offset = 22
        dial_freq = struct.unpack('>Q', data[offset:offset+8])[0]
        return dial_freq

    def set_frequency(self, freq_hz, tx=False):
        # Send Set Frequency command to WSJT-X
        msg_id = 0x0002
        tx_flag = 1 if tx else 0

       # self.client_id = b'JTSDK\x00' * 3 + b'\x00'  # total 16 bytes
        self.client_id = b'\x00' * 16
        self.client_id_padded = self.client_id + b'\x00' * (16 - len(self.client_id))
        payload = struct.pack('>16sHIQ', self.client_id_padded, msg_id, tx_flag, freq_hz)
            # Create a new socket for sending (do not reuse self.sock)
        send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        send_sock.sendto(payload, self.addr)
        send_sock.close()
        
        print(f"[WSJT-X] Set frequency to {freq_hz} Hz (tx={tx})")
