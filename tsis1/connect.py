import psycopg2 # Подключаем библиотеку для работы с базой данных PostgreSQL
from config import params # Импортируем настройки (host, dbname, user, password) из файла config.py

# Функция для создания объекта соединения с базой
def get_connection():
    # Создаем соединение, распаковывая словарь params с помощью **
    conn = psycopg2.connect(**params)
    # Принудительно ставим кодировку UTF8, чтобы не было проблем с русскими буквами
    conn.set_client_encoding('UTF8')
    # Возвращаем готовый объект соединения (connection)
    return conn

# Функция для создания таблиц (здесь прописывается структура твоей БД)
def create_tables():
    # Список SQL-запросов для создания нужных таблиц
    # К примеру, создадим таблицу 'users', если она еще не существует
    commands = (
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL
        )
        """,
    )
    
    conn = None # Инициализируем переменную для соединения
    try:
        # Вызываем нашу функцию для подключения
        conn = get_connection()
        # Создаем курсор — это инструмент для отправки SQL-команд в базу
        cur = conn.cursor()
        
        # Перебираем и выполняем каждую команду из списка commands
        for command in commands:
            cur.execute(command)
        
        # Закрываем курсор после завершения всех команд
        cur.close()
        # Сохраняем (фиксируем) все изменения в базе данных
        conn.commit()
        print("Таблицы проверены/созданы успешно.")
        
    except (Exception, psycopg2.DatabaseError) as error:
        # Если возникнет любая ошибка (нет связи, ошибка в SQL), она выведется сюда
        print(f"Произошла ошибка: {error}")
        
    finally:
        # Блок finally выполняется всегда: закрываем соединение, чтобы не тратить ресурсы
        if conn is not None:
            conn.close()
            print("Соединение с БД закрыто.")

# Если мы запускаем именно этот файл, сработает создание таблиц
if __name__ == "__main__":
    create_tables()
