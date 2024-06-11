import random
import tkinter as tk
from tkinter import ttk
class Farm:
    def __init__(self):
        self.current_month = 0   # glowna klasa reprezentujaca farme
        self.money = 5000
        self.season = 1
        self.resources = {}
        self.total_resources_collected = {}  # Zmienne do sledzenia wartosci
        self.animals = {}
        self.max_animals = {}
        self.sickAnimals_count = {}
        self.crops = None
        self.total_medicines_used = 0

    def addAnimal(self, animal_type, quantity): # funkcja dodajaca zwierzeta
        if animal_type not in self.animals:
            self.animals[animal_type] = []
            resource_key = animal_type.__name__.lower() + "_resource"
            self.resources[resource_key] = 0
            self.total_resources_collected[resource_key] = 0  # wprowadzenie calkowitych zasobow
            self.max_animals[animal_type] = animal_type.default_capacity
            self.sickAnimals_count[animal_type] = 0

        for i in range(quantity):
            if len(self.animals[animal_type]) < self.max_animals[animal_type]:
                self.animals[animal_type].append(animal_type())

    def addCrops(self, crops):          # dodawanie upraw
        self.crops = crops

    def addSickCount(self, animal_type):              # dodawanie liczby chorych zwierzat
        self.sickAnimals_count[animal_type] += 1

    def decSickCount(self, animal_type):
        self.sickAnimals_count[animal_type] -= 1     # odejmowanie liczby chorych zwierzat

    def MonthlyEvents(self):          # wydarzenia miesieczne na farmie
        self.current_month += 1
        for animal_type, animals_list in self.animals.items():
            for animal in animals_list[:]:
                animal.age += 1
                self.money -= animal.costOfLiving

                # CHOROBY
                if not animal.is_sick and random.random() < animal.chanceOfSickness:
                    animal.is_sick = True

                if animal.is_sick:
                    for other_animal in animals_list:
                        if not other_animal.is_sick and random.random() < animal.chanceOfInfection:
                            other_animal.is_sick = True
                            self.addSickCount(animal_type)

                # RODZENIE
                if animal.is_pregnant:
                    animal.pregnancyTime += 1
                    animal.check_pregnancy()
                    if animal.readyToBirth:
                        animal.is_pregnant = False
                        animal.pregnancyTime = 0
                        animal.readyToBirth = False
                        if len(self.animals[animal_type]) < self.max_animals[animal_type]:
                            self.addAnimal(animal_type, 1)
                        else:
                            newbornAnimal = animal_type()
                            self.money += newbornAnimal.prize

                elif random.random() < animal.chanceOfBirth and animal.is_sick == False:
                    animal.is_pregnant = True

                # JAJKA MLEKO WEŁNA
                if random.random() < animal.chanceOfResource:
                    resource_key = animal_type.__name__.lower() + "_resource"
                    self.resources[resource_key] += 1
                    self.total_resources_collected[resource_key] += 1  # Aktualizacja całkowitych zasobów

                # UMIERANIE
                animal.check_ageDebuff()
                DeathChance = animal.chanceOfDeath
                if random.random() < DeathChance:
                    if animal.is_sick == True:
                        self.decSickCount(animal_type)
                    self.animals[animal_type].remove(animal)

        # koszty utrzymania plonow
        if self.crops:
            self.money -= self.crops.monthly_maintenance
            self.crops.total_maintenance_cost += self.crops.monthly_maintenance
            if self.current_month % 12 == 6:
                self.crops.check_for_drought()
                self.money += self.crops.annual_profit
                self.crops.total_profit += self.crops.annual_profit

    # AUTOMATYCZNE POWIĘKSZANIE MIEJSC NA ZWIERZAKI
    def AutoUpgrade(self, upgrade_manager):
        total_living_cost = sum(self.calculate_total_living_cost(animal_type) for animal_type in self.animals.keys())
        affordable_upgrades = [animal_type for animal_type, cost in upgrade_manager.upgrade_costs.items() if
                               self.money >= cost + total_living_cost]
        if affordable_upgrades:
            best_upgrade = max(affordable_upgrades, key=lambda animal_type: animal_type.default_capacityCost)
            upgrade_manager.upgrade_capacity(best_upgrade)

    # OBLICZANIE MIESIĘCZNEGO KOSZU UTRZYMANIA ZWIERZĄT
    def calculate_total_living_cost(self, animal_type):
        total_cost = 0
        for animal in self.animals.get(animal_type, []):
            total_cost += animal.costOfLiving
        return total_cost

    # WYŚWIETLANIE STATYSTYK
    def show_statistics(self):
        for animal_type, animals in self.animals.items():
            total_births = len([animal for animal in animals if animal.age == 0])
            total_deaths = len([animal for animal in animals if animal.age >= animal_type.default_capacity])
            resource_key = animal_type.__name__.lower() + "_resource"
            print(f"{animal_type.__name__}:")
            print(f"  Number of animals: {len(animals)}")
            print(f"  Total number of resources produced: {self.total_resources_collected[resource_key]}")
            print(f"  Births: {total_births}")
            print(f"  Deaths: {total_deaths}")
        if self.crops:
            final_crops_profit = self.crops.total_profit - self.crops.total_maintenance_cost
            print(f"Total profit from crops: {round(final_crops_profit)}")
            print(f"Total medicines used: {self.total_medicines_used}")  # Display the total medicines used


class UpgradeManager:              # klasa zajmujaca sie ulepszeniami
    def __init__(self, farm):
        self.farm = farm
        self.upgrade_costs = {}

    # USTAWIANIE KOSZTU POWIĘKSZENIA MIEJSC
    def set_upgrade_cost(self, animal_type):
        self.upgrade_costs[animal_type] = animal_type.default_capacityCost

    # POWIĘKSZENIE MIEJSC NA ZWIERZĄT
    def upgrade_capacity(self, animal_type):
        if self.farm.money >= self.upgrade_costs[animal_type]:
            self.farm.money -= self.upgrade_costs[animal_type]
            self.farm.max_animals[animal_type] += animal_type.capacity_increase
            self.upgrade_costs[animal_type] = int(self.upgrade_costs[animal_type] * 1.20)

class Market:                #klasa zajmujaca sie marketem
    def __init__(self):
        self.prices = {}
        self.medicine_price = 500

    # USTAWIANIE CEN ZASOBÓW DLA DANEGO ZWIERZĘCIA
    def set_price(self, animal_type):
        resource_key = animal_type.__name__.lower() + "_resource"
        self.prices[resource_key] = animal_type.resource_value

    # SPRZEDAWANIE WSZYSTKICH ZASOBÓW
    def sell_resources(self, farm):
        for resource_key, amount in farm.resources.items():
            if resource_key in self.prices:
                farm.money += amount * self.prices[resource_key]
        farm.resources = {key: 0 for key in farm.resources}

    # KUPOWANIE PODANEJ ILOSCI ZWIERZĄT
    def buy_animal(self, farm, animal_type, quantity):
        animals_price = int(animal_type().prize * 1.25)
        if len(farm.animals[animal_type]) + quantity < farm.max_animals[animal_type]:
            totalCost = animals_price * quantity
            if farm.money >= totalCost:
                farm.money -= totalCost
                farm.addAnimal(animal_type, quantity)

    # SPRZEDAWANIE WYBRANEGO ZWIERZĘCIA
    def sell_animal(self, farm, animal_type, index):
        animal = farm.animals[animal_type][index]
        animal_price = int(animal.prize)
        del farm.animals[animal_type][index]
        farm.money += animal_price

    # ULECZENIE WSZYSTKICH CHORYCH ZWIERZĄT
    def buy_medicine(self, farm):
        for animal_type, count in farm.sickAnimals_count.items():
            if count >= 1:
                if farm.money >= self.medicine_price:
                    farm.money -= self.medicine_price
                    farm.sickAnimals_count[animal_type] = 0
                    for animal in farm.animals[animal_type]:
                        animal.set_SickStatusFalse()
                        farm.total_medicines_used += 1
class Crops:                # klasa odpowiedzialna za plony
    def __init__(self, monthly_maintenance, annual_profit):
        self.monthly_maintenance = monthly_maintenance
        self.annual_profit = annual_profit
        self.upgrade_cost = 1000
        self.profit_increase = 2000
        self.total_maintenance_cost = 0
        self.total_profit = 0
        self.drought_penalty = 0.20  # Penalty percentage for drought
    def upgrade(self):
        self.annual_profit += self.profit_increase


    def check_for_drought(self):           # sprawdzanie szansy na susze
        if random.random() < 0.20:
            self.annual_profit = self.annual_profit *(1 - self.drought_penalty)

class Animal:                # klasa odpowiedzialna za zwierzeta na farmie
    default_capacity = 0
    capacity_increase = 0
    default_capacityCost = 0
    resource_value = 0
    costOfLiving = 0
    chanceOfSickness = 0.0001
    chanceOfInfection = 0.005

    def __init__(self):
        self.is_sick = False
        self.is_pregnant = False
        self.readyToBirth = False
        self.pregnancyTime = 0
        self.chanceOfResource = 0
        self.chanceOfBirth = 0
        self.chanceOfDeath = 0
        self.age = 0
        self.ageDebuff = 0
        self.prize = 0
        self.set_prize()

    def __str__(self):
        return (f"Type: {self.__class__.__name__}\n"
                f"Is Sick: {self.is_sick}\n"
                f"Is Pregnant: {self.is_pregnant}\n"
                f"Ready to Birth: {self.readyToBirth}\n"
                f"Pregnancy Time: {self.pregnancyTime}\n"
                f"Chance of Resource: {self.chanceOfResource}\n"
                f"Chance of Birth: {self.chanceOfBirth}\n"
                f"Chance of Death: {self.chanceOfDeath}\n"
                f"Age in months: {self.age}")

    # SPRAWDZANIE CZY ZWIERZE JEST W CIĄŻY
    def check_pregnancy(self):
        pass

    # OBLICZANIE MNOŻNIKA NA NEGATYWNE EFEKTY ZE WZGL. NA WIEK
    def check_ageDebuff(self):
        pass

    # USTAWIANIE CENY ZE WZGLĘDU NA WIEK
    def set_prize(self):
        pass

    def set_SickStatusFalse(self):
        self.is_sick = False

class Cow(Animal):                     # klasa dziedziczaca z klasy animal
    default_capacity = 5
    capacity_increase = 5
    default_capacityCost = 1200
    resource_value = 100
    costOfLiving = 50
    chanceOfSickness = 0.0001
    chanceOfInfection = 0.005

    def __init__(self):
        super().__init__()
        self.chanceOfResource = 0.35
        self.chanceOfBirth = 0.05

    def check_pregnancy(self):                # sprawdzanie ciazy zwierzat
        if self.pregnancyTime == 9:
            self.readyToBirth = True

    def check_ageDebuff(self):             # zwiekszanie szansy na smierc zwierzat
        if self.age <= 12:
            self.ageDebuff = 0
        elif self.age > 12 and self.age <= 72:
            self.ageDebuff = 1
        elif self.age > 72 and self.age < 120:
            self.ageDebuff = 2
        else:
            self.ageDebuff = 10
        if self.is_sick:
            self.chanceOfDeath = 0.015 * self.ageDebuff * 2
        else:
            self.chanceOfDeath = 0.015 * self.ageDebuff

    def set_prize(self):
        if self.age <= 24:
            self.prize = 2000
        elif self.age > 24 and self.age < 120:
            self.prize = 5000
        else:
            self.prize = 500

class Chicken(Animal):           # klasa dziedziczaca
    default_capacity = 15
    capacity_increase = 25
    default_capacityCost = 900
    resource_value = 20
    costOfLiving = 10
    chanceOfSickness = 0.00015
    chanceOfInfection = 0.005

    def __init__(self):
        super().__init__()
        self.chanceOfResource = 0.5
        self.chanceOfBirth = 0.06

    def check_pregnancy(self):
        if self.pregnancyTime == 1:
            self.readyToBirth = True

    def check_ageDebuff(self):
        if self.age <= 2:
            self.ageDebuff = 0
        elif self.age > 2 and self.age <= 16:
            self.ageDebuff = 1
        elif self.age > 16 and self.age < 48:
            self.ageDebuff = 2
        else:
            self.ageDebuff = 10
        if self.is_sick:
            self.chanceOfDeath = 0.015 * self.ageDebuff * 2
        else:
            self.chanceOfDeath = 0.015 * self.ageDebuff

    def set_prize(self):
        if self.age <= 2:
            self.prize = 100
        elif self.age > 2 and self.age <= 16:
            self.prize = 250
        else:
            self.prize = 50

class Sheep(Animal):
    default_capacity = 5
    capacity_increase = 5
    default_capacityCost = 1300
    resource_value = 500
    costOfLiving = 50
    chanceOfSickness = 0.0001
    chanceOfInfection = 0.005

    def __init__(self):
        super().__init__()
        self.chanceOfResource = 0.15
        self.chanceOfBirth = 0.05

    def check_pregnancy(self):
        if self.pregnancyTime == 5:
            self.readyToBirth = True

    def check_ageDebuff(self):
        if self.age <= 12:
            self.ageDebuff = 0
        elif self.age > 12 and self.age <= 60:
            self.ageDebuff = 1
        elif self.age > 60 and self.age < 96:
            self.ageDebuff = 2
        else:
            self.ageDebuff = 10
        if self.is_sick:
            self.chanceOfDeath = 0.015 * self.ageDebuff * 2
        else:
            self.chanceOfDeath = 0.015 * self.ageDebuff

    def set_prize(self):
        if self.age <= 12:
            self.prize = 2000
        elif self.age > 12 and self.age <= 60:
            self.prize = 6000
        else:
            self.prize = 1100

def main_menu():            # glowne menu konsoli
    global farm
    farm = Farm()
    print("Welcome to farm simulator!")
    print("1. Run simulation in GUI")
    print("2. Change length of simulation")
    print("3. Turn off")
    choice = input("Choose option: ")
    return choice

def run_simulation(duration):           # wlaczenie symulacji
    farm = Farm()
    upgrade_manager = UpgradeManager(farm)
    market = Market()

    farm.addAnimal(Cow, 2)
    farm.addAnimal(Sheep, 2)             # dodanie zwierzat do farmy i kosztow/zyskow z plonow
    farm.addAnimal(Chicken, 2)
    farm.addCrops(Crops(monthly_maintenance=300, annual_profit=9000))

    for animal_type in farm.animals:
        market.set_price(animal_type)
        upgrade_manager.set_upgrade_cost(animal_type)

    for i in range(duration):
        farm.MonthlyEvents()
        market.sell_resources(farm)
        farm.AutoUpgrade(upgrade_manager)
        market.buy_medicine(farm)
    print(f"Summary of simulation:")
    print(f"Money: {round(farm.money)}")               # wyswietlenie danych
    print(f"Months: {farm.current_month}")
    farm.show_statistics()

if __name__ == "__main__":
    duration = 150
    while True:
        choice = main_menu()
        if choice == "1":
            run_simulation(duration)             # kod odpowiedzialny za reagowania na poszczegolne przyciski na klawiaturze
            break
        elif choice == "2":
            duration = int(input("Enter the new month length of simulation: "))
        elif choice == "3":
            break
        else:
            print("Wrong choice!!!, try again.")


 # rozpoczęcie gui
class FarmSimulatorApp:         # glowna klasa aplikacji GUI
    def __init__(self, root):
        self.root = root
        self.root.title("Farm Simulator")    # ustawienie tytulu

        self.duration = 150
        self.farm = None      # referencja do obiektu farmy

        self.create_widgets()

    def create_widgets(self):          # funkcja odpowiedzialna za tworzenie widgetow
        self.main_frame = ttk.Frame(self.root, padding="10")          # glowna ramka GUI
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.label = ttk.Label(self.main_frame, text="Welcome to Farm Simulator!")
        self.label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

        self.run_button = ttk.Button(self.main_frame, text="Run Simulation", command=self.run_simulation)
        self.run_button.grid(row=1, column=0, pady=5)

        self.change_button = ttk.Button(self.main_frame, text="Change Simulation Length", command=self.change_length)
        self.change_button.grid(row=2, column=0, pady=5)        # tworzenie przyciskow do symulacji

        self.quit_button = ttk.Button(self.main_frame, text="Quit", command=self.root.quit)
        self.quit_button.grid(row=3, column=0, pady=5)

        self.text_output = tk.Text(self.main_frame, wrap="word", width=60, height=20)
        self.text_output.grid(row=1, column=1, rowspan=3, padx=(10, 0))

    def run_simulation(self):
        self.text_output.delete(1.0, tk.END)    # czysci wszystkie pola tekstowe przed symulacja

        self.farm = Farm()
        upgrade_manager = UpgradeManager(self.farm)      # tworzenie farmy i obiektow, inicjalizacja farmy jak w kodzie na gorze
        market = Market()

        self.farm.addAnimal(Cow, 2)
        self.farm.addAnimal(Sheep, 2)
        self.farm.addAnimal(Chicken, 2)
        self.farm.addCrops(Crops(monthly_maintenance=300, annual_profit=9000))

        for animal_type in self.farm.animals:
            market.set_price(animal_type)
            upgrade_manager.set_upgrade_cost(animal_type)

        for i in range(self.duration):
            self.farm.MonthlyEvents()
            market.sell_resources(self.farm)
            self.farm.AutoUpgrade(upgrade_manager)
            market.buy_medicine(self.farm)

        summary = f"Summary of simulation:\nMoney: {round(self.farm.money)}\nMonths: {self.farm.current_month}\n"
        self.text_output.insert(tk.END, summary)
        self.show_statistics()                        # wyswietlenie wynikow

    def change_length(self):
        def set_length():
            try:                        # zmienianie dlugosci symulacji
                self.duration = int(duration_entry.get())
                length_window.destroy()
            except ValueError:
                duration_entry.delete(0, tk.END)
                duration_entry.insert(0, "Enter a valid number")

        length_window = tk.Toplevel(self.root)
        length_window.title("Change Simulation Length")    # tworzenie nowego okna

        ttk.Label(length_window, text="Enter new length of simulation (months):").grid(row=0, column=0, padx=10, pady=10)
        duration_entry = ttk.Entry(length_window)
        duration_entry.grid(row=1, column=0, padx=10, pady=10)
        duration_entry.insert(0, str(self.duration))

        ttk.Button(length_window, text="Set Length", command=set_length).grid(row=2, column=0, padx=10, pady=10)

    def show_statistics(self):                    # wyswietlanie danych
        for animal_type, animals in self.farm.animals.items():
            total_births = len([animal for animal in animals if animal.age == 0])
            total_deaths = len([animal for animal in animals if animal.age >= animal_type.default_capacity])
            resource_key = animal_type.__name__.lower() + "_resource"

            stats = (f"{animal_type.__name__}:\n"
                     f"  Number of animals: {len(animals)}\n"
                     f"  Total number of resources produced: {self.farm.total_resources_collected[resource_key]}\n"
                     f"  Births: {total_births}\n"
                     f"  Deaths: {total_deaths}\n")

            self.text_output.insert(tk.END, stats)

        if self.farm.crops:
            final_crops_profit = self.farm.crops.total_profit - self.farm.crops.total_maintenance_cost
            crops_stats = (f"Total profit from crops: {round(final_crops_profit)}\n"
                           f"Total medicines used: {self.farm.total_medicines_used}\n")

            self.text_output.insert(tk.END, crops_stats)

if __name__ == "__main__":
    root = tk.Tk()               # funkcja uruchamiajaca interfejs glowny GUI
    app = FarmSimulatorApp(root)
    root.mainloop()
