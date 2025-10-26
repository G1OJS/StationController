from tkinter import ttk
import tkinter as tk
import memoryFuncs
from tkinter import simpledialog
import ants
import mcu
from enum import Enum

class FollowMode(Enum):
    DO_NOTHING = "Do nothing"
    SET_ANTENNAS = "Set antennas"
    SET_ANTENNAS_AND_TUNE = "Set antennas and tune loop"
    TUNE_LOOP_ONLY = "Tune loop only"

def init(app):
    app.fkHz = tk.IntVar()
    app.fkHz_old = 14000
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

def updateAntennaFrequency(app):
    mode = FollowMode(app.follow_mode.get())
    if mode == FollowMode.SET_ANTENNAS:
        set_antenna_selection_from_frequency(app)
    elif mode == FollowMode.SET_ANTENNAS_AND_TUNE:
        set_antenna_selection_from_frequency(app)
        ants.tune_loop_from_frequency(app)
    elif mode == FollowMode.TUNE_LOOP_ONLY:
        ants.tune_loop_from_frequency(app)
 
def checkRigFreqMode(app):
    fHz = app.icom.getFreqHz()
    if(not fHz):
        return
    app.fkHz.set(int(round(fHz / 1000)))
    if abs(app.fkHz.get() - app.fkHz_old) > 2:
        updateAntennaFrequency(app)
    app.fkHz_old = app.fkHz.get()
    app.after(1000, checkRigFreqMode, app)

def tune_to_memory(app, mem):
    app.fkHz.set(mem.freq_hz // 1000)
    app.icom.setFreqHz(mem.freq_hz)
    md = mem.mode
    if(md == 'USB-D'):
        app.icom.setMode('USB', True)
    else:
        app.icom.setMode(md)

def prompt_frequency_input(app):
    user_input = simpledialog.askstring("Set Frequency", "Enter frequency in kHz (e.g. 14074):")
    if user_input:
        try:
            freq_khz = float(user_input)
            freq_hz = int(freq_khz * 1000)
            app.fkHz.set(freq_khz)
            icom.setFreqHz(mem.freq_hz)
        except ValueError:
            print("Invalid frequency input.")

# =======================================    
# move below here into module 'ui_builder.py'


def build_gui(app):
    # Create Notebook (tab control)
    app.notebook = ttk.Notebook(app)
    app.notebook.pack(expand=True, fill='both')
    
    # Create frames and add to the main notebook
    app.main_tab = ttk.Frame(app.notebook)
    app.notebook.add(app.main_tab, text="Main")
    app.main_tab.rowconfigure(0, weight=1)
    
    app.settings_tab = ttk.Frame(app.notebook)
    app.notebook.add(app.settings_tab, text="Settings")    

    # Frequency Display
    app.freq_label = tk.Label(
        app.main_tab, textvariable=app.fkHz, anchor=tk.CENTER, bg="lightblue",
        height=1, width=30, bd=3, font=("Arial", 24, "bold"),
        fg="green", padx=15, pady=15, justify=tk.CENTER, relief=tk.RAISED
    )
    app.freq_label.grid(row=0, column=0, columnspan=3, pady=(10, 5))

    # Antenna Selection Frame
    antSelection_frame = tk.LabelFrame(app.main_tab, text="Antenna Select")
    antSelection_frame.grid(row=1, column=0, sticky="w", padx=10)

    # RX Antenna
    rx_frame = tk.LabelFrame(antSelection_frame, text="Receive Antenna")
    rx_frame.grid(row=0, column=0, sticky="w", padx=10)
    app.rxActive = tk.Radiobutton(rx_frame, text="Active Loop", variable=app.selectedRxAntenna,
                                   value="Active", command=lambda: mcu.send_command(app,"RA"))
    app.rxMain = tk.Radiobutton(rx_frame, text="Tx Antenna", variable=app.selectedRxAntenna,
                                 value="Main", command=lambda: mcu.send_command(app,"RM"))
    app.rxActive.pack(anchor=tk.W)
    app.rxMain.pack(anchor=tk.W)
    app.rxActive.invoke()

    # TX Antenna
    tx_frame = tk.LabelFrame(antSelection_frame, text="Transmit Antenna")
    tx_frame.grid(row=1, column=0, sticky="w", padx=10)
    app.txLoop = tk.Radiobutton(tx_frame, text="Magloop", variable=app.selectedTxAntenna,
                                 value="Loop", command=lambda: mcu.send_command(app,"ML"))
    app.txFan = tk.Radiobutton(tx_frame, text="Fan Dipole", variable=app.selectedTxAntenna,
                                value="Dipoles", command=lambda: mcu.send_command(app,"MD"))
    app.txLoop.pack(anchor=tk.W)
    app.txFan.pack(anchor=tk.W)

    # Magloop Controls
    loop_frame = tk.LabelFrame(app.main_tab, text="Magloop")
    loop_frame.grid(row=1, column=2, sticky="w", padx=10, pady=(5, 0))
    app.loopStatusLabel = tk.Label(loop_frame, textvariable=app.magloop_tuning_status)
    app.loopStatusLabel.pack()
    
    app.tuningStepBox = tk.Frame(loop_frame)
    app.tuningStepLabel = tk.Label(app.tuningStepBox, text="Step = ")
    app.tuningStepLabel.grid(row=0, column=0, sticky="w", padx=10)
    app.tuningStepEntry = tk.Entry(app.tuningStepBox, textvariable=app.tuningStep)
    app.tuningStepEntry.grid(row=0, column=1, sticky="w", padx=10)
    app.tuningStepEntry.bind("<Return>", lambda e: ants.tune_loop_to_step(app))
    app.tuningStepEntry.bind("<FocusOut>", lambda e: ants.tune_loop_to_step(app))
    app.tuningStepBox.pack()

    app.magloopButtonsBox = tk.Frame(loop_frame)
    app.tuneFromFrequencyBtn = tk.Button(app.magloopButtonsBox, text="Tune from freq", command=lambda: ants.tune_loop_from_frequency(app))
    app.tuneFromFrequencyBtn.grid(row=0, column=0, sticky="w", padx=10)
    app.magloopSaveDictBtn = tk.Button(app.magloopButtonsBox, text="Save Dictionary", command=lambda:  ants.save_tuning_dictionary(app))
    app.magloopSaveDictBtn.grid(row=0, column=1, sticky="w", padx=10)
    app.magloopButtonsBox.pack()

    # Follow Mode
    follow_frame = tk.LabelFrame(app.main_tab, text="On Frequency Change")
    follow_frame.grid(row=1, column=1, sticky="w", padx=10, pady=(5, 0))
    for mode in FollowMode:
        tk.Radiobutton(follow_frame, text=mode.value, variable=app.follow_mode, value=mode.value).pack(anchor=tk.W)

    # ========== Memory tabs ==========
    app.memsNotebook =ttk.Notebook(app.main_tab)
    app.memsNotebook.grid(row=2, column=0, sticky='nsew', padx=10, pady=10)
    
    # Clear previous memory panels if any
    if hasattr(app, "memory_panels"):
        for panel in app.memory_panels:
            panel.destroy()
        app.memory_panels = []

    # Add memory tabs *inside* the memory frame
    add_memory_tab(app, "memories_lf.csv", "LF", parent=app.memsNotebook)
    add_memory_tab(app, "memories_hf.csv", "HF", parent=app.memsNotebook)
    add_memory_tab(app, "memories_ft8.csv", "FT8", parent=app.memsNotebook)

def add_memory_tab(app, filepath, title="Memory Panel", max_columns=2, parent=None):
    if parent is None:
        parent = app
    if not hasattr(app, "memory_panels"):
        app.memory_panels = []

    memsFrame = ttk.Frame(parent)
    memories = memoryFuncs.load_sdruno_csv(filepath)
    for mem in memories:
        label = f"{mem.name} ({mem.freq_hz // 1000} kHz {mem.mode})"
        btn = tk.Button(memsFrame, text=label,
                        command=lambda m=mem: tune_to_memory(app, m))
        btn.pack(anchor="w")

    app.memsNotebook.add(memsFrame, text = title )
    return
