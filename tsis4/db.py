import psycopg2


class Database:
    def __init__(self):
        # подключение к postgresql базе данных
        self.conn = psycopg2.connect(
            dbname="snake_db",
            user="postgres",
            password="1234",
            host="localhost"
        )
        self.cursor = self.conn.cursor()
        self._create_tables()  # создаём таблицы сразу при запуске если их нет

    def _create_tables(self):
        # создаём таблицу игроков - хранит уникальные имена
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id       SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL
            );
        """)

        # создаём таблицу сессий - каждая запись это одна сыгранная игра
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS game_sessions (
                id            SERIAL PRIMARY KEY,
                player_id     INTEGER REFERENCES players(id),
                score         INTEGER   NOT NULL,
                level_reached INTEGER   NOT NULL,
                played_at     TIMESTAMP DEFAULT NOW()
            );
        """)

        self.conn.commit()  # фиксируем создание таблиц в базе

    def get_or_create_player(self, username):
        """
        ищет игрока по имени, если не находит - создаёт нового.
        возвращает id игрока из таблицы players.
        on conflict do nothing - не падает если имя уже есть.
        """
        self.cursor.execute(
            "INSERT INTO players (username) VALUES (%s) ON CONFLICT (username) DO NOTHING",
            (username,)
        )
        self.conn.commit()

        # отдельный select нужен потому что insert не возвращает id при конфликте
        self.cursor.execute(
            "SELECT id FROM players WHERE username = %s", (username,)
        )
        return self.cursor.fetchone()[0]

    def save_session(self, player_id, score, level):
        """
        сохраняет результат одной игры в таблицу game_sessions.
        вызывается автоматически в конце каждой игры.
        played_at проставляется базой данных через default now().
        """
        self.cursor.execute(
            "INSERT INTO game_sessions (player_id, score, level_reached) VALUES (%s, %s, %s)",
            (player_id, score, level)
        )
        self.conn.commit()

    def get_top_10(self):
        """
        возвращает топ-10 лучших результатов среди всех игроков.
        join соединяет таблицы чтобы получить имя игрока вместо его id.
        order by score desc - сортировка от большего к меньшему.
        to_char форматирует дату прямо в sql чтобы не делать это в python.
        """
        self.cursor.execute("""
            SELECT p.username, s.score, s.level_reached,
                   TO_CHAR(s.played_at, 'DD.MM.YY HH24:MI')
            FROM game_sessions s
            JOIN players p ON s.player_id = p.id
            ORDER BY s.score DESC
            LIMIT 10
        """)
        return self.cursor.fetchall()

    def get_personal_best(self, player_id):
        """
        возвращает максимальный счёт конкретного игрока.
        max() - агрегатная функция sql, считает максимум по колонке.
        если игрок ещё не играл - max вернёт none, тогда возвращаем 0.
        """
        self.cursor.execute(
            "SELECT MAX(score) FROM game_sessions WHERE player_id = %s",
            (player_id,)
        )
        result = self.cursor.fetchone()[0]
        return result if result else 0  # защита от none если игр ещё не было

    def close(self):
        # закрываем курсор и соединение - важно вызвать перед выходом из программы
        self.cursor.close()
        self.conn.close()
