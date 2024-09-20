import argparse
import json
import math
import time
import os
from enum import Enum

parser = argparse.ArgumentParser() 
parser.add_argument('-s', '--seed', type=int, default=20_000_000)
parser.add_argument('-ld', '--lambd', type=float, default=14.8) 
parser.add_argument('-rb', '--resource_blocks', type=int, default=273)
parser.add_argument('-lg', '--logs', type=bool, default=False)

args = parser.parse_args()

if not os.path.exists(f'{args.lambd}'):
    os.mkdir(f'{args.lambd}') 

output_path = f'{args.lambd}/time_networkusers_lambda_{args.lambd}_seed_{args.seed}.json' 

class Generator():
    def __init__(self, seed:int, m: float = 2147483647.0, a: float = 16807.0, q: float = 127773.0, r: float = 2836.0 ) -> None:
        self.m = m
        self.a = a
        self.q = q
        self.r = r
        self.seed = seed
    
    def rand(self):
        h = self.seed // self.q
        self.seed = self.a * (self.seed - self.q * h) - self.r * h

        if(self.seed < 0):
            self.seed += self.m
        
        return self.seed/self.m

class Generator_UniformDistribution(Generator):

    def __init__(self, min:int, max:int, seed:int, m: float = 2147483647, a: float = 16807, q: float = 127773, r: float = 2836) -> None:
        super().__init__(seed, m, a, q, r)
        self.min = min
        self.max = max
    
    def get(self):
        ret = super().rand() * (self.max - self.min) + self.min
        return int(ret)

class Generator_ExponentialDistribution(Generator):

    def __init__(self, seed:int, m: float = 2147483647, a: float = 16807, q: float = 127773, r: float = 2836) -> None:
        super().__init__(seed, m, a, q, r)
    
    def get(self, lambd: float):
        k:float = super().rand()
        return int(-1000/lambd*math.log(k)) # 1000/lambda czas w milisekundach
    
class Sched():
    
    def __init__(self) -> None:
        self.id = 0
        self.next_time = 0
    
    def run(self, *args):
        return self.toRun(*args)
    
    def toRun(self):
        return 0

class BS():
    pass

class Sched_ChangeBsStatus(Sched):
    
    def __init__(self, id:str, bs:BS) -> None:
        super().__init__()
        self.id = id
        self.bs = bs
    
    def toRun(self,actual_time):
        self.bs.changeStatus(actual_time)
        self.next_time = 0

    def set(self,actual_time, adder = 50):
        self.next_time = actual_time + adder

class BsStatus(Enum):
    WakingUp = 0
    Active = 1
    NoddingOff = 2
    Sleeping = 3

class BS():
    
    def __init__(self, id, rb_max:int, low = 0.2, high = 0.8) -> None:
        self.id = id
        self.users_list = []
        self.rb_max = rb_max
        self.rb_taken = len(self.users_list)
        self.disconnected_users = 0
        self.all_users = 0

        #tresholds
        self.H = int(self.rb_max*high)
        self.L = int(self.rb_max*low)

        #status variables
        self.can_sleep = False
        self.status = BsStatus.Active
        self.passed_to_neighbour_1 = False
        self.status_changer = None
        self.status_change_time_length = 50

        #power consumption
        self.sleeping_power_consumption = 1
        self.working_power_consumption = 200
        self.status_change_power_consumption = 1000
        self.sleeping_time = 0
        self.working_time = 0
        self.power_consumed = 0
        self.power_consumed_by_changing_status = 0
        self.last_status_change_time = 0

    def addSchedToChangeStatus(self, status_changer:Sched_ChangeBsStatus):
        self.status_changer = status_changer
    
    def addNeighbour(self, neighbour_1, neighbour_2):
        self.neighbour_1 = neighbour_1
        self.neighbour_2 = neighbour_2
    
    def connect(self,mi, actual_time, passed = False):
        if self.rb_taken < self.rb_max and self.status == BsStatus.Active:
            
            self.users_list.append(mi)
            self.rb_taken = len(self.users_list)
            
            if self.rb_taken >= self.H:
                # WakeUp neighbour
                if self.neighbour_1.status == BsStatus.Sleeping:
                    self.neighbour_1.changeStatus(actual_time)
                    self.neighbour_1.users_list, self.neighbour_1.rb_taken = self.divideUsersList()
                    if self.neighbour_1.rb_taken > self.neighbour_1.L :
                        self.neighbour_1.can_sleep = True
                    

                elif self.neighbour_2.status == BsStatus.Sleeping:
                    self.neighbour_2.changeStatus(actual_time)
                    self.neighbour_2.users_list, self.neighbour_2.rb_taken = self.divideUsersList()
                    if self.neighbour_2.rb_taken > self.neighbour_2.L :
                        self.neighbour_2.can_sleep = True

            elif self.rb_taken > self.L and self.can_sleep == False:
                self.can_sleep = True
            
            return True
        
        else:
            # handover
            self.handoverToNeighbours(mi, actual_time)
            
    def divideUsersList(self):
        for_neighbour = []
        temp = []

        for i, user_mi in enumerate(self.users_list):
            if i < len(self.users_list)/2:
                for_neighbour.append(user_mi)
            else:
                temp.append(user_mi)
        
        self.users_list = temp
        self.rb_taken = len(self.users_list)
        return for_neighbour, len(for_neighbour)
        
    def handoverToNeighbours(self, mi, actual_time):

        if self.passed_to_neighbour_1 == False:
            if self.neighbour_1.status == BsStatus.Active and self.neighbour_1.rb_taken < self.neighbour_1.rb_max:
                self.passed_to_neighbour_1 = True
                connected_status = self.neighbour_1.connect(mi, actual_time, True)
                return connected_status
            if self.neighbour_2.status == BsStatus.Active and self.neighbour_2.rb_taken < self.neighbour_2.rb_max:
                connected_status = self.neighbour_2.connect(mi, actual_time, True)
                return connected_status
            else:
                self.disconnected_users += 1
                return False

                 
        else:
            if self.neighbour_2.status == BsStatus.Active and self.neighbour_2.rb_taken < self.neighbour_2.rb_max:
                self.passed_to_neighbour_1 = False
                connected_status = self.neighbour_2.connect(mi, actual_time, True)
                return connected_status
            if self.neighbour_1.status == BsStatus.Active and self.neighbour_1.rb_taken < self.neighbour_1.rb_max:
                connected_status = self.neighbour_1.connect(mi, actual_time, True)
                return connected_status
            else:
                self.disconnected_users += 1
                return False
        
        
    def getMin(self):
        if not self.users_list:
            return 0
        else:
            return min(self.users_list)
    
    def reduceRB(self,actual_time):
        if self.users_list:
            self.users_list.remove(actual_time)
            if self.can_sleep == True and self.rb_taken <= self.L:
                #sleep
                self.changeStatus(actual_time)
        self.rb_taken = len(self.users_list)
    
    def changeStatus(self, actual_time):

        if self.status == BsStatus.Active:

            for user_mi in self.users_list:
                self.handoverToNeighbours(user_mi,actual_time)
            self.users_list = []


            self.calculatePowerConsumed(actual_time)
            self.status = BsStatus.NoddingOff
            self.status_changer.set(actual_time, self.status_change_time_length)
            
        elif self.status == BsStatus.NoddingOff:

            self.calculatePowerConsumed(actual_time)
            self.status = BsStatus.Sleeping
            self.can_sleep = False

        elif self.status == BsStatus.Sleeping:

            self.calculatePowerConsumed(actual_time)
            self.status = BsStatus.WakingUp
            self.status_changer.set(actual_time, self.status_change_time_length)

        elif self.status == BsStatus.WakingUp:

            self.calculatePowerConsumed(actual_time)
            self.status = BsStatus.Active
        
        return True
        
    def calculatePowerConsumed(self,actual_time = 0):

        if self.status == BsStatus.Active:

            self.working_time += (actual_time - self.last_status_change_time)
            
        elif self.status == BsStatus.NoddingOff:
            
            self.power_consumed_by_changing_status += self.status_change_power_consumption * self.status_change_time_length/1000
            self.last_status_change_time = actual_time

        elif self.status == BsStatus.Sleeping:

            self.sleeping_time += (actual_time - self.last_status_change_time)
            
        elif self.status == BsStatus.WakingUp:

            self.power_consumed_by_changing_status += self.status_change_power_consumption * self.status_change_time_length/1000
            self.last_status_change_time = actual_time

        self.power_consumed = int(self.power_consumed_by_changing_status + (self.sleeping_time/1000 * self.sleeping_power_consumption) + (self.working_time/1000 * self.working_power_consumption))
        
        

class Sched_ReduceRB(Sched):
    
    def __init__(self, id:str, bs:BS) -> None:
        super().__init__()
        self.id = id
        self.bs = bs
        self.next_time = self.bs.getMin()

    def update(self):
        self.next_time = self.bs.getMin()
    
    def toRun(self,actual_time):
        self.bs.reduceRB(actual_time)
        self.update()



class Sched_ChangeIntensity(Sched):
    
    def __init__(self, lambd, intensity_index = 0) -> None:
        super().__init__()
        self.id = "ChangeIntensity"
        self.lambd = lambd
        self.intensity_index = intensity_index
        self.day_time = 86400000 # trwanie dnia w ms
        self.intensity_dict = dict(enumerate([1/2, 3/4, 1, 3/4]))
        self.time_dict = dict(enumerate([28800000, 50400000, 64800000, 86400000]))
        self.next_time = self.time_dict.get(self.intensity_index)
        self.actual_intensity = self.lambd*self.intensity_dict.get(self.intensity_index)
        
    
    def toRun(self,actual_time):

        self.day = actual_time // self.day_time # jaki moment dnia 
        self.intensity_index = (self.intensity_index+1)%4 # rejestr przesuwny
        self.actual_intensity = self.lambd*self.intensity_dict.get(self.intensity_index)
        self.next_time = (self.day * self.day_time) + self.time_dict.get(self.intensity_index)
    
    def get(self):

        return self.actual_intensity
    
    def getIntensityMultiplier(self):

        return self.intensity_dict.get(self.intensity_index)
    
    

class Sched_UserArrival(Sched):
    
    def __init__(self, id:str, bs:BS, sched_reduceRB: Sched_ReduceRB, sched_intensity: Sched_ChangeIntensity, gen_exp:Generator_ExponentialDistribution, gen_uni: Generator_UniformDistribution) -> None:
        super().__init__()
        self.id = id
        self.bs = bs
        self.gen_exp = gen_exp
        self.gen_uni = gen_uni
        self.sched_intensity = sched_intensity
        self.next_time = self.gen_exp.get(sched_intensity.get())
        self.sched_reduceRB = sched_reduceRB
    
    def toRun(self,actual_time):
        mi:int = self.gen_uni.get()
        self.bs.all_users += 1
        self.bs.connect(actual_time + mi, actual_time)
        self.next_time = actual_time + self.gen_exp.get(self.sched_intensity.get())
        self.sched_reduceRB.update() # 


class Simulation():
    
    def __init__(self, bs_1:BS, bs_2:BS, bs_3:BS, bs_4:BS, seed=1234) -> None:
        self.bs_1 = bs_1
        self.bs_2 = bs_2
        self.bs_3 = bs_3
        self.bs_4 = bs_4

        self.gen_uni = Generator_UniformDistribution(1000,30000,seed)
        self.gen_exp = Generator_ExponentialDistribution(seed)

        self.sched_change_intensity = Sched_ChangeIntensity(args.lambd)

        self.sched_reduce_rb_1 = Sched_ReduceRB("ReduceRB_1",self.bs_1)
        self.sched_user_arrival_1 = Sched_UserArrival("UserArrival_1",self.bs_1, self.sched_reduce_rb_1, self.sched_change_intensity, self.gen_exp, self.gen_uni)
        self.sched_reduce_rb_2 = Sched_ReduceRB("ReduceRB_2",self.bs_2)
        self.sched_user_arrival_2 = Sched_UserArrival("UserArrival_2",self.bs_2, self.sched_reduce_rb_2, self.sched_change_intensity, self.gen_exp, self.gen_uni)
        self.sched_reduce_rb_3 = Sched_ReduceRB("ReduceRB_3",self.bs_3)
        self.sched_user_arrival_3 = Sched_UserArrival("UserArrival_3",self.bs_3, self.sched_reduce_rb_3, self.sched_change_intensity, self.gen_exp, self.gen_uni)
        self.sched_reduce_rb_4 = Sched_ReduceRB("ReduceRB_4",self.bs_4)
        self.sched_user_arrival_4 = Sched_UserArrival("UserArrival_4",self.bs_4, self.sched_reduce_rb_4, self.sched_change_intensity, self.gen_exp, self.gen_uni)
        
        self.sched_change_bs_status_1 = Sched_ChangeBsStatus("Bs_1_Status",self.bs_1)
        self.sched_change_bs_status_2 = Sched_ChangeBsStatus("Bs_2_Status",self.bs_2)
        self.sched_change_bs_status_3 = Sched_ChangeBsStatus("Bs_3_Status",self.bs_3)
        self.sched_change_bs_status_4 = Sched_ChangeBsStatus("Bs_4_Status",self.bs_4)

        self.bs_1.addSchedToChangeStatus(self.sched_change_bs_status_1)
        self.bs_2.addSchedToChangeStatus(self.sched_change_bs_status_2)
        self.bs_3.addSchedToChangeStatus(self.sched_change_bs_status_3)
        self.bs_4.addSchedToChangeStatus(self.sched_change_bs_status_4)

    def run(self, days_to_simulate, logs = True):
        
        actual_time = 0
        day = 0
        day_time = 86400000
        next_day_end = day_time
        networks_users = 0
        new_networks_users = 0
        data_to_json = {}


        schedule = [self.sched_change_intensity,
                    self.sched_reduce_rb_1,
                    self.sched_user_arrival_1,
                    self.sched_reduce_rb_2,
                    self.sched_user_arrival_2,
                    self.sched_reduce_rb_3,
                    self.sched_user_arrival_3,
                    self.sched_reduce_rb_4,
                    self.sched_user_arrival_4,
                    self.sched_change_bs_status_1,
                    self.sched_change_bs_status_2,
                    self.sched_change_bs_status_3,
                    self.sched_change_bs_status_4
                    ]
        # self.showSchedule(schedule)
        schedule = self.sort(schedule)

        if logs == True: 
            self.showSchedule(schedule)

        actual_time = schedule[0].next_time


        while(day<days_to_simulate):
            
            if logs == True:
                print(f'Actual schedule element to run: {schedule[0].id}')
                print(f'Actual time: {actual_time} ms')
                print(f'Actual intensity: {self.sched_change_intensity.get()}')
                print(f'Actual intensity multiplier: {self.sched_change_intensity.getIntensityMultiplier()}')
                print(f'Time to next intensity change: {self.sched_change_intensity.next_time} ms')
                
                print("=========================================================")

            schedule[0].run(actual_time)

            self.sched_reduce_rb_1.update() # aktualizacja elementów do usuwania userów 
            self.sched_reduce_rb_2.update()
            self.sched_reduce_rb_3.update()
            self.sched_reduce_rb_4.update()


            schedule = self.sort(schedule)

            if logs == True:
                self.showSchedule(schedule)
                self.showBsResources()
            
            new_networks_users = bs_1.rb_taken + bs_2.rb_taken + bs_3.rb_taken + bs_4.rb_taken

            if new_networks_users != networks_users:
                networks_users = new_networks_users
                data_to_json.update({actual_time : networks_users})

            actual_time = schedule[0].next_time # przesunięcie czasu do następnego zdarzenia czasowego

            if actual_time >= next_day_end :
                next_day_end += day_time 
                day += 1
            
        bs_1.calculatePowerConsumed(actual_time) # podsumwanie zużytej mocy stacji bazowych
        bs_2.calculatePowerConsumed(actual_time)
        bs_3.calculatePowerConsumed(actual_time)
        bs_4.calculatePowerConsumed(actual_time)
        
        with open(output_path, "w") as file:
            json.dump(data_to_json, file, indent=1)
        
        return bs_1.disconnected_users + bs_2.disconnected_users + bs_3.disconnected_users + bs_4.disconnected_users
    

    def sort(self, lst:list):
        
        sorted = [] 
        zeros = [] 

        for i, el in enumerate(lst):
            if el.next_time == 0:
                zeros.append(el)
            elif i !=0:
                inserted = False
                for j, el2 in enumerate(sorted):
                    if el.next_time <= el2.next_time:
                        sorted.insert(j,el)
                        inserted = True
                        break
                if not inserted: 
                    sorted.append(el)
            else:
                sorted.append(el)

        sorted.extend(zeros)

        return sorted

    def showSchedule(self, schedule:list):
        
        print("\nSchedule: ")

        for i,el in enumerate(schedule):
            print(f'{i}. {el.id}: {el.next_time}')
        
        print("\n")

    def showBsResources(self):
        print(f'[{str(self.bs_1.status).split(".")[1]}]{self.bs_1.id} resources: {self.bs_1.rb_taken}/{self.bs_1.rb_max}')
        print(f'[{str(self.bs_2.status).split(".")[1]}]{self.bs_2.id} resources: {self.bs_2.rb_taken}/{self.bs_2.rb_max}')
        print(f'[{str(self.bs_3.status).split(".")[1]}]{self.bs_3.id} resources: {self.bs_3.rb_taken}/{self.bs_3.rb_max}')
        print(f'[{str(self.bs_4.status).split(".")[1]}]{self.bs_4.id} resources: {self.bs_4.rb_taken}/{self.bs_4.rb_max}')
        print("\n")




if __name__ == "__main__":


    bs_1 = BS("bs_1", args.resource_blocks, 0.2, 0.8)
    bs_2 = BS("bs_2", args.resource_blocks, 0.2, 0.8)
    bs_3 = BS("bs_3", args.resource_blocks, 0.2, 0.8)
    bs_4 = BS("bs_4", args.resource_blocks, 0.2, 0.8)

    bs_1.addNeighbour(bs_4, bs_2)
    bs_2.addNeighbour(bs_1, bs_3)
    bs_3.addNeighbour(bs_2, bs_4)
    bs_4.addNeighbour(bs_3, bs_1)

    simul = Simulation(bs_1, bs_2, bs_3, bs_4)

    
    if args.logs == True:
        print("------------------------------")
        print("Starting program....")
        print("------------------------------")
        print("LOGS:", args.logs)
        print("------------------------------")
        print("\n")
        print("------------Data-------------")
        print("Seed:",args.seed)
        print("Lambd:",args.lambd)
        print("Resource Blocks:",args.resource_blocks)
        print("------------------------------")

    start = time.time() 
    disc_users = simul.run(1, logs=args.logs)
    end = time.time()
    if args.logs == True:
        print(f'Simulation time: {round(end-start,2)} s')
        print('\n')
        print(f'Disconnected users:')
        print(f'bs_1 {bs_1.disconnected_users}')
        print(f'bs_2 {bs_2.disconnected_users}')
        print(f'bs_3 {bs_3.disconnected_users}')
        print(f'bs_4 {bs_4.disconnected_users}')
        
        print("------------------------------")

        print("Sleeping time:")
        print(f'bs_1: {bs_1.sleeping_time}')
        print(f'bs_2: {bs_2.sleeping_time}')
        print(f'bs_3: {bs_3.sleeping_time}')
        print(f'bs_4: {bs_4.sleeping_time}')

        print("------------------------------")

        print(f'Disconnected users:')
        print(f'bs_1 {bs_1.disconnected_users}')
        print(f'bs_2 {bs_2.disconnected_users}')
        print(f'bs_3 {bs_3.disconnected_users}')
        print(f'bs_4 {bs_4.disconnected_users}')

        print(f'Sum ==: {disc_users}')
        print("------------------------------")

        print(f'Power Consumed:')
        print(f'bs_1 {bs_1.power_consumed/1_000_000} MJ')
        print(f'bs_2 {bs_2.power_consumed/1_000_000} MJ')
        print(f'bs_3 {bs_3.power_consumed/1_000_000} MJ')
        print(f'bs_4 {bs_4.power_consumed/1_000_000} MJ')

        print("------------------------------")

        print(f'All Users: {bs_1.all_users + bs_2.all_users + bs_3.all_users + bs_4.all_users}')

        print("------------------------------")