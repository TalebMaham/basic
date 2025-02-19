from datetime import datetime
from typing import Dict

### 🏗 CLASSE PRODUIT ###

class Product:
    """Modélise un produit avec ses informations essentielles."""
    def __init__(self, name: str, category: str, price: float, ingredients: list):
        self.name = name
        self.category = category
        self.price = price
        self.ingredients = ingredients

    def __str__(self):
        return f"{self.name} ({self.category}) - {self.price}€"


### 🏗 CLASSE PRODUCTION ###

class Production:
    """Modélise une production d'un produit en kg avec des métadonnées."""
    def __init__(self, product: Product, quantity: float, production_date: str):
        self.product = product
        self.quantity = quantity  # Production en kg
        self.production_date = production_date  # Date de production

    def __str__(self):
        return f"Production de {self.quantity} kg de {self.product.name} ({self.production_date})"


### 🏗 CLASSE REPOSITORY ###

class ProductionRepository:
    """Stocke les productions et gère le suivi quotidien."""
    def __init__(self):
        self.daily_production: Dict[str, float] = {}  # Stocke la production par jour

    def add_production(self, production: Production):
        """Ajoute une production et met à jour les statistiques."""
        if production.production_date not in self.daily_production:
            self.daily_production[production.production_date] = 0

        self.daily_production[production.production_date] += production.quantity

    def get_daily_production(self):
        """Retourne la production totale par jour."""
        return self.daily_production


### 🏗 CLASSE STOCK CUMULATIF ###

class Stock:
    """Gère le stock en cumulant la production nette après retrait du gaspillage."""
    
    def __init__(self):
        self.stock_data: Dict[str, float] = {}  # Stock cumulé par date

    def update_stock(self, date: str, production_kg: float, waste_kg: float):
        """
        Ajoute la production au stock après retrait du gaspillage et accumulation du stock précédent.
        """
        stock_nette = max(production_kg - waste_kg, 0)  # Production nette après gaspillage

        # Récupérer le stock de la veille
        previous_date = sorted(self.stock_data.keys())[-1] if self.stock_data else None
        previous_stock = self.stock_data[previous_date] if previous_date else 0

        # Ajouter la production nette au stock cumulatif
        self.stock_data[date] = previous_stock + stock_nette

    def get_stock(self, date: str) -> float:
        """Retourne le stock disponible à une date donnée."""
        return self.stock_data.get(date, 0)

    def get_total_stock(self) -> float:
        """Retourne le stock total cumulé."""
        return sum(self.stock_data.values())

    def __str__(self):
        report = "📦 État du Stock Cumulatif 📦\n"
        for date, qty in sorted(self.stock_data.items()):
            report += f"{date} : {qty:.2f} kg\n"
        return report


### 🏗 CLASSE GASPIAGE (CORRIGÉE) ###

class Gaspillage:
    """Calcule le gaspillage des films et cartons en kg basé sur la production et les films utilisés."""

    def __init__(self):
        self.daily_waste = {}  # Stocke le gaspillage par jour
        self.machines_output = {}  # Stocke le nombre de films utilisés
        self.alerts = []  # Liste des alertes en cas d'abus ou d'erreur

    def register_machine_output(self, date: str, machine_m1: int, machine_m2: int):
        """
        Enregistre le nombre de films utilisés :
        - M1 : Nombre de films de 500g
        - M2 : Nombre de films de 250g
        """
        self.machines_output[date] = machine_m1 + machine_m2  # Total des films utilisés

    def calculate_waste(self, production_repo: ProductionRepository):
        """Compare la production réelle avec le nombre de films utilisés."""
        self.daily_waste.clear()
        self.alerts.clear()

        for date, production_kg in production_repo.get_daily_production().items():
            films_necessaires = production_kg * 20  # Films nécessaires
            films_utilises = self.machines_output.get(date, 0)  # Films réellement utilisés

            # Calcul du gaspillage des films
            waste_kg = max((films_utilises - films_necessaires) * 0.005, 0)  # Films gaspillés en kg

            # Détection des écarts
            if waste_kg > 0:
                self.alerts.append(f"🚨 {date} : {waste_kg:.2f} kg de films/cartons gaspillés !")
            elif films_utilises < films_necessaires:
                manque_kg = (films_necessaires - films_utilises) * 0.005
                self.alerts.append(f"⚠️ {date} : {manque_kg:.2f} kg de films manquants !")

            self.daily_waste[date] = {
                "total_production": production_kg,
                "films_necessaires": films_necessaires,
                "films_utilises": films_utilises,
                "waste_kg": waste_kg
            }

    def get_waste_report(self):
        """Retourne un rapport détaillé du gaspillage en kg et des erreurs machines/humaines."""
        report = "📉 Rapport de gaspillage des films et cartons 📉\n"
        for date, data in self.daily_waste.items():
            report += f"\n📆 {date} :\n"
            report += f"    • Production : {data['total_production']} kg\n"
            report += f"    • Films nécessaires : {data['films_necessaires']} unités\n"
            report += f"    • Films utilisés : {data['films_utilises']} unités\n"
            report += f"    • Films gaspillés (kg) : {data['waste_kg']:.2f} kg\n"

        if self.alerts:
            report += "\n🚨 Alertes détectées 🚨\n" + "\n".join(self.alerts)
        else:
            report += "\n✅ Aucune anomalie détectée."

        return report


### ✅ TESTONS AVEC LES DONNÉES QUE TU AS FOURNIES

# Création des produits
spaghetti = Product("Spaghetti", "Pâtes", 2.5, ["Semoule de blé", "Eau"])

# Instanciation des repositories et du gaspillage
production_repo = ProductionRepository()
gaspillage_manager = Gaspillage()
stock_manager = Stock()

# 🔹 Le 26 : production = 1140 kg, M1=11800, M2=1000
production_repo.add_production(Production(spaghetti, 1140, "2025-02-26"))
gaspillage_manager.register_machine_output("2025-02-26", 11800, 1000)

# 🔹 Le 27 : production = 1480 kg, M1=148000, M2=15300
production_repo.add_production(Production(spaghetti, 1480, "2025-02-27"))
gaspillage_manager.register_machine_output("2025-02-27", 14800, 15300)

# 🔹 Le 28 : production = 1340 kg, M1=13000, M2=16000
production_repo.add_production(Production(spaghetti, 1340, "2025-02-28"))
gaspillage_manager.register_machine_output("2025-02-28", 13000, 16000)

# Calcul du gaspillage
gaspillage_manager.calculate_waste(production_repo)

# Mise à jour du stock après retrait du gaspillage
for date, data in sorted(gaspillage_manager.daily_waste.items()):
    stock_manager.update_stock(date, data["total_production"], data["waste_kg"])

# Affichage des rapports
print("\n--- Rapport de Gaspillage ---")
print(gaspillage_manager.get_waste_report())

print("\n--- État du Stock Cumulatif ---")
print(stock_manager)
