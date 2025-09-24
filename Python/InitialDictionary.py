import pickle

freqDict={0: 20,
1800: 50,
1840: 57,
3500: 289,
3573: 311,
3800: 333,
5357: 593,
7001: 857,
7074: 884,
7200: 900,
30000:1000  }

print(freqDict)


with open('freqs.pkl', 'wb') as f:
  pickle.dump(freqDict, f)

