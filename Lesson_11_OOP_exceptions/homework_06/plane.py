"""
создайте класс `Plane`, наследник `Vehicle`
"""

import exceptions
from base import Vehicle

class Plane(Vehicle):

    def __init__(self, max_cargo: int, weight = 1500, started = False, fuel = 50, fuel_consumption = 10):
        super().__init__(weight, started, fuel, fuel_consumption)
        self.cargo = 0
        self.max_cargo = max_cargo

    def load_cargo(self, loaded_cargo: int):
        new_cargo = self.cargo + loaded_cargo
        if new_cargo <= self.max_cargo:
            self.cargo = new_cargo
        else:
            raise exceptions.CargoOverload

    def remove_all_cargo(self) -> int:
        old_cargo = self.cargo
        self.cargo = 0
        return old_cargo