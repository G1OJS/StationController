import socket
import struct

def send_set_frequency(freq_hz, tx=False):
    WSJTX_ADDR = ('127.0.0.1', 2237)  # WSJT-X default UDP port

    # Use a short ASCII ID and pad it *exactly* to 16 bytes
    client_id = "MyCtrl"
    client_id_padded = client_id.encode('utf-8').ljust(16, b'\x00')

    # WSJT-X "Set Frequency" message ID = 0x0002
    msg_id = 0x0002
    tx_flag = 1 if tx else 0

    # Structure: >16sHIQ (16-byte string, uint16, uint32, uint64)
    payload = struct.pack('>16sHIQ', b"0xadbccbda", msg_id, tx_flag, freq_hz)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(payload, WSJTX_ADDR)
    sock.close()

    print(f"Sent SetFreq to WSJT-X: {freq_hz} Hz (tx={tx})")
    print("Sending payload (hex):", payload.hex())


# Try setting 14.074 MHz
send_set_frequency(14074000)
