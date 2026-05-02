import json
import os

LEADERBOARD_FILE = "leaderboard.json"
SETTINGS_FILE = "settings.json"  # файлы для хранения рекордов и настроек


def load_json(filename, default):
    if not os.path.exists(filename): 
        return default  # если файла нет — возвращаем значения по умолчанию

    with open(filename, "r", encoding="utf-8") as f:
        try: 
            return json.load(f)  # загрузка JSON данных
        except: 
            return default  # защита от битого/пустого файла


def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)  # сохранение с форматированием и поддержкой UTF-8


def get_top_scores():
    return load_json(LEADERBOARD_FILE, [])  # получение списка рекордов


def save_score(name, score, distance):
    scores = get_top_scores()

    scores.append({
        "name": name,
        "score": score,
        "distance": int(distance)
    })  # добавление нового результата

    scores = sorted(scores, key=lambda x: x["score"], reverse=True)[:10]  
    # сортировка по очкам и оставляем топ-10

    save_json(LEADERBOARD_FILE, scores)  # сохранение обновлённого списка


def load_settings():
    default = {
        "sound": True,
        "car_color": "Blue",
        "difficulty": "Medium"
    }  # дефолтные настройки

    return load_json(SETTINGS_FILE, default)  # загрузка или возврат дефолта


def save_settings(settings):
    save_json(SETTINGS_FILE, settings)  # сохранение пользовательских настроек
