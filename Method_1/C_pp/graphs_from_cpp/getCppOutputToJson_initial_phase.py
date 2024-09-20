import json
import os

def pushToJson(input_path, output_path):
    data = {}
    i=0
    initial_phase_len = 800
    with open(input_path, 'r') as file:
        for line in file.readlines():
            line = line[:-1]
            line = line.split(" ")

            if i == 0:    
                seed = int(line[1])
                users_per_second = float(line[3])
            elif i == 1:
                pass
            elif i in range(2,initial_phase_len):
                data.update({int(line[0]): int(line[1])})
            else:
                break
            i += 1
    
    with open(output_path, 'w') as file:
        json.dump(data, file, indent=1)
    
            

cpp_output_path = "./cpp_output"
json_output_path = "./jsons/initial_phase_800/"

if os.path.exists(json_output_path) == False:
    os.mkdir(json_output_path)

for directory in os.listdir(cpp_output_path):
    for file in os.listdir(os.path.join(cpp_output_path,directory)):
        if ".txt" in file:
            filename = file[:-4]
            new_dir = os.path.join(json_output_path,directory)
            if os.path.exists(new_dir) == False:
                os.mkdir(new_dir)
            pushToJson(os.path.join(cpp_output_path,directory,file),os.path.join(new_dir,filename+".json"))
            


# input_path = 'cpp_output/users_in_time_output_seed_5_lambda_3_1.txt'
# trim = 100

# data = {}
# i = 0
# with open(input_path, 'r') as file:
#     for line in file.readlines():
#         line = line[:-1]
#         line = line.split(" ")
        
#         if i == 0:    
#             seed = int(line[1])
#             users_per_second = float(line[3])
#         elif i % trim == 0 or i in range(99):
#             data.update({int(line[0]): int(line[1])})
#         i += 1

# output_path = f'results_04_06/initial_phase_seed_{seed}_lambda_{users_per_second}'
# output_path = output_path.replace(".","_")
# output_path = output_path + ".json"


# with open(output_path, 'w') as file:
#     json.dump(data, file, indent=1)
    
print(" END -> json created ")