import tkinter as tk
import memoryFuncs
from tkinter import simpledialog
from rigctrld import rigctrld
import ants
import mcu
from enum import Enum

class FollowMode(Enum):
    DO_NOTHING = "Do nothing"
    SET_ANTENNAS = "Set antennas"
    SET_ANTENNAS_AND_TUNE = "Set antennas and tune loop"
    TUNE_LOOP_ONLY = "Tune loop only"

def init_vars(app):
        app.fkHz = tk.IntVar()
        app.selectedRxAntenna = tk.StringVar()
        app.selectedTxAntenna = tk.StringVar()
        app.magloop_tuning_status = tk.StringVar(value="-----")
        app.tuningStep = tk.IntVar()
        app.follow_mode = tk.StringVar(value=FollowMode.SET_ANTENNAS_AND_TUNE.value)
        app.active_ant_was_selected_at_tuning_start = False

def set_antenna_selection_from_frequency(app):
    f = app.fkHz.get()
    isLoopFrequency = ((7000 < f < 7200) or (3500 < f < 3800) or (1800 < f < 2000) or (5300 < f < 5400))
    if (isLoopFrequency):
        app.rxMain.invoke()
        app.txLoop.invoke()
    else:
        app.txFan.invoke()
    if f < 30000:
        app.rxActive.invoke()
    else:
        app.rxMain.invoke()
 
def update_frequency(app):
    fHz = rigctrld.get_frequency()
    if fHz:
        fkHz_old = app.fkHz.get()
        app.fkHz.set(int(round(fHz / 1000)))
        if abs(app.fkHz.get() - fkHz_old) > 2:
            mode = FollowMode(app.follow_mode.get())
            if mode == FollowMode.SET_ANTENNAS:
                set_antenna_selection_from_frequency(app)
            elif mode == FollowMode.SET_ANTENNAS_AND_TUNE:
                set_antenna_selection_from_frequency(app)
                ants.tune_loop_from_frequency(app)
            elif mode == FollowMode.TUNE_LOOP_ONLY:
                ants.tune_loop_from_frequency(app)
    app.after(250, update_frequency, app)


def add_memory_panel(app, filepath, title="Memory Panel", max_columns=2):
    if not hasattr(app, "memory_panels"):
        app.memory_panels = []

    index = len(app.memory_panels)
    row = index // max_columns
    col = index % max_columns

    frame = tk.LabelFrame(app, text=title)
    frame.grid(row = row +2, column=col, padx=10, pady=5, sticky="nw")

    memories = memoryFuncs.load_sdruno_csv(filepath)
    for mem in memories:
        label = f"{mem.name} ({mem.freq_hz // 1000} kHz {mem.mode})"
        btn = tk.Button(frame, text=label,
                        command=lambda m=mem: tune_to_memory(app, m))
        btn.pack(anchor="w")

    app.memory_panels.append(frame)
    return frame


def add_memory_panel_old(app, filepath):
    app.memory_frame = tk.LabelFrame(app, text="Memory Panel")
    app.memory_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=5)

    app.memories = memoryFuncs.load_sdruno_csv(filepath)
    for mem in app.memories:
        label = f"{mem.name} ({mem.freq_hz//1000} kHz {mem.mode})"
        btn = tk.Button(app.memory_frame, text=label,
                        command=lambda m=mem: tune_to_memory(app,m))
        btn.pack(anchor="w")

def tune_to_memory(app, mem):
    app.fkHz.set(mem.freq_hz // 1000)
    rigctrld.rigctl_session([
        f"F {mem.freq_hz}",
        f"M {mem.mode} {mem.bandwidth}"
    ])

def prompt_frequency_input(app):
    user_input = simpledialog.askstring("Set Frequency", "Enter frequency in kHz (e.g. 14074):")
    if user_input:
        try:
            freq_khz = float(user_input)
            freq_hz = int(freq_khz * 1000)
            app.fkHz.set(freq_khz)
            rigctrld.set_frequency(freq_hz)
        except ValueError:
            print("Invalid frequency input.")
    
def build_gui(app):
    # Frequency Display
    app.freq_label = tk.Label(
        app, textvariable=app.fkHz, anchor=tk.CENTER, bg="lightblue",
        height=1, width=30, bd=3, font=("Arial", 24, "bold"),
        fg="green", padx=15, pady=15, justify=tk.CENTER, relief=tk.RAISED
    )
    app.freq_label.grid(row=0, column=0, columnspan=2, pady=(10, 5))

    # Bind right-click (on Windows it's <Button-3>, macOS may need <Button-2>)
 #   app.freq_label.bind("<Button-3>", prompt_frequency_input(app))

    # RX Antenna
    rx_frame = tk.LabelFrame(app, text="Receive Antenna")
    rx_frame.grid(row=1, column=0, sticky="w", padx=10)
    app.rxActive = tk.Radiobutton(rx_frame, text="Active Loop", variable=app.selectedRxAntenna,
                                   value="Active", command=lambda: mcu.send_command(app,"RA"))
    app.rxMain = tk.Radiobutton(rx_frame, text="Tx Antenna", variable=app.selectedRxAntenna,
                                 value="Main", command=lambda: mcu.send_command(app,"RM"))
    app.rxActive.pack(anchor=tk.W)
    app.rxMain.pack(anchor=tk.W)
    app.rxActive.invoke()

    # TX Antenna
    tx_frame = tk.LabelFrame(app, text="Transmit Antenna")
    tx_frame.grid(row=1, column=1, sticky="w", padx=10)
    app.txLoop = tk.Radiobutton(tx_frame, text="Magloop", variable=app.selectedTxAntenna,
                                 value="Loop", command=lambda: mcu.send_command(app,"ML"))
    app.txFan = tk.Radiobutton(tx_frame, text="Fan Dipole", variable=app.selectedTxAntenna,
                                value="Dipoles", command=lambda: mcu.send_command(app,"MD"))
    app.txLoop.pack(anchor=tk.W)
    app.txFan.pack(anchor=tk.W)

    # Magloop Controls
    loop_frame = tk.LabelFrame(app, text="Magloop")
    loop_frame.grid(row=2, column=0, sticky="w", padx=10, pady=(5, 0))
    app.loopStatusLabel = tk.Label(loop_frame, textvariable=app.magloop_tuning_status)
    app.loopStatusLabel.pack()
    app.tuneFromFrequencyBtn = tk.Button(loop_frame, text="Tune to Freq", command=lambda: ants.tune_loop_from_frequency(app))
    app.tuneFromFrequencyBtn.pack(anchor=tk.W)
    app.tuningStepEntry = tk.Entry(loop_frame, textvariable=app.tuningStep)
    app.tuningStepEntry .pack()
    app.tuneToStepBtn = tk.Button(loop_frame, text="Tune to Step", command=lambda: ants.tune_loop_to_step(app))
    app.tuneToStepBtn.pack(anchor=tk.W)
    app.magloopSaveDictBtn = tk.Button(loop_frame, text="Save Dictionary", command=lambda:  ants.save_tuning_dictionary(app))
    app.magloopSaveDictBtn.pack(anchor=tk.W)

    # Follow Mode
    follow_frame = tk.LabelFrame(app, text="On Frequency Change")
    follow_frame.grid(row=2, column=1, sticky="w", padx=10, pady=(5, 0))
    for mode in FollowMode:
        tk.Radiobutton(follow_frame, text=mode.value, variable=app.follow_mode, value=mode.value).pack(anchor=tk.W)

    # Memory Panel
    add_memory_panel(app,"memories_lf.csv","LF")
    add_memory_panel(app,"memories_hf.csv","HF")
    add_memory_panel(app,"memories_ft8.csv","FT8")
