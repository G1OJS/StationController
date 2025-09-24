
class MemoryEntry:
    def __init__(self, name, freq_hz, mode='USB', bandwidth=3000):
        self.name = name
        self.freq_hz = int(freq_hz)
        self.mode = mode.upper()
        self.bandwidth = int(bandwidth)

    def __repr__(self):
        return f"{self.name}: {self.freq_hz} Hz, {self.mode}, BW {self.bandwidth}"

def load_sdruno_csv(filepath):
    memories = []
    try:
        with open(filepath, newline='') as csvfile:
            for row in csvfile.readlines():
                fields = row.split(",")
                try:
                    mem = MemoryEntry(
                        freq_hz=float(fields[0]),
                        mode=fields[2],
                        name=fields[3],
                        bandwidth=fields[6]
                    )
                    memories.append(mem)
                except (KeyError, ValueError):
                    continue
    except FileNotFoundError:
        print(f"Memory file not found: {filepath}")
    return memories


