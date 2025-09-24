import pickle
import time
import mcu
import ui

def load_freq_dict(app):
    app.debug("Loading frequencies ...")
    try:
        with open('freqs.pkl', 'rb') as f:
            app.freqDict = pickle.load(f)
    except FileNotFoundError:
        app.freqDict = {}

def save_tuning_dictionary(app):
    app.debug("Updating dictionary:")
    app.magloopSaveDictBtn.config(state="disabled")
    f = app.fkHz.get()
    to_delete = [k for k in app.freqDict if abs(k - f) < 10]
    for key in to_delete:
        app.debug(f"Removed {key}, {app.freqDict[key]}")
        del app.freqDict[key]
    app.freqDict[f] = app.tuningStep.get()
    app.debug(f"Added {f}, {app.freqDict[f]}")
    with open('freqs.pkl', 'wb') as f:
        pickle.dump(app.freqDict, f)
    app.magloopSaveDictBtn.config(state="active")
    app.debug("Frequency dictionary saved")


def update_tuning_status(app):
    if not app.arduino.isOpen():
        return
    if app.arduino.in_waiting > 0:
        data = app.arduino.readline()
        app.debug(str(data))
        if b"CurrStep" in data and app.magloop_tuning_status.get() != "TUNED":
            try:
                step_val = int(float(data.decode().split(" ")[1]))
                app.tuningStep.set(step_val)
            except (ValueError, IndexError):
                pass
        if b"TUNED" in data:
            app.magloop_tuning_status.set("TUNED")
            app.tuneFromFrequencyBtn.config(state="active")
            app.debug("TUNED")
            if app.active_ant_was_selected_at_tuning_start:
                app.rxActive.invoke()
    app.after(50, update_tuning_status, app)
    
def isLoopFrequency(f):
    return ((7000 < f < 7200) or (3500 < f < 3800) or (1800 < f < 2000) or (5300 < f < 5400))

def tune_loop_from_frequency(app):
    f = app.fkHz.get()
    if not isLoopFrequency(f):
        return
    app.tuneFromFrequencyBtn.config(state="disabled")
    BotFreq = max((k for k in app.freqDict if k <= f), default=None)
    TopFreq = min((k for k in app.freqDict if k >= f), default=None)
    if BotFreq is None or TopFreq is None:
        return
    BotStep = app.freqDict[BotFreq]
    TopStep = app.freqDict[TopFreq]
    if abs(TopFreq - BotFreq) < 1:
        step = BotStep
    else:
        step = BotStep + (TopStep - BotStep) * (f - BotFreq) / (TopFreq - BotFreq)
    app.tuningStep.set(step)
    tune_loop_to_step(app)

def tune_loop_to_step(app):
    app.rxMain.invoke()
    app.txLoop.invoke()
    time.sleep(2)
    step = app.tuningStep.get()
    app.magloop_tuning_status.set(f"TUNING to {step}")
    mcu.send_command(app,f"T{int(step)}")
    app.debug(f"Tune to: {step}")
    app.after(50, update_tuning_status, app)

