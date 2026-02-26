class Person:
    species = "Human"

    def __init__(self, name):
        self.name = name


person1 = Person("Ali")
person2 = Person("Dana")

print(person1.name)
print(person2.name)

print(person1.species)
print(person2.species)
