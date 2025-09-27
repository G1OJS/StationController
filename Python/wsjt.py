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
    message += get_parm + set_parm + vfo_ops + ptt_type
    message += done

    return message

HOST = "127.0.0.1"
PORT = 4532

class wsjt:
    def __init__(self, app, pttOn, pttOff):
        self.wsjtHz = 0
        self.handshake_responses = {
            b'\\get_powerstat\n':   '1',
            b'\\chk_vfo\n':         '1',
            b'\\dump_state\n':      f"{_dump_state()}",
            b'v\n':                 'VFOA'
            }
        self.app = app
        self.pttOn = pttOn
        self.pttOff = pttOff
        self.conn = None
        self.initSocket()

    def initSocket(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((HOST, PORT))
        self.s.listen(1)
        self.s.setblocking(False)

    def serveWSJT(self):
        self.app.after(100, self.serveWSJT)
        if(not self.s):
            self.initSocket()
        if(not self.conn):
            try:
                self.conn, _ = self.s.accept()
                self.conn.settimeout(0)
                self.app.debug("WSJTX: connected")
            except BlockingIOError:
                return
        if(not self.conn):
            return
        try:
            data = self.conn.recv(1024)
        except BlockingIOError:
            return
        if(data==b''):
            self.app.debug("WSJTX: connection closed")
            self.conn.close()
            self.conn = None
            return
        self.processWSJTMsg(data)

    def respondToWSJT(self, msg):
        if(not self.conn):
            return
        msg_enc = (str(msg)+"\n").encode("ascii")
        self.app.debug(f"WSJTX: Sent to WSJTX: {msg_enc}")
        self.conn.sendall(msg_enc)
    
    def processWSJTMsg(self, data):
        self.app.debug(f"WSJTX: Received from WSJTX: {data}")
        if(data in self.handshake_responses):
            resp = self.handshake_responses[data]
            self.respondToWSJT(resp)

        if (data.startswith(b't')):
            self.respondToWSJT("0")

        if (data.startswith(b's')):
            self.respondToWSJT("RPRT 0")
            
        if (data == b'f VFOA\n'):
            self.respondToWSJT(self.app.fkHz.get()*1000)
        if (data == b'm VFOA\n'):
            self.respondToWSJT("USB 3000")
            self.respondToWSJT("RPRT 0")
            
        if (data.startswith(b'F')):
            self.wsjtHz = float(data.split()[2])
            self.respondToWSJT("RPRT 0")

        if(data == b'\\get_lock_mode\n'):
            self.respondToWSJT("0")         
            self.respondToWSJT("RPRT 0")

        if(data ==  b'M VFOA PKTUSB -1\n'):
            self.respondToWSJT("RPRT 0")

        if(data == b'T VFOA 1\n'):
            self.pttOn()
            self.respondToWSJT("RPRT 0")            

        if(data == b'T VFOA 0\n'):
            self.pttOff()
            self.respondToWSJT("RPRT 0")            

        if (data == b'q\n'):
            self.conn.close()
            self.conn = None
 







