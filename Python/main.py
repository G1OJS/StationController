import tkinter as tk
import datetime
import time
import ui
import mcu
import ants


class AntennaControlApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Antenna Control")
        mcu.connect_arduino(self)
        ui.init(self)
        ui.build_gui(self)
        ants.load_freq_dict(self)

    def debug(self, txt):
#        if("CAT" in txt):
#            return
        t = datetime.datetime.now(datetime.timezone.utc)
        print(f"{t.strftime("%H:%M:%S")}: {txt}")

if __name__ == "__main__":
    app = AntennaControlApp()
    app.mainloop()

