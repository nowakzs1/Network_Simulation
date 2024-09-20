import json
import matplotlib.pyplot as plt
import numpy as np
import os

input_directory = "./jsons/initial_phase_800/"
output_directory = "./graphs/initial_phase_800/"
day_ms = 86400000
h_8 = day_ms/3
h_8_6 = h_8+ day_ms/4
h_8_6_4 = h_8_6+ day_ms/6

if os.path.exists(output_directory) == False:
    os.mkdir(output_directory)

# Funkcja do wczytywania danych z pliku JSON
def load_data(nazwa_pliku):
    with open(nazwa_pliku, 'r') as file:
        data = json.load(file)
    keys = []
    for i in data.keys():
        keys.append(int(i))
    values = list(data.values())
    return keys, values

for directory in os.listdir(input_directory):
    plt.figure()
    for jsonfile in os.listdir(os.path.join(input_directory,directory)):
        
        x,y = load_data(os.path.join(input_directory,directory,jsonfile))
        # plt.plot([i for i in range(len(x))],y)
        plt.plot(np.arange(x[0],max(x), step=((max(x)-x[0])/len(x))),y)
        # plt.show()
    
    plt.axvline(x=25000, color = "red")
    plt.title("Faza początkowa")
    plt.xlabel("Czas [ms]")
    plt.ylabel("Ilosc zapelnionych RB")
    # plt.xticks()
    new_dir = os.path.join(output_directory,directory)
    if os.path.exists(new_dir) == False : os.mkdir(new_dir)
        
    plt.savefig(os.path.join(new_dir,f"{jsonfile[0]}_h_8_6_4_end.png"))
    plt.clf()
    
# plt.show()
print("End -> graphs has been drawn")


