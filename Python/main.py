import tkinter as tk
import datetime
import time
import ui
import mcu
import ants
import IcomCIV
import wsjt


class AntennaControlApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Antenna Control")
        mcu.connect_arduino(self)
        ui.init(self)
        ui.build_gui(self)
        ants.load_freq_dict(self)
        self.icom = IcomCIV.IcomCIV(self)
        self.wsjtx = wsjt.wsjt(self, self.icom.setPTTON, self.icom.setPTTOFF)
        self.wsjtx.serve()
        self.after(10, ui.checkRigFreqMode, self)

    def debug(self, txt):
 #       if("CAT" in txt):
 #           return
        if("Received" in txt):
            print()
        t = datetime.datetime.now(datetime.timezone.utc)
        print(f"{t.strftime("%H:%M:%S")}: {txt}")

if __name__ == "__main__":
    app = AntennaControlApp()
    app.mainloop()

