import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  
# абсолютный путь к папке файла 

SETTINGS_PATH = os.path.join(BASE_DIR, 'settings1.json')  
# полный путь к файлу настроек


DEFAULT_SETTINGS = {
    "snake_color": [0, 255, 0],
    "grid_overlay": True,
    "sound": True
}  # дефолтные значения 


def load_settings():
    if not os.path.exists(SETTINGS_PATH):
        save_settings(DEFAULT_SETTINGS)  # создаём файл, если его нет
        return DEFAULT_SETTINGS.copy()  # возвращаем копию 

    try:
        with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)  # загрузка настроек из файла

            for key, val in DEFAULT_SETTINGS.items():
                if key not in data:
                    data[key] = val  
                    # автоматическое добавление новых настроек 

            return data

    except (json.JSONDecodeError, IOError):
        save_settings(DEFAULT_SETTINGS)  
        # если файл повреждён или не читается — пересоздаём

        return DEFAULT_SETTINGS.copy()


def save_settings(settings):
    with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)  
        # сохранение с форматированием и поддержкой u
