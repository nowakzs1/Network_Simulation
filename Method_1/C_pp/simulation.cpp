#include <algorithm>
#include <cstdio>
#include <chrono>
#include <list>
#include <math.h>
#include <iostream>


using namespace std;

class Config{
    public:
        int Max_resource_blocks = 65;
        int Min_mi = 1000;
        int Max_mi = 30000;
        int Seed = 5;
        float Users_per_second = 3.15; 
        float L = 0.47;
        // float L = 0.1;
        bool Logs = true;
};

class Generator{
    
    public:
    float M;
    float A;
    float Q;
    float R;
    int Seed;

    Generator(int seed,float m = 2147483647.0, float a = 16807.0, float q = 127773.0, float r = 2836.0 ){
        this->M = m;
        this->A = a;
        this->Q = q;
        this->R = r;
        this->Seed = seed;
    }

    float rand(){
        float h = floor(this->Seed/this->Q);
        this->Seed = this->A * (this->Seed - this->Q * h) - this->R * h;
        if(this->Seed < 0){
            this->Seed += this->M;
        }

        return this->Seed/this->M;
    }


};

class UniformDistribution: private Generator{

    public:
    int Min;
    int Max;
    
    UniformDistribution(int min, int max, int seed): Generator{seed}{
        this->Min = min;
        this->Max = max;
    }

    float get(){
        return Generator::rand() * (this->Max - this->Min) + this->Min;
    }

};

class ExponentialDistribution: public Generator{

    public:
    ExponentialDistribution(int seed): Generator{seed}{};

    float get(float lamb){
        float k = Generator::rand();
        return -(1000/lamb)*log(k);
    }
};

class BaseStation{

    public:

    bool CanGoToSleep;
    bool IsAsleep;
    bool IsFull;
    bool Overloading;
    bool PassedToNeighbour_1;
    bool PassedToNeighbour_2;
    bool Blocked;
    
    int ID;
    int RB_max;
    int H_threshold;
    int L_threshold;
    int NoddingOff;
    int WakingUp;
    int BadNeighbour;
    int BlockingTime;
    int DisconnectedUsers;
    float PowerConsumed;
    int RunningTime;
    int SleepingTime;
    float RunningPowerValue;
    float SleepingPowerValue;

    float Lambda;
    float UserPerSecond;

    list<int> ResourceBlocks;

    ExponentialDistribution* Gen_exponential;
    BaseStation* Neighbour_1;
    BaseStation* Neighbour_2;

    BaseStation(
                int id, 
                float user_per_second, 
                int rb_max, 
                ExponentialDistribution* gen_exp,
                float l = 0.2,
                float h = 0.8
                ){
        this->ID = id;
        this->Gen_exponential = gen_exp;
        this->UserPerSecond = user_per_second;
        this->RB_max = rb_max;
        this->CanGoToSleep=false;
        this->IsAsleep = false;
        this->IsFull = false;
        this->H_threshold = rb_max * h;
        this->L_threshold = rb_max * l;
        this->Overloading = false;
        this->NoddingOff = 0;
        this->Blocked = false;
        this->WakingUp = 0;
        this->BadNeighbour = 0;
        this->PassedToNeighbour_1 = false;
        this->PassedToNeighbour_2 = false;
        this->BlockingTime = 50;
        this->DisconnectedUsers = 0;
        this->PowerConsumed = 0;
        this->RunningTime = 0;
        this->SleepingTime = 0;
        this->RunningPowerValue = 200;
        this->SleepingPowerValue = 1;
    }

    void addNeighbours(BaseStation* neighbour_1, BaseStation* neighbour_2){
        this->Neighbour_1 = neighbour_1;
        this->Neighbour_2 = neighbour_2;
    }

    void setLambda(float lmb){
        this->Lambda = lmb * this->UserPerSecond;
    }

    int generateUser(){
        int next_user_arrival = (int)Gen_exponential->get(this->Lambda);
        return next_user_arrival;
    }

    bool connect(int user_disconnect_time){
        if(this->IsFull == false && this->IsAsleep == false && this->Blocked == false){
            this->ResourceBlocks.push_back(user_disconnect_time);
            if(this->ResourceBlocks.size() == this->RB_max){
                this->IsFull = true;

            }else if(this->ResourceBlocks.size() >= this->H_threshold){
                this->Overloading = true;

            }else if(this->ResourceBlocks.size() > this->L_threshold){
                this->CanGoToSleep = true;
            }
            return true;
        }

        return false;
    }

    bool handOver(int user_disconnect_time){
        bool connected;

        if(this->PassedToNeighbour_1 == false){
            connected = this->Neighbour_1->connect(user_disconnect_time);
            if(connected == true){
                this->PassedToNeighbour_1 = true;
                this->PassedToNeighbour_2 = false;
                return true;
            }else{
                connected = this->Neighbour_2->connect(user_disconnect_time);
                return connected;
            }
        }

        if(this->PassedToNeighbour_2 == false){
            connected = this->Neighbour_2->connect(user_disconnect_time);
            if(connected == true){
                this->PassedToNeighbour_1 = false;
                this->PassedToNeighbour_2 = true;
                return true;
            }else{
                connected = this->Neighbour_1->connect(user_disconnect_time);
                return connected;
            }
        }

        return false;
    }

    bool disconnect(int actual_time){

        this->ResourceBlocks.remove(actual_time);
        
        if(this->Overloading == true && this->ResourceBlocks.size() < this->H_threshold){
            this->Overloading = false;
        }else if(this->ResourceBlocks.size() < this->RB_max){
            this->IsFull = false;
        }
        
        if(this->CanGoToSleep == true && this->ResourceBlocks.size() <= this->L_threshold){
            return true;
        }

        return false;
    }

    bool sleepWell(int time_ms){
        list<int>::iterator it;
        int rb_size = this->ResourceBlocks.size();
        int i = 0;
        bool connected;
        for (it = this->ResourceBlocks.begin(); it != this->ResourceBlocks.end(); ++it){
            
            if(i < (rb_size/2)){
                connected = this->Neighbour_1->connect(*it);
                if(connected == false){
                    connected = this->Neighbour_2->connect(*it);
                    if(connected == false){
                        this->DisconnectedUsers += 1;
                    }
                }
            }else{
                connected = this->Neighbour_2->connect(*it);
                if(connected == false){
                    connected = this->Neighbour_1->connect(*it);
                    if(connected == false){
                        this->DisconnectedUsers += 1;
                    }
                }
            }
        
            ++i;
        
        }
        this->ResourceBlocks = {};
        this->NoddingOff = time_ms + this->BlockingTime;
        this->Blocked = true;
        return true;
    }


    bool wakeUpNeighbour(int time_ms){

        if(this->Neighbour_1->IsAsleep == true && this->Neighbour_1->Blocked == false){
            this->Neighbour_1->WakingUp = time_ms + this->BlockingTime;
            this->Neighbour_1->Blocked = true;
            this->Neighbour_1->BadNeighbour = this->ID;
            return true;
        }

        if(this->Neighbour_2->IsAsleep == true && this->Neighbour_2->Blocked == false){
            this->Neighbour_2->WakingUp = time_ms + this->BlockingTime;
            this->Neighbour_2->Blocked = true;
            this->Neighbour_2->BadNeighbour = this->ID;
            return true;
        }

        return false;
    }

    void relieveNeighbor(){
        
        if(this->BadNeighbour == Neighbour_1->ID){
            this->takeHalfOfUsers(Neighbour_1);
        }else{
            this->takeHalfOfUsers(Neighbour_2);
        }
    }

    void takeHalfOfUsers(BaseStation* Neighbour){
        
        list<int>::iterator it;
        int rb_size = Neighbour->ResourceBlocks.size();
        for(int i = 0; i < rb_size/2; i++){
            it = Neighbour->ResourceBlocks.begin();
            this->connect((*it));
            Neighbour->ResourceBlocks.pop_front();
        }
        Neighbour->Overloading = false;

    }

    int getNextDisconnectTime(){

        if(!this->ResourceBlocks.empty()){
            list<int>::iterator it = this->ResourceBlocks.begin();
            int min = *it; 
            for(it = this->ResourceBlocks.begin(); it != this->ResourceBlocks.end(); ++it){
                if(*it < min){
                    min = *it;
                }
            }

            return min;
        }

        return 0;
    }

    void calculatePowerConsumed(int time_ms){
        if(this->IsAsleep == true){
            this->SleepingTime += time_ms;
        }else if (this->IsAsleep == false){
            this->RunningTime += time_ms;
        }

        this->PowerConsumed = this->SleepingTime*(this->SleepingPowerValue/1000) + this->RunningTime*(this->RunningPowerValue/1000);
        
    }


};

class Network{
    public:

    int Day_ms;
    int Users_number;

    float Lambda;

    bool Logs;

    BaseStation* bs_1;
    BaseStation* bs_2;
    BaseStation* bs_3;

    UniformDistribution* gen_uniform;

    Network(BaseStation* bs1, BaseStation* bs2, BaseStation* bs3, UniformDistribution* gen_uni, bool logs ){
        this->bs_1 = bs1;
        this->bs_2 = bs2;
        this->bs_3 = bs3;
        this->gen_uniform = gen_uni; 
        this->Day_ms = 86400000;
        this->Lambda = 0.5;
        this->Logs = logs;
        this->Users_number = 0;
    }

    int run(int days = 1){
        int time_ms = 0;
        int old_time = 0;
        int day = -1;
        int simulation_time = days * Day_ms;
        int user_disconnect_time;
        list<int> next_time;


        int next_lambda_change = 0;
        bs_1->setLambda(this->Lambda);
        bs_2->setLambda(this->Lambda);
        bs_3->setLambda(this->Lambda);
        int next_user_arrival_1 = bs_1->generateUser();
        int next_user_arrival_2 = bs_2->generateUser();
        int next_user_arrival_3 = bs_3->generateUser();

        int next_disconnect_time_1 = 0;
        int next_disconnect_time_2 = 0;
        int next_disconnect_time_3 = 0;

        int sleeping_bs = 0;
        int wakingup_bs = 0;
        bool went_sleep = false;
        bool awoken = false;
        bool time_to_sleep_1 = false;
        bool time_to_sleep_2 = false;
        bool time_to_sleep_3 = false;
        
        bool user_connected;

        int disconnected_users = 0;

        bs_1->calculatePowerConsumed(time_ms);
        bs_2->calculatePowerConsumed(time_ms);
        bs_3->calculatePowerConsumed(time_ms);


        while(time_ms < simulation_time){

            if(time_ms == next_lambda_change){
                int day_time = time_ms % Day_ms;
                if(day_time == 0){
                    day+=1;
                }
                next_lambda_change = (Day_ms*day) + getNextLambdaChange(day_time);
                bs_1->setLambda(this->Lambda);
                bs_2->setLambda(this->Lambda);
                bs_3->setLambda(this->Lambda);
                
            }

            if(time_ms == bs_1->WakingUp && bs_1->WakingUp > 0){
                //WakeUp
                bs_1->IsAsleep = false;
                bs_1->CanGoToSleep = false;
                bs_1->Blocked = false;
                bs_1->WakingUp = 0;
                wakingup_bs -= 1;
                //take half of users from BadNeigbour
                bs_1->relieveNeighbor();
            }

            if(time_ms == bs_2->WakingUp && bs_2->WakingUp > 0){
                //WakeUp
                bs_2->IsAsleep = false;
                bs_2->CanGoToSleep = false;
                bs_2->Blocked = false;
                bs_2->WakingUp = 0;
                wakingup_bs -= 1;
                //take half of users from BadNeigbour
                bs_2->relieveNeighbor();
            }

            if(time_ms == bs_3->WakingUp && bs_3->WakingUp > 0){
                //WakeUp
                bs_3->IsAsleep = false;
                bs_3->CanGoToSleep = false;
                bs_3->Blocked = false;
                bs_3->WakingUp = 0;
                wakingup_bs -= 1;
                //take half of users from BadNeigbour
                bs_3->relieveNeighbor();
            }

            if(time_ms == bs_1->NoddingOff && bs_1->NoddingOff > 0){
                bs_1->IsAsleep = true;
                bs_1->CanGoToSleep = false;
                bs_1->Blocked = false;
                bs_1->NoddingOff = 0;
            }

            if(time_ms == bs_2->NoddingOff && bs_2->NoddingOff > 0){
                bs_2->IsAsleep = true;
                bs_2->CanGoToSleep = false;
                bs_2->Blocked = false;
                bs_2->NoddingOff = 0;
            }
        
            if(time_ms == bs_3->NoddingOff && bs_3->NoddingOff > 0){
                bs_3->IsAsleep = true;
                bs_3->CanGoToSleep = false;
                bs_3->Blocked = false;
                bs_3->NoddingOff = 0;
            }

            if(time_ms == next_disconnect_time_1 && next_disconnect_time_1 > 0){
                time_to_sleep_1 = bs_1->disconnect(time_ms);
            }

            if(time_ms == next_disconnect_time_2 && next_disconnect_time_2 > 0){
                time_to_sleep_2 = bs_2->disconnect(time_ms);
            }

            if(time_ms == next_disconnect_time_3 && next_disconnect_time_3 > 0){
                time_to_sleep_3 = bs_3->disconnect(time_ms);
            }

            if(sleeping_bs==2){
                time_to_sleep_1 = false;
                time_to_sleep_2 = false;
                time_to_sleep_3 = false;
            }

            if(time_to_sleep_1 == true){
                went_sleep = bs_1->sleepWell(time_ms);

                if(went_sleep == true ){
                    sleeping_bs += 1;
                }
                time_to_sleep_1 = false;
            }

            if(time_to_sleep_2 == true){
                went_sleep = bs_2->sleepWell(time_ms);

                if(went_sleep == true ){
                    sleeping_bs += 1;
                }
                time_to_sleep_2 = false;
            }

            if(time_to_sleep_3 == true){
                went_sleep = bs_3->sleepWell(time_ms);

                if(went_sleep == true ){
                    sleeping_bs += 1;
                }
                time_to_sleep_3 = false;
            }

            if(time_ms == next_user_arrival_1){
                this->Users_number +=1;
                user_disconnect_time = time_ms + (int)gen_uniform->get();
                user_connected = bs_1->connect( user_disconnect_time);

                if(user_connected == false){
                    user_connected = bs_1->handOver(user_disconnect_time);
                    if(user_connected == false){
                        bs_1->DisconnectedUsers +=1;
                    }
                }

                next_user_arrival_1 = time_ms + bs_1->generateUser();

            }

            if(time_ms == next_user_arrival_2){
                this->Users_number +=1;
                user_disconnect_time = time_ms + (int)gen_uniform->get();
                user_connected = bs_2->connect(user_disconnect_time);

                if(user_connected == false){
                    user_connected = bs_2->handOver(user_disconnect_time);
                    if(user_connected == false){
                        bs_2->DisconnectedUsers +=1;
                    }
                }

                next_user_arrival_2 = time_ms + bs_2->generateUser();
            }
            
            if(time_ms == next_user_arrival_3){
                this->Users_number +=1;
                user_disconnect_time = time_ms + (int)gen_uniform->get();
                user_connected = bs_3->connect(user_disconnect_time);

                if(user_connected == false){
                    user_connected = bs_3->handOver(user_disconnect_time);
                    if(user_connected == false){
                        bs_3->DisconnectedUsers +=1;
                    }
                }

                next_user_arrival_3 = time_ms + bs_3->generateUser();
            }


            // WakeUp using overloading 
            if(sleeping_bs > 0 && wakingup_bs == 0){
                if(bs_1->Overloading == true){
                    awoken = bs_1->wakeUpNeighbour(time_ms);
                    if(awoken == true){
                        sleeping_bs -= 1;
                        wakingup_bs += 1;
                    }
                }else if(bs_2->Overloading == true){
                    awoken = bs_2->wakeUpNeighbour(time_ms);
                    if(awoken == true){
                        sleeping_bs -= 1;
                        wakingup_bs += 1;
                    }
                }else if(bs_3->Overloading == true){
                    awoken = bs_3->wakeUpNeighbour(time_ms);
                    if(awoken == true){
                        sleeping_bs -= 1;
                        wakingup_bs += 1;
                    }
                }
            }
                
            next_disconnect_time_1  = bs_1->getNextDisconnectTime();
            next_disconnect_time_2  = bs_2->getNextDisconnectTime();
            next_disconnect_time_3  = bs_3->getNextDisconnectTime();

            next_time = {
                        next_lambda_change, 
                        next_user_arrival_1, 
                        next_user_arrival_2, 
                        next_user_arrival_3, 
                        next_disconnect_time_1, 
                        next_disconnect_time_2, 
                        next_disconnect_time_3, 
                        bs_1->NoddingOff, 
                        bs_2->NoddingOff, 
                        bs_3->NoddingOff,
                        bs_1->WakingUp, 
                        bs_2->WakingUp, 
                        bs_3->WakingUp
                        };

            if(this->Logs == true){
                printf("==============================");
                printf("\nActual Time: %d \n", time_ms);
                printf("\nBasestation 1 [%d/%d]:",bs_1->ResourceBlocks.size(), bs_1->RB_max);
                this->draw(bs_1->ResourceBlocks.size());
                printf("\nPowerConsumed: %4.2f\n", bs_1->PowerConsumed);

                printf("\nBasestation 2 [%d/%d]:",bs_2->ResourceBlocks.size(), bs_2->RB_max);
                this->draw(bs_2->ResourceBlocks.size());
                printf("\nPowerConsumed: %4.2f\n", bs_2->PowerConsumed);

                printf("\nBasestation 3 [%d/%d]:",bs_3->ResourceBlocks.size(), bs_3->RB_max);
                this->draw(bs_3->ResourceBlocks.size());
                printf("\nPowerConsumed: %4.2f\n", bs_3->PowerConsumed);

                printf("\n=============================\n\n");
            }

            
            old_time = time_ms;
            time_ms = getNextTime(next_time);
            bs_1->calculatePowerConsumed(time_ms-old_time);
            bs_2->calculatePowerConsumed(time_ms-old_time);
            bs_3->calculatePowerConsumed(time_ms-old_time);
        }

        disconnected_users = bs_1->DisconnectedUsers + bs_2->DisconnectedUsers + bs_3->DisconnectedUsers;

        return disconnected_users;

    }

    int getNextTime(list<int> &lst){

        list<int>::iterator it = lst.begin();
        int min = *it;
        for(it = lst.begin(); it != lst.end(); ++it) {
            if(*it != 0 && *it < min){
                min = *it;
            }
        }

        return min;
    }

    int getNextLambdaChange(int time_ms){
        // lambda
            // 8h - 1/2 lb - 0-8
            // 6h - 3/4 lb - 8-14
            // 4h -  1  lb - 14-18
            // 6h - 3/4 lb - 18-24

        float h_8 = this->Day_ms/3;
        float h_8_6 = h_8+ this->Day_ms/4; // 6h = 21 600 000
        float h_8_6_4 = h_8_6+ this->Day_ms/6;

        if(time_ms < h_8){
            this->Lambda = 0.5;
            return h_8;
        }else if(h_8 <= time_ms && time_ms < h_8_6){
            this->Lambda = 0.75;
            return h_8_6;
        }else if(h_8_6 <= time_ms && time_ms < h_8_6_4){
            this->Lambda = 1.0;
            return h_8_6_4;
        }else if(h_8_6_4 <= time_ms && time_ms < Day_ms){
            this->Lambda = 0.75;
            return Day_ms;
        }else{
            abort;
        }
        
        return 0;
    }

    void draw(int resource_blocks_number){
        if(resource_blocks_number > 0){
            printf("|");
            for(int i = 0; i < resource_blocks_number; i++){
                printf("x|");
            }
        }
            
    }
        
};

int main(){

    for(int i = 5; i<=150; i+=15){
        Config config;
        config.Seed = i;
        
        UniformDistribution uniform_generator(config.Min_mi, config.Max_mi, config.Seed);
        ExponentialDistribution exponential_generator_1(config.Seed);
        ExponentialDistribution exponential_generator_2(config.Seed+22);
        ExponentialDistribution exponential_generator_3(config.Seed+333);

        BaseStation bs_1(1 , config.Users_per_second, config.Max_resource_blocks, &exponential_generator_1, config.L);
        BaseStation bs_2(2 , config.Users_per_second, config.Max_resource_blocks, &exponential_generator_2, config.L);
        BaseStation bs_3(3 , config.Users_per_second, config.Max_resource_blocks, &exponential_generator_3, config.L);

        bs_1.addNeighbours(&bs_2, &bs_3);
        bs_2.addNeighbours(&bs_3, &bs_1);
        bs_3.addNeighbours(&bs_1, &bs_2);

        Network network_1(&bs_1, &bs_2, &bs_3, &uniform_generator, config.Logs);

        chrono::steady_clock::time_point begin = chrono::steady_clock::now();
        int disc = network_1.run(1);
        chrono::steady_clock::time_point end = chrono::steady_clock::now();
        printf("\n=================================");
        cout << "\n>> \'network_1.Run()\' Time difference = " << chrono::duration_cast<chrono::seconds>(end - begin).count() << "[s]" << endl;
        printf("\nSeed: %d", config.Seed);
        printf("\nLamb: %4.2f", config.Users_per_second);
        printf("\nAll users: %d", network_1.Users_number);
        printf("\nDisconnected users: %d", disc);
        float prc = (((float)disc/(float)network_1.Users_number)*100);
        printf("\nLoss: %4.2f %%", prc);
        float power = bs_1.PowerConsumed + bs_2.PowerConsumed + bs_3.PowerConsumed;
        printf("\n----------------------------------");
        printf("\nPower Consumed summary: %4.2f J", power);
        printf("\n----------------------------------");
        printf("\nBS_1:");
        printf("\nPower Consumed: %4.2f J",bs_1.PowerConsumed);
        printf("\nRunningTime: %d ms", bs_1.RunningTime);
        printf("\nSleepingTime: %d ms", bs_1.SleepingTime);

        printf("\n----------------------------------");
        printf("\nBS_2:");
        printf("\nPower Consumed: %4.2f J",bs_2.PowerConsumed);
        printf("\nRunningTime: %d ms", bs_2.RunningTime);
        printf("\nSleepingTime: %d ms", bs_2.SleepingTime);

        printf("\n----------------------------------");
        printf("\nBS_3:");
        printf("\nPower Consumed: %4.2f J",bs_3.PowerConsumed);
        printf("\nRunningTime: %d ms", bs_3.RunningTime);
        printf("\nSleepingTime: %d ms", bs_3.SleepingTime);

        printf("\n=================================");
        printf("\n");
    }

    // Config config;
    // UniformDistribution uniform_generator(config.Min_mi, config.Max_mi, config.Seed);
    // ExponentialDistribution exponential_generator_1(config.Seed);
    // ExponentialDistribution exponential_generator_2(config.Seed+22);
    // ExponentialDistribution exponential_generator_3(config.Seed+333);

    // BaseStation bs_1(1 , config.Users_per_second, config.Max_resource_blocks, &exponential_generator_1, config.L);
    // BaseStation bs_2(2 , config.Users_per_second, config.Max_resource_blocks, &exponential_generator_2, config.L);
    // BaseStation bs_3(3 , config.Users_per_second, config.Max_resource_blocks, &exponential_generator_3, config.L);

    // bs_1.addNeighbours(&bs_2, &bs_3);
    // bs_2.addNeighbours(&bs_3, &bs_1);
    // bs_3.addNeighbours(&bs_1, &bs_2);

    // Network network_1(&bs_1, &bs_2, &bs_3, &uniform_generator, config.Logs);

    // chrono::steady_clock::time_point begin = chrono::steady_clock::now();
    // int disc = network_1.run(1);
    
    // chrono::steady_clock::time_point end = chrono::steady_clock::now();
    //     printf("\n-------------------------");
    //     cout << "\n>> \'network_1.Run()\' Time difference = " << chrono::duration_cast<chrono::seconds>(end - begin).count() << "[s]" << endl;
    //     printf("\nseed: %d", config.Seed);
    //     printf("\nlamb: %4.2f", config.Users_per_second);
    //     printf("\nAll users: %d", network_1.Users_number);
    //     printf("\nDisconnected users: %d", disc);
    //     printf("\n");



        

    return 0;
}