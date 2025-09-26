import socket
import time
# https://hamlib.sourceforge.net/html/rigctld.1.html

def _dump_state():
    # hamlib expects this large table of rig info when connecting
    rigctlver = "0\n"
    rig_model = "2\n"
    itu_region = "0\n"
    fHzs = "0.000000 30000000.000000"
    modes = "0x2f"  # AM LSB USB CW (NB)FM see hamlib/rig.h
    # no tx power, one VFO per channel, one antenna
    rx_range = "{} {} -1 -1 0x1 0x1\n".format(fHzs, modes)
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
    def __init__(self, app = None):
        self.fHz = 14074000
        self.handshake_responses = {
            b'\\get_powerstat\n':   '1',
            b'\\chk_vfo\n':         '1',
            b'\\dump_state\n':      f"{_dump_state()}",
            b'v\n':                 'VFOA'
            }
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((HOST, PORT))
        self.s.listen(1)
        self.s.setblocking(False)
        self.conn = None
        self.app = app

    def acceptIfNeeded(self):
        if(self.conn):
            return True
        try:
            self.conn, _ = self.s.accept()
            self.conn.settimeout(0)
            self.app.debug("WSJTX: connected")
            return True
        except BlockingIOError:
            return False        

    def getfHz(self):
        return self.fHz
    
    def setfHz(self, fHz):
        self.fHz = fHz

    def respond(self, msg):
        msg_enc = (str(msg)+"\n").encode("ascii")
        self.app.debug(f"WSJTX: Sent to WSJTX: {msg_enc}")
        self.conn.sendall(msg_enc)
    
    def poll(self):
        if(not self.acceptIfNeeded()):
            return False    # no WSJT comms
        try:
            data = self.conn.recv(1024)
        except (BlockingIOError, socket.timeout):
            return
        self.app.debug(f"WSJTX: Received from WSJTX: {data}")
        if(data in self.handshake_responses):
            resp = self.handshake_responses[data]
            self.respond(resp)

        if (data.startswith(b't')):
            self.respond("0")

        if (data.startswith(b's')):
            self.respond("RPRT 0")
            
        if (data == b'f VFOA\n'):
            self.respond(self.getfHz())
        if (data == b'm VFOA\n'):
            self.respond("USB 3000")
            self.respond("RPRT 0")
            
        if (data.startswith(b'F')):
            self.setfHz(float(data.split()[2]))
            self.respond("RPRT 0")

        if(data == b'\\get_lock_mode\n'):
            self.respond("0")         
            self.respond("RPRT 0")

        if(data ==  b'M VFOA PKTUSB -1\n'):
            self.respond("RPRT 0")

        if(data == b'T VFOA 1\n'):
            #PTT on
            self.respond("RPRT 0")            

        if(data == b'T VFOA 0\n'):
            #PTT off
            self.respond("RPRT 0")            

            
        if (data == b'q\n'):
            self.s.close()
            self.acceptIfNeeded()
            return True
        return False


def test():
# for testing this emulates what will live in the rest of the app:
    wsjtx = wsjt()
    while True:
        wsjtx.poll()
        self.app.debug("WSJTX: Running")
        time.sleep(2)

#test()




