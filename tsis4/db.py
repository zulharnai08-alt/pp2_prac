import psycopg2


class Database:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname="snake_db",
            user="postgres",
            password="1234",
            host="localhost"
        )
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id       SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL
            );
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS game_sessions (
                id            SERIAL PRIMARY KEY,
                player_id     INTEGER REFERENCES players(id),
                score         INTEGER   NOT NULL,
                level_reached INTEGER   NOT NULL,
                played_at     TIMESTAMP DEFAULT NOW()
            );
        """)
        self.conn.commit()

    def get_or_create_player(self, username):
        """Возвращает id игрока, создаёт если не существует"""
        self.cursor.execute(
            "INSERT INTO players (username) VALUES (%s) ON CONFLICT (username) DO NOTHING",
            (username,)
        )
        self.conn.commit()
        self.cursor.execute("SELECT id FROM players WHERE username = %s", (username,))
        return self.cursor.fetchone()[0]

    def save_session(self, player_id, score, level):
        """Сохраняет результат игровой сессии"""
        self.cursor.execute(
            "INSERT INTO game_sessions (player_id, score, level_reached) VALUES (%s, %s, %s)",
            (player_id, score, level)
        )
        self.conn.commit()

    def get_top_10(self):
        """Возвращает топ-10 результатов всех игроков"""
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
        """Возвращает лучший результат конкретного игрока"""
        self.cursor.execute(
            "SELECT MAX(score) FROM game_sessions WHERE player_id = %s",
            (player_id,)
        )
        result = self.cursor.fetchone()[0]
        return result if result else 0

    def close(self):
        self.cursor.close()
        self.conn.close()
