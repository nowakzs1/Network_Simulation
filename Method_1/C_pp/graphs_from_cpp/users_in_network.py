import json
import matplotlib.pyplot as plt
import numpy as np
import os

input_directory = "./jsons/05_06_max_lambda/"
output_directory = "./graphs/05_06_max_lambda/"
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
    for jsonfile in os.listdir(os.path.join(input_directory,directory)):
        x,y = load_data(os.path.join(input_directory,directory,jsonfile))
        x_8 = [i for i in x if int(i)<h_8]
        y_8 = [value for i,value in enumerate(y) if i<len(x_8)]

        a = len(x_8)
        x_8_6 = [i for i in x if h_8< int(i) <h_8_6]
        b = len(x_8) + len(x_8_6)
        y_8_6 = [value for i,value in enumerate(y) if a<= i < b ]

        a = len(x_8) + len(x_8_6)
        x_8_6_4 = [i for i in x if h_8_6< int(i) <h_8_6_4]
        b = len(x_8) + len(x_8_6) + len(x_8_6_4)  
        y_8_6_4 = [value for i,value in enumerate(y) if a <= i <b ]

        a = len(x_8) + len(x_8_6) + len(x_8_6_4)
        x_end= [i for i in x if h_8_6_4< int(i) <day_ms]
        b = len(x_8) + len(x_8_6) + len(x_8_6_4) + len(x_end)
        y_end = [value for i,value in enumerate(y) if a <= i < b ]

        jsonfile = jsonfile.split(".")
        plt.plot(x_8,y_8)
        # plt.plot(np.arange(x_8[0],max(x_8), step=((max(x_8)-x_8[0])/len(x_8))),y_8)
        # plt.savefig(os.path.join(output_directory,f"{jsonfile[0]}_h_8.png"))
    
        plt.plot(x_8_6,y_8_6)
        # plt.plot(np.arange(x_8_6[0],max(x_8_6), step=((max(x_8_6)-x_8_6[0])/len(x_8_6))),y_8_6)
        # plt.savefig(os.path.join(output_directory,f"{jsonfile[0]}_h_8_6.png"))

        plt.plot(x_8_6_4,y_8_6_4)
        # plt.plot(np.arange(x_8_6_4[0],max(x_8_6_4), step=((max(x_8_6_4)-x_8_6_4[0])/len(x_8_6_4))),y_8_6_4)
        # plt.savefig(os.path.join(output_directory,f"{jsonfile[0]}_h_8_6_4.png"))

        plt.plot(x_end,y_end)
        # plt.plot(np.arange(x_end[0],max(x_end), step=((max(x_end)-x_end[0])/len(x_end))),y_end)

        
        
        # plt.plot(range(86400000),[195 for i in range(86400000)], color= "red")
        # plt.axvline(x=25000, color = "red")
        plt.hlines(y=195,xmin=0,xmax=86400000, linewidth=2, color="red")
        # plt.xticks(np.arange(x[0],max(x), step=((max(x)-x[0])/len(x))))
        new_dir = os.path.join(output_directory,directory)
        if os.path.exists(new_dir) == False : os.mkdir(new_dir)
        plt.title("Liczba użytkowników w sieci w czasie")
        plt.ylabel("Liczba użytkowników")
        plt.xlabel("Czas [ms]")
        plt.savefig(os.path.join(new_dir,f"{jsonfile[0]}_h_8_6_4_end.png"))
        plt.clf()
    
# plt.show()
print("End -> graphs has been drawn")


