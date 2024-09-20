import json
import os

input_path = "./cpp_output/04_06_lambda_3_0_different_seed"



for filename in os.listdir(input_path):
    
    with open(os.path.join(input_path,filename), 'r') as file:
        licznik_195 = 0
        licznik_190 = 0
        licznik_180 = 0
        for line in file.readlines():
            line = line[:-1]
            line = line.split(" ")
            
            if int(line[1])  == 195:
                licznik_195 += 1
            elif int(line[1]) > 190:
                licznik_190 +=1
            elif int(line[1]) > 180:
                licznik_180 +=1
    
    print(filename)
    print(f"wartosci wiecej niz 195 jest {licznik_195}")
    print(f"wartosci wiecej niz 190 jest {licznik_190}")
    print(f"wartosci wiecej niz 180 jest {licznik_180}")
    print('\n')