class Car:
    def start(self):
        print("Car started")

    def drive(self, speed):
        print(f"Driving at {speed} km/h")

car = Car()
car.start()
car.drive(60)
