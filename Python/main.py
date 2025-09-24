import tkinter as tk
import datetime
import time

import memoryFuncs
import ui
import mcu
import ants
#import wsjt

class AntennaControlApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Antenna Control")
        mcu.connect_arduino(self)
        ui.init_vars(self)
        ui.build_gui(self)
        ants.load_freq_dict(self)
        self.after(100,ui.update_frequency, self)

    def debug(self, txt):
        t = datetime.datetime.now(datetime.timezone.utc)
        print(t.strftime("%H:%M:%S") + ": " + txt)

if __name__ == "__main__":
    app = AntennaControlApp()
    app.mainloop()

