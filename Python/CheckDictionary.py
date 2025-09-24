import pickle

# get the frequency dictionary
print("Loading frequencies ...")
with open('freqs.pkl', 'rb') as f:
    freqDict = pickle.load(f)

for Fr, St in freqDict.items():
  print(Fr, St)