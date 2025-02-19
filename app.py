from flask import Flask, render_template, request, jsonify
from datetime import datetime
from typing import Dict, List

app = Flask(__name__)

### 🏗 CLASSES ###

class Product:
    """Modélise un produit avec ses informations essentielles."""
    def __init__(self, name: str, category: str, price: float, ingredients: List[str]):
        self.name = name
        self.category = category
        self.price = price
        self.ingredients = ingredients

    def __str__(self):
        return f"{self.name} ({self.category}) - {self.price}€ | Ingrédients: {', '.join(self.ingredients)}"


class Production:
    """Modélise une production d'un produit en kg avec des métadonnées."""
    def __init__(self, product: Product, quantity: float, production_date: str):
        self.product = product
        self.quantity = quantity
        self.production_date = production_date

    def __str__(self):
        return f"Production de {self.quantity} kg de {self.product.name} ({self.production_date})"


class ProductionRepository:
    """Stocke les productions et gère le suivi quotidien."""
    def __init__(self):
        self.daily_production: Dict[str, List[Production]] = {}

    def add_production(self, production: Production):
        """Ajoute une production et stocke chaque produit par date."""
        if production.production_date not in self.daily_production:
            self.daily_production[production.production_date] = []
        self.daily_production[production.production_date].append(production)

    def get_daily_production(self):
        """Retourne la production totale par jour sous forme de dictionnaire."""
        daily_totals = {}
        for date, productions in self.daily_production.items():
            daily_totals[date] = sum(prod.quantity for prod in productions)
        return daily_totals


class Stock:
    """Gère le stock en cumulant la production nette après retrait du gaspillage."""
    def __init__(self):
        self.stock_data: Dict[str, float] = {}
        self.initial_stock = 0

    def set_initial_stock(self, value: float):
        """Définit le stock initial."""
        self.initial_stock = value
        self.stock_data["initial"] = value

    def update_stock(self, date: str, production_kg: float, waste_kg: float):
        """Met à jour le stock en tenant compte du gaspillage."""
        stock_nette = max(production_kg - waste_kg, 0)

        previous_date = sorted(self.stock_data.keys())[-1] if self.stock_data else None
        previous_stock = self.stock_data[previous_date] if previous_date else self.initial_stock

        self.stock_data[date] = previous_stock + stock_nette

    def get_stock(self, date: str) -> float:
        return self.stock_data.get(date, self.initial_stock)


class Gaspillage:
    """Calcule le gaspillage des films et cartons."""
    def __init__(self):
        self.daily_waste = {}
        self.machines_output = {}

    def register_machine_output(self, date: str, machine_m1: int, machine_m2: int):
        """Enregistre le nombre de films utilisés."""
        self.machines_output[date] = machine_m1 + machine_m2

    def calculate_waste(self, production_repo: ProductionRepository):
        """Compare la production avec les films utilisés et calcule le gaspillage."""
        self.daily_waste.clear()

        for date, production_kg in production_repo.get_daily_production().items():
            films_necessaires = production_kg * 20
            films_utilises = self.machines_output.get(date, 0)
            waste_kg = max((films_utilises - films_necessaires) * 0.005, 0)

            self.daily_waste[date] = {
                "total_production": production_kg,
                "films_necessaires": films_necessaires,
                "films_utilises": films_utilises,
                "waste_kg": waste_kg
            }

        return self.daily_waste


### 📌 INSTANCIATION ###
production_repo = ProductionRepository()
stock_manager = Stock()
gaspillage_manager = Gaspillage()


### 📌 ROUTES FLASK ###
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/set_stock', methods=['POST'])
def set_stock():
    data = request.json
    stock_manager.set_initial_stock(float(data['stock']))
    return jsonify({"message": "Stock initial mis à jour."})

@app.route('/add_production', methods=['POST'])
def add_production():
    data = request.json
    product = Product(data['name'], data['category'], float(data['price']), data['ingredients'])
    production = Production(product, float(data['production']), data['date'])

    production_repo.add_production(production)
    return jsonify({"message": "Production ajoutée."})

@app.route('/register_machines', methods=['POST'])
def register_machines():
    data = request.json
    date = data['date']
    m1 = int(data['m1'])
    m2 = int(data['m2'])

    gaspillage_manager.register_machine_output(date, m1, m2)
    return jsonify({"message": "Valeurs M1 et M2 enregistrées."})

@app.route('/get_report', methods=['GET'])
def get_report():
    gaspillage_data = gaspillage_manager.calculate_waste(production_repo)

    for date, data in gaspillage_data.items():
        stock_manager.update_stock(date, data["total_production"], data["waste_kg"])

    return jsonify({
        "gaspillage": gaspillage_data,
        "stock": stock_manager.stock_data
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
