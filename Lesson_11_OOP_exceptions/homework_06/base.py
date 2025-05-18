from abc import ABC

import exceptions


class Vehicle(ABC):

    def __init__(self, weight: int = 1500, started: bool = False, fuel: int = 50, fuel_consumption: int = 10):
        super().__init__()
        self.started = started
        self.configure(weight, fuel, fuel_consumption)

    def configure(self, weight: int, fuel: int, fuel_consumption: int):
        self.weight = weight
        self.fuel = fuel
        self.fuel_consumption = fuel_consumption

    def start(self):
        if not self.started:
            if self.fuel > 0:
                self.started = True
            else:
                raise exceptions.LowFuelError

    def move(self, distance: int):
        fuel_required = self.fuel_consumption * distance
        if fuel_required <= self.fuel:
            self.fuel -= fuel_required
        else:
            raise exceptions.NotEnoughFuel
