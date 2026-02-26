# json.py
import json

# Pythin objest
data = {
    "name": "Zulhar",
    "age": 19
}

# JSON write
with open("data.json", "w") as file:
    json.dump(data, file)

print("JSON файл сақталды!")

# JSON read
with open("data.json", "r") as file:
    loaded_data = json.load(file)

print("Оқылған мәлімет:", loaded_data)
