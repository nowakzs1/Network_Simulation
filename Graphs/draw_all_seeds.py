import json
import os
import numpy as np
import matplotlib.pyplot as plt

def lookForSeed(filename:str):
    filename = filename[:-5]
    words = filename.split('_')
    for i, word in enumerate(words):
        if word == "seed":
            return words[i+1]

#Najwazniejsze dane do ruszania
input_json_path = '15_0'
output_path = 'graphs/seeds_15_0.png'
ilosc_stacji_bazowych = 4


for filename in os.listdir(input_json_path):
    # print(filename)
    seed = lookForSeed(filename)
    with open(os.path.join(input_json_path,filename), 'r') as jsonfile:
        data = json.load(jsonfile)

    x = list(data.keys())
    x = [int(i) for i in x]
    y = list(data.values())
    plt.plot(x,y, label = f'seed {seed}')

# Marker
plt.axhline(y=273*ilosc_stacji_bazowych, color='r',linestyle = '--')

# Titles
plt.title("Liczba uzytkownikow w sieci w czasie")
plt.ylabel("Uzytkownicy w sieci")
plt.xlabel("Czas [ms]")

plt.legend()
plt.savefig(output_path)
# plt.show()
