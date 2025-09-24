#!/usr/bin/env python3
import socket

HOST = "127.0.0.1"
PORT = 4532
freq_hz = 14000000

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

def checkWSJT():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(1)
        print(f"Waiting for WSJT-X on {HOST}:{PORT}")
        conn, addr = s.accept()
        print("Connected from", addr)

        with conn:
            buffer = ""
            data = conn.recv(1024)
            if not data:
                return
            buffer += data.decode("ascii")
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.strip()
                print("RX:", line)

                if line.startswith("\\get_powerstat"):
                    conn.sendall(b"1\n")
                elif line.startswith("\\chk_vfo"):
                    conn.sendall(b"CHKVFO 0\n")
                elif line.startswith("\\dump_state"):
                    conn.sendall(_dump_state().encode('ASCII'))
                elif line.startswith("f"):
                    conn.sendall(f"{freq_hz}\n".encode("ascii"))
                elif line.startswith("F "):
                    _, v = line.split()
                    freq_hz = v
                    print("Frequency set to", freq_hz)
                    conn.sendall(b"RPRT 0\n")
                elif line.startswith("q"):
                    conn.sendall(b"RPRT 0\n")
                    print("Client requested quit")
                    conn.close()
                    # Go back to accept a new connection instead of break
                    conn, addr = s.accept()
                    print("Connected from", addr)
                    continue
                elif line == "v":
                    conn.sendall(b"VFOA\n")
                    continue
                elif line.startswith("V"):      # upper-case V: set VFO
                    conn.sendall(b"RPRT 0\n")
                    continue
                else:
                    conn.sendall(b"RPRT 0\n")

