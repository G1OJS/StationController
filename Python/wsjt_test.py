import socket
import time

def _dump_state():
    # hamlib expects this large table of rig info when connecting
    rigctlver = "0\n"
    rig_model = "2\n"
    itu_region = "0\n"
    freqs = "0.000000 30000000.000000"
    modes = "0x2f"  # AM LSB USB CW (NB)FM see hamlib/rig.h
    # no tx power, one VFO per channel, one antenna
    rx_range = "{} {} -1 -1 0x1 0x1\n".format(freqs, modes)
    rx_end = "0 0 0 0 0 0 0\n"
    tx_range = ""
    tx_end = "0 0 0 0 0 0 0\n"
    tuningsteps = ""
    for step in ["1", "100", "1000", "5000", "9000", "10000"]:
        tuningsteps += "{} {}\n".format(modes, step)
    steps_end = "0 0\n"
    ssbfilt = "0xc 2200\n"
    cwfilt = "0x2 500\n"
    amfilt = "0x1 6000\n"
    fmfilt = "0x20 12000\n"
    filt_end = "0 0\n"
    max_rit = "0\n"
    max_xit = "0\n"
    max_ifshift = "0\n"
    announces = "0\n"
    preamp = "\n"
    attenuator = "\n"
    get_func = "0x0\n"
    set_func = "0x0\n"
    get_level = "0x0\n"
    set_level = "0x0\n"
    get_parm = "0x0\n"
    set_parm = "0x0\n"
    vfo_ops = "vfo_ops=0x0\n"
    ptt_type = "ptt_type=0x0\n"
    done = "done\n"

    message = rigctlver + rig_model + itu_region
    message += rx_range + rx_end + tx_range + tx_end
    message += tuningsteps + steps_end
    message += ssbfilt + cwfilt + amfilt + fmfilt + filt_end
    message += max_rit + max_xit + max_ifshift + announces
    message += preamp + attenuator
    message += get_func + set_func + get_level + set_level
    message += get_parm + set_parm + vfo_ops + ptt_type + done

    return message

HOST = "127.0.0.1"
PORT = 4532

class wsjt:
    def __init__(self):
        self.freq = 14074000
        self.mode = 'USB'
        self.responses = {
            b'\\get_powerstat\n':   b"1\n",
            b'\\chk_vfo\n':         b"1\n",
            b'\\dump_state\n':      f"{_dump_state()}\n".encode("ascii"),
            b'v\n':                 b'VFOA 0\n'
            }
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((HOST, PORT))
        self.s.listen(1)
        self.conn, _  = self.s.accept()
        while self.poll():
            pass

    def getMode(self):
        return self.mode            

    def getFreq(self):
        return self.freq
    
    def setFreq(self, freq):
        self.freq = freq
        
    def poll(self):
        data = self.conn.recv(1024)
        print(data)
        if(data in self.responses):
            resp = self.responses[data]
            self.conn.sendall(resp)
        if (data == b'f VFOA\n'):
            self.conn.sendall(f"{self.getFreq()}\n".encode("ascii"))
        if (data == b'm VFOA\n'):
            self.conn.sendall(f"{self.getMode()}\n".encode("ascii"))
        if (data.startswith(b'F')):
            self.setFreq(data.split()[2])
            self.conn.sendall(b"RPRT 0\n")
        if (data == b'q'):
            self.conn, _  = self.s.accept()
            return True
        return False


# for testing this emulates what will live in the rest of the app:
test = wsjt()
while True:
    test.poll()
    time.sleep(0.1)





