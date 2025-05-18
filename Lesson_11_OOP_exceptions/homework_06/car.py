"""
создайте класс `Car`, наследник `Vehicle`
"""

from base import Vehicle
from engine import Engine

class Car(Vehicle):
    
    def __init__(self, engine: Engine, weight = 1500, started = False, fuel = 50, fuel_consumption = 10):
        super().__init__(weight, started, fuel, fuel_consumption)
        self.engine = engine

    def set_engine(self, engine: Engine):
        self.engine = engine
