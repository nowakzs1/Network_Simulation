import json
import math
import os
import time
from enum import Enum


class Config():
    seed = 1123124
    lambd = 14.2
    resource_blocks = 273
    days_to_simulate = 1
    low = 40
    output_dir = f'Output_Simulation_method_1/lambda_{lambd}/users_count_lambda_{lambd}_seed_{seed}.json'

class Generator():
    def __init__(self, seed:int, m: float = 2147483647.0, a: float = 16807.0, q: float = 127773.0, r: float = 2836.0 ):
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

    def __init__(self, min:int, max:int, seed:int, m: float = 2147483647, a: float = 16807, q: float = 127773, r: float = 2836):
        super().__init__(seed, m, a, q, r)
        self.min = min
        self.max = max
    
    def get(self):
        ret = super().rand() * (self.max - self.min) + self.min
        return int(ret)
        
class Generator_ExponentialDistribution(Generator):

    def __init__(self, seed:int, m: float = 2147483647, a: float = 16807, q: float = 127773, r: float = 2836):
        super().__init__(seed, m, a, q, r)
    
    def get(self, lambd: float):
        k:float = super().rand()
        return int(-1000/lambd*math.log(k))

class BsStatus(Enum):
    Active = 0
    FallingAsleep = 1
    Sleeping = 2
    WakingUp = 3

class Bs():
    def __init__(self, id:str, max_rb:int, high:float = 0.8):
        self.id = id
        self.max_rb = max_rb
        self.rb_list = []
        self.disconnected_users = 0
        self.passed_to_neighbour_1 = False

        #Tresholds
        self.H = int(self.max_rb * high)
        self.overloading = False

        self.L = int(self.max_rb * Config.low)
        self.can_sleep = False

       #Status variables
        self.status = BsStatus.Active
        self.next_time_status_change = 0
        self.status_change_time_length = 50 # ms
        self.take_from_neighbour = None
        self.last_time_status_change = 0

        #Power consumption        
        self.power_consumption_by_status_change = 1000 #W
        self.power_consumption_while_sleeping = 1 #W
        self.power_consumption_while_working = 200 #W

        self.power_consumed = 0
        self.sleeping_time = 0
        self.working_time = 0
        self.power_consumed_status_change = 0
    

    def addNeighbour(self, neighbour_1, neighbour_2):
        self.neighbour_1 = neighbour_1
        self.neighbour_2 = neighbour_2


    def connect(self, mi):
        if self.status == BsStatus.Active and len(self.rb_list) < self.max_rb:
            
            self.rb_list.append(mi)

            if len(self.rb_list) > self.H:
                self.overloading = True

            elif len(self.rb_list) >= self.L and self.can_sleep == False:
                self.can_sleep = True

            return True
        
        else:
            return False
    
    def getNextDisconnection(self):
        if self.rb_list:
            return min(self.rb_list)
        return 0
    

    def disconnect(self,time):
        self.rb_list.remove(time)
        if self.can_sleep == True and len(self.rb_list) < self.L:
            self.changeStatus(time)
            return True
        elif len(self.rb_list) < self.H and self.overloading == True:
            self.overloading = False

        return False
    
    def changeStatus(self,time_now = 0):
        
        if self.status == BsStatus.Active:
            
            for user_mi in self.rb_list:
                connected_status = self.handOver(user_mi)
                if connected_status == False: 
                    self.disconnected_users+=1
                
            self.rb_list = []
            self.next_time_status_change = time_now + self.status_change_time_length
            self.calculatePowerConsumed(time_now)
            self.status = BsStatus.FallingAsleep
            
        elif self.status == BsStatus.FallingAsleep:
            self.calculatePowerConsumed(time_now)
            self.status = BsStatus.Sleeping
        
        elif self.status == BsStatus.Sleeping:
            self.next_time_status_change = time_now + self.status_change_time_length
            self.calculatePowerConsumed(time_now)
            self.status = BsStatus.WakingUp
        
        elif self.status == BsStatus.WakingUp:
            self.rb_list = self.take_from_neighbour.handOverHalf()
            self.calculatePowerConsumed(time_now)
            self.status = BsStatus.Active
        
        return 1
    
    def calculatePowerConsumed(self, time_now):
        if self.status == BsStatus.Active:
            self.working_time += time_now - self.last_time_status_change
              
        elif self.status == BsStatus.FallingAsleep:
            self.power_consumed_status_change += self.power_consumption_by_status_change * self.status_change_time_length/1000
            self.last_time_status_change = time_now 
        
        elif self.status == BsStatus.Sleeping:
            self.sleeping_time += time_now - self.last_time_status_change
        
        elif self.status == BsStatus.WakingUp:
            self.power_consumed_status_change += self.power_consumption_by_status_change * self.status_change_time_length/1000
            self.last_time_status_change = time_now

        self.power_consumed = int( self.power_consumed_status_change + self.power_consumption_while_working * self.working_time/1000 + self.power_consumption_while_sleeping* self.sleeping_time/1000)
    
    def handOver(self, mi):
        if self.passed_to_neighbour_1 == False:
            self.passed_to_neighbour_1 = True
            connected_status = self.neighbour_1.connect(mi)

            if connected_status == False:
                connected_status = self.neighbour_2.connect(mi)
        else:
            self.passed_to_neighbour_1 = False
            connected_status = self.neighbour_2.connect(mi)

            if connected_status == False:
                connected_status = self.neighbour_1.connect(mi)
        
        return connected_status
    
    def handOverHalf(self):
        
        for_neighbour = []

        for i in range(0,len(self.rb_list)//2):
            for_neighbour.append(self.rb_list.pop())
        
        return for_neighbour


    def wakeUpNeigbour(self, time_now):

        if self.neighbour_1.status == BsStatus.WakingUp or self.neighbour_2.status == BsStatus.WakingUp:
            return False
        elif self.neighbour_1.status == BsStatus.Sleeping:
            self.neighbour_1.changeStatus(time_now)
            self.neighbour_1.take_from_neighbour = self
            return True
        elif self.neighbour_2.status == BsStatus.Sleeping:
            self.neighbour_2.changeStatus(time_now)
            self.neighbour_2.take_from_neighbour = self
            return True


class Simulation():
    def __init__(self, bs_1:Bs, bs_2:Bs, bs_3:Bs, seed):
        self.bs_1 = bs_1
        self.bs_2 = bs_2
        self.bs_3 = bs_3
        
        self.intensity_index = 0
        self.intensity_time = dict(enumerate([28800000, 50400000, 64800000, 86400000]))
        self.intensity_multiplier = dict(enumerate([1/2, 3/4, 1, 3/4]))

        self.day_ms = 86400000

        self.uniform_generator = Generator_UniformDistribution(1000,30000,seed)
        self.exponential_generator = Generator_ExponentialDistribution(seed)


    def run(self, days_to_simulate, lambd):

        time_now = 0
        day_now = 0
        next_day_time = self.day_ms

        
        intensity, next_intensity_change_time = self.getNextIntensity(lambd, day_now)

        user_arrival_1 = time_now + self.exponential_generator.get(intensity)
        user_arrival_2 = time_now + self.exponential_generator.get(intensity)
        user_arrival_3 = time_now + self.exponential_generator.get(intensity)

        user_disconnection_1 = bs_1.getNextDisconnection() 
        user_disconnection_2 = bs_2.getNextDisconnection()
        user_disconnection_3 = bs_3.getNextDisconnection()

        sleeping_bs = 0
        users_in_network = 0
        new_users_in_network = 0
        total_users_connected =0
        total_users = 0
        json_data = {}

        
        while(time_now < self.day_ms*days_to_simulate):
            
            if(time_now == next_intensity_change_time):
                intensity, next_intensity_change_time = self.getNextIntensity(lambd, day_now)
                
            
            if(time_now == user_arrival_1):
                mi = time_now + self.uniform_generator.get()
                connected_status = bs_1.connect(mi)
                total_users+=1

                if(connected_status == False):
                    connected_status = bs_1.handOver(mi)

                    if(connected_status == False):
                        bs_1.disconnected_users +=1

                if(connected_status == True):
                    total_users_connected+=1
                

                user_arrival_1 = time_now + self.exponential_generator.get(intensity)

            if(time_now == user_arrival_2):
                mi = time_now + self.uniform_generator.get()
                connected_status = bs_2.connect(mi)
                total_users+=1
                
                if(connected_status == False):
                    connected_status = bs_2.handOver(mi)

                    if(connected_status == False):
                        bs_2.disconnected_users +=1

                if(connected_status == True):
                    total_users_connected+=1
               

                user_arrival_2 = time_now + self.exponential_generator.get(intensity)

            if(time_now == user_arrival_3):
                mi = time_now + self.uniform_generator.get()
                connected_status = bs_3.connect(mi)
                total_users+=1

                if(connected_status == False):
                    connected_status = bs_3.handOver(mi)

                    if(connected_status == False):
                        bs_3.disconnected_users +=1

                if(connected_status == True):
                    total_users_connected+=1

                user_arrival_3 = time_now + self.exponential_generator.get(intensity)

            if(bs_1.overloading == True and sleeping_bs > 0):
                wake_up_status = bs_1.wakeUpNeigbour(time_now)
                if wake_up_status == True:
                    sleeping_bs -= 1

            if(bs_2.overloading == True and sleeping_bs > 0):
                wake_up_status = bs_2.wakeUpNeigbour(time_now)
                if wake_up_status == True:
                    sleeping_bs -= 1

            if(bs_3.overloading == True and sleeping_bs > 0):
                wake_up_status = bs_3.wakeUpNeigbour(time_now)
                if wake_up_status == True:
                    sleeping_bs -= 1

            if(time_now == user_disconnection_1 and user_disconnection_1 != 0):
                sleeping_status = bs_1.disconnect(time_now)
                
                if sleeping_status == True: 
                    sleeping_bs += 1

            if(time_now == user_disconnection_2 and user_disconnection_2 != 0):
                sleeping_status = bs_2.disconnect(time_now)
                
                if sleeping_status == True: 
                    sleeping_bs += 1

            if(time_now == user_disconnection_3 and user_disconnection_3 != 0):
                sleeping_status = bs_3.disconnect(time_now)
                
                if sleeping_status == True: 
                    sleeping_bs += 1
            
            
            if(time_now == bs_1.next_time_status_change and bs_1.next_time_status_change != 0):
                bs_1.changeStatus(time_now)
                bs_1.next_time_status_change = 0
            
            if(time_now == bs_2.next_time_status_change and bs_2.next_time_status_change != 0):
                bs_2.changeStatus(time_now)
                bs_2.next_time_status_change = 0

            if(time_now == bs_3.next_time_status_change and bs_3.next_time_status_change != 0):
                bs_3.changeStatus(time_now)
                bs_3.next_time_status_change = 0



            user_disconnection_1 = bs_1.getNextDisconnection() 
            user_disconnection_2 = bs_2.getNextDisconnection()
            user_disconnection_3 = bs_3.getNextDisconnection()
            
            new_users_in_network = len(bs_1.rb_list) + len(bs_2.rb_list) + len(bs_3.rb_list)
            
            if users_in_network != new_users_in_network:
                users_in_network = new_users_in_network
                json_data.update({time_now: users_in_network})
            

            time_now = self.getMinTime(
                [
                    next_intensity_change_time,
                    user_arrival_1,
                    user_arrival_2,
                    user_arrival_3,
                    user_disconnection_1,
                    user_disconnection_2,
                    user_disconnection_3,
                    bs_1.next_time_status_change,
                    bs_2.next_time_status_change,
                    bs_3.next_time_status_change

                ]
            )

            if time_now == next_day_time:
                day_now +=1
                next_day_time += self.day_ms

        bs_1.calculatePowerConsumed(time_now)
        bs_2.calculatePowerConsumed(time_now)
        bs_3.calculatePowerConsumed(time_now)
        
        with open(Config.output_dir, "w") as outputfile:
            json.dump(json_data,outputfile, indent=1)

        disconnected_users = bs_1.disconnected_users + bs_2.disconnected_users + bs_3.disconnected_users
        return disconnected_users, total_users_connected, total_users
        
    
    def getMinTime(self, lst:list):

        min = lst[0]

        for i in lst:
            if i != 0 and i < min:
                min = i
        
        return min

 

    def getNextIntensity(self,lambd, day_now):
        multiplier = self.intensity_multiplier.get(self.intensity_index)
        next_change_time = (day_now*self.day_ms) + self.intensity_time.get(self.intensity_index)
        self.intensity_index = (self.intensity_index+1)%4

        return multiplier*lambd, next_change_time



if __name__ == "__main__":

    bs_1 = Bs("bs_1", Config.resource_blocks)
    bs_2 = Bs("bs_2", Config.resource_blocks)
    bs_3 = Bs("bs_3", Config.resource_blocks)

    bs_1.addNeighbour(bs_3, bs_2)
    bs_2.addNeighbour(bs_1, bs_3)
    bs_3.addNeighbour(bs_2, bs_1)

    simulation = Simulation(bs_1, bs_2, bs_3, Config.seed)

    start = time.time()
    disconnected_users, total_users_connected, total_users = simulation.run(Config.days_to_simulate, Config.lambd)
    end = time.time()
            
    print(f'Czas trwania symulacji: {round(end-start,2)} s\n')
    print(f'Czas nieaktywności stacji bs_1: {int(bs_1.sleeping_time/1000)}s\n')
    print(f'Czas nieaktywności stacji bs_2: {int(bs_2.sleeping_time/1000)}s\n')
    print(f'Czas nieaktywności stacji bs_3: {int(bs_3.sleeping_time/1000)}s\n')
    print(f'Czas pracy stacji bs_1: {int(bs_1.working_time/1000)}s\n')
    print(f'Czas pracy stacji bs_2: {int(bs_2.working_time/1000)}s\n')
    print(f'Czas pracy stacji bs_3: {int(bs_3.working_time/1000)}s\n')
    print(f'=================================================\n')
    print(f'Łączna zużyta moc przez stację bs_1: {round(bs_1.power_consumed/1000000,2)} MJ\n')
    print(f'Łączna zużyta moc przez stację bs_2: {round(bs_2.power_consumed/1000000,2)} MJ\n')
    print(f'Łączna zużyta moc przez stację bs_3: {round(bs_3.power_consumed/1000000,2)} MJ\n')
    print(f'=================================================\n')
    print(f'Całkowita liczba użytkowników w systemie: {total_users}\n')
    print(f'Łączna liczba połączonych użytkowników w systemie: {total_users_connected}\n')
    print(f'Liczba rozłączonych użytkowników: {disconnected_users}\n')
    print(f'Procentowa ilość traconcyh użytkowników: {round(disconnected_users/total_users*100,2)}%\n')
    print(f'=================================================\n')
       