import psycopg2  # библиотека для подключения к PostgreSQL

def get_connection():
    # создаёт и возвращает соединение с базой данных
    return psycopg2.connect(
        dbname="TSIS1",       # название базы данных
        user="postgres",      # имя пользователя PostgreSQL
        password="1234",      # пароль
        host="localhost",     # сервер — локальный компьютер
        port="5432"           # стандартный порт PostgreSQL
    )
