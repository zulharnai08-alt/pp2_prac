
-- ПРОЦЕДУРА 1: добавить телефон контакту

CREATE OR REPLACE PROCEDURE add_phone(   -- OR REPLACE — перезапишет если уже существует
    p_contact_name VARCHAR,              -- входной параметр: имя контакта
    p_phone        VARCHAR,              -- входной параметр: номер телефона
    p_type         VARCHAR               -- входной параметр: тип (home/work/mobile)
)
LANGUAGE plpgsql AS $$                   -- язык написания — PL/pgSQL
DECLARE
    v_id INT;                            -- переменная для хранения id найденного контакта
BEGIN
    -- ищем контакт по имени, сохраняем его id в переменную v_id
    SELECT id INTO v_id FROM contacts WHERE name = p_contact_name;

    IF v_id IS NOT NULL THEN             -- если контакт найден
        INSERT INTO phones (contact_id, phone, type)
        VALUES (v_id, p_phone, p_type);  -- добавляем телефон привязанный к этому контакту
    ELSE
        -- контакт не найден — просто уведомление, НЕ ошибка (Python это не увидит!)
        RAISE NOTICE 'Contact "%" not found.', p_contact_name;
    END IF;
END;
$$;



-- ПРОЦЕДУРА 2: переместить контакт в группу

CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,              -- имя контакта которого перемещаем
    p_group_name   VARCHAR               -- название новой группы
)
LANGUAGE plpgsql AS $$
DECLARE
    v_group_id INT;                      -- переменная для id группы
BEGIN
    -- создаём группу если её ещё нет, иначе ничего не делаем
    INSERT INTO groups (name) VALUES (p_group_name)
    ON CONFLICT (name) DO NOTHING;

    -- получаем id группы (только что созданной или уже существующей)
    SELECT id INTO v_group_id FROM groups WHERE name = p_group_name;

    -- обновляем group_id у контакта — перемещаем его в новую группу
    UPDATE contacts SET group_id = v_group_id WHERE name = p_contact_name;
END;
$$;



-- ФУНКЦИЯ: поиск контактов (возвращает таблицу)

CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE (                          -- функция возвращает набор строк как таблицу
    contact_name  VARCHAR,
    contact_email VARCHAR,
    group_name    VARCHAR,
    phone_list    TEXT                   -- все телефоны склеенные в одну строку
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY                         -- возвращаем результат SELECT как таблицу
    SELECT
        c.name,
        c.email,
        g.name,
        string_agg(p.phone, ', ')        -- склеивает все телефоны через ", " в одну строку
    FROM contacts c
    LEFT JOIN groups g ON c.group_id = g.id   -- присоединяем группу (NULL если нет группы)
    LEFT JOIN phones p ON c.id = p.contact_id -- присоединяем телефоны (NULL если нет телефонов)
    WHERE c.name  ILIKE '%' || p_query || '%' -- ищем по имени, без учёта регистра
       OR c.email ILIKE '%' || p_query || '%' -- ИЛИ по email
       OR p.phone ILIKE '%' || p_query || '%' -- ИЛИ по номеру телефона
    GROUP BY c.id, c.name, c.email, g.name;  -- группируем чтобы string_agg работал корректно
END;
$$;
