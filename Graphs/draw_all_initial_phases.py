import json
import os
import numpy as np
import matplotlib.pyplot as plt

def lookForSeed(filename:str): # Szukanie Lambdy w nazwie pliku
    filename = filename[:-5]
    words = filename.split('_')
    for i, word in enumerate(words):
        if word == "seed":
            return words[i+1]

#Najwazniejsze dane do ruszania
input_json_path = '14_9'
output_path = 'graphs/lambd_14_9.png'
initial_phase = 1000*30*5 # mniej wiecej 
marker = 30000



for filename in os.listdir(input_json_path):
    x = []
    y = []

    seed = lookForSeed(filename)
    with open(os.path.join(input_json_path,filename), 'r') as jsonfile:
        data = json.load(jsonfile)

    for i ,item in enumerate(data.items()):
        if int(item[0]) < initial_phase:
            x.append(int(item[0]))
            y.append(item[1])
        else:
            break

    plt.plot(np.arange(x[0],max(x), step=((max(x)-x[0])/len(x))),y, label = f'seed {seed}')

# Marker
plt.axvline(x = marker, color = 'r')

# Titles
plt.title("Faza Początkowa")
plt.ylabel("Użytkownicy w sieci")
plt.xlabel("Czas [ms]")

plt.legend()
plt.savefig(output_path)
# plt.show()
