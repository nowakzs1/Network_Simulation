import json
import matplotlib.pyplot as plt
import numpy as np
import os

# Funkcja do wczytywania danych z pliku JSON
def wczytaj_dane(nazwa_pliku):
    with open(nazwa_pliku, 'r') as file:
        data = json.load(file)
    keys = list(map(float, data.keys()))  # Konwersja kluczy na float
    # values = list(data.values())
    values = []
    for value in data.values():
        values.append(int(value))
    return keys, values

# Lista plików JSON
lista_plikow = [f'results/initial_phase_seed_{i}_date_04_06.json' for i in range(5, 141, 15)]

# Inicjalizacja wykresu
plt.figure(figsize=(12, 6))

# Inicjalizacja zmiennej do przechowywania maksymalnej wartości Y
max_y_value = 0

# Iteracja po plikach i dodawanie danych do wykresu
for i, plik in enumerate(lista_plikow):
    if os.path.exists(plik):
        keys, values = wczytaj_dane(plik)
        plt.plot(keys, values, label=f'Ziarno: {i}')
        max_y_value = max(max_y_value, max(values))
    else:
        print(f'Plik {plik} nie istnieje.')

# Ustawienia osi X
plt.xlabel('Czas')
plt.ylabel('Liczba użytkowników w systemie')

# Formatowanie osi X z zaokrąglonymi wartościami
if keys:
    plt.xticks(np.arange(min(keys), max(keys)+1, step=100000), rotation=45)

# Formatowanie osi Y, aby wartości wyświetlały się co 50
plt.yticks(np.arange(0, max_y_value + 10, step=50))

# Dodanie tytułu i legendy
plt.title('Liczba użytkowników w sieci w czasie')
plt.legend()

# Wyświetlenie wykresu
plt.tight_layout()
plt.show()
