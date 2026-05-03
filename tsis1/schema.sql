-- Таблица групп (Family, Work, Friends, Other)
CREATE TABLE IF NOT EXISTS groups (        -- IF NOT EXISTS — не падает если таблица уже есть
    id   SERIAL PRIMARY KEY,              -- SERIAL = автоинкремент (1, 2, 3...)
    name VARCHAR(50) UNIQUE NOT NULL      -- UNIQUE — нельзя создать две группы с одним именем
);

-- Заполняем группы по умолчанию
INSERT INTO groups (name) VALUES ('Family'), ('Work'), ('Friends'), ('Other')
ON CONFLICT (name) DO NOTHING;            -- если группа уже есть — просто пропускаем, не ошибка

-- Таблица контактов
CREATE TABLE IF NOT EXISTS contacts (
    id       SERIAL PRIMARY KEY,
    name     VARCHAR(100) UNIQUE NOT NULL, -- имя уникальное — два контакта с одним именем запрещены
    email    VARCHAR(100),                 -- email необязателен (нет NOT NULL)
    birthday DATE,                         -- дата рождения необязательна
    group_id INTEGER REFERENCES groups(id) -- внешний ключ — связь с таблицей groups
);

-- Таблица телефонов (у одного контакта может быть несколько номеров)
CREATE TABLE IF NOT EXISTS phones (
    id         SERIAL PRIMARY KEY,
    contact_id INTEGER REFERENCES contacts(id) ON DELETE CASCADE, -- если удалить контакт —
                                                                  -- его телефоны удалятся тоже
    phone      VARCHAR(20) NOT NULL,                              -- номер обязателен
    type       VARCHAR(10) CHECK (type IN ('home', 'work', 'mobile')) -- только эти 3 значения разрешены
);
