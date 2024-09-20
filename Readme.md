# Network simulation -  a task for the Poznań University of Technology

## Task description

### Task:

Rozważmy system radiokomunikacyjny składający się z N stacji bazowych posiadających R bloków zasobów (ang. Resource Blocks). W losowych odstępach czasu 𝜏 (wynikającej z intensywności zgłoszeń λ) w każdej stacji bazowej pojawiają się użytkownicy. Każdy użytkownik zajmuje jeden bloków na losowy czas μ. Jeśli stacja bazowa nie ma wystarczającej liczby bloków zasobów by obsłużyć użytkownika jego zgłoszenie może być przekierowane do sąsiedniej stacji. Jeśli żadna ze stacji bazowych nie może obsłużyć zgłoszenia jest ono tracone. 
Intensywność zgłoszeń w systemie zmienia się cyklicznie: 
przez pierwsze 8 godziny intensywność zgłoszeń wynosi λ/2 
przez kolejne 6 godzin - 3λ/4, 
następnie przez 4 godziny wynosi λ, 
po czym spada do wartości 3λ/4 na 6 godzin i cykl się powtarza. Dla stacji bazowych można ustalić próg przejścia w stan uśpienia L (wyrażony w % zajętych bloków zasobów). Stacja bazowa w stanie uśpienia pobiera moc równą 1 W, a podczas gdy jest aktywna 200 W. Zgłoszenia z uśpionej stacji są przejmowane równomiernie przez sąsiednie stacje. Podobnie jeśli w jednej z sąsiednich komórkach przekroczony zostanie próg H (wyrażony w % zajętych bloków zasobów), uśpiona komórka jest aktywowana i przejmuje połowę zgłoszeń ze stacji, w której przekroczony został próg H. Proces uśpienia i aktywacji komórki trwa 50 ms i zużywa jednorazowo 1000 W.

### Methods

1. Action browsing – focuses on analyzing the actions in the model and the conditions that determine when an action starts. Does not explicitly handle interactions between events. Each time the clock is updated, the conditions for each action to occur are checked and if they are met, the action starts.

2. Event planning - A method characterized by prioritizing events in terms of their occurrence in time - the event log (which is nothing more than an Agenda in the interaction of processes).
Each entry in the event list is characterized by at least an absolute time indicator and a reference to the procedure to be executed after its occurrence.
The event list contains only the implementation of handling time events, which is why these events must necessarily implement within themselves the handling of possible conditional events that will affect the change in the system state.
The simulation operation should be started by implementing the first event in the event list, and the next events of the same type are planned by executing previous tasks (so-called Bootstrapping), or events of a different type are planned by executing previous tasks of a different type (e.g. planning the end of handling the event at the moment it starts).

### Program output for report:

Graphs:

1. Graph showing the number of users in simulated network over time for different seeds
![users_in_network_over_time_graph](/Placeholder/draw_all_seeds_output_1.png)
![users_in_network_over_time_graph](/Placeholder/draw_all_seeds_output_2.png)

2. Graph showing the initial phase of the simulation.
![initial_phase_graph](/Placeholder/draw_all_initial_phases_output.png)

## Programs

### Method_1/cpp

- **Method used:** 1
- **Programming language:** C++ (for simulation) and Python (for graphs)
- **Date of birth:** 06_2024

Files: 

1. **simulation.ccp** - default simulation 
2. **simulation_draw_users_in_time.ccp** - simulation which returns txt file with data (connected users over time)
3. **getCppOutputToJson_initial_phase.py** - Gets x amout of data from txt files and makes jsons
4. **getCppOutputToJson.py** - Gets all data from txt files and makes jsons

5. **users_in_network.py** - draws users_in_network graph from jsons

6. **users_in_network_initial_phase.py** - draws initial_phase graph from jsons

### Method_1/python

- **Method used:** 1
- **Programming language:** python
- **Date of birth:** 09_2024

Files: 
1. **Simulation_method_1.py** - makes json with simulation data (users in network over time)

### Method_2/python

- **Method used:** 2
- **Programming language:** python
- **Date of birth:** 08_2024

Files: 

1. **Simulation_method_2.py** - makes json with simulation data (users in network over time)

## Graphs

- **Designed for:** *Method_1/python* and *Method_2/python*
- **Programming language:** python
- **Date of birth:** 09_2024

Files: 

1. **draw_all_initial_phases.py** - draws data from jsons for x amount of data

**Output example:**

![initial_phase_graph](/Placeholder/draw_all_initial_phases_output.png)

2. **draw_all_seeds.py** - draws data from jsons

**Output example:**

![users_in_network_over_time_graph](/Placeholder/draw_all_seeds_output_2.png)