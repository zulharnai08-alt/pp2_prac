-- Создаем или заменяем функцию поиска контактов
-- На вход принимаем строку p_query (текст поиска)
-- Функция возвращает виртуальную ТАБЛИЦУ (TABLE) с четырьмя колонками
CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE (
    contact_name VARCHAR,   -- Имя контакта
    contact_email VARCHAR,  -- Почта
    group_name VARCHAR,     -- Название группы
    phone_list TEXT         -- Все телефоны одной строкой
) 
LANGUAGE plpgsql AS $$
BEGIN
    -- RETURN QUERY говорит функции вернуть результат выполнения SQL-запроса
    RETURN QUERY
    SELECT 
        c.name, 
        c.email, 
        g.name, 
        -- string_agg склеивает все найденные номера телефонов в одну строку через запятую
        string_agg(p.phone, ', ')
    FROM contacts c
    -- Используем LEFT JOIN, чтобы контакт отображался, даже если у него нет группы или телефона
    LEFT JOIN groups g ON c.group_id = g.id
    LEFT JOIN phones p ON c.id = p.contact_id
    -- ILIKE — это поиск без учета регистра. 
    -- Оператор || склеивает % (символ любого количества знаков) с поисковым запросом
    WHERE c.name ILIKE '%' || p_query || '%' 
       OR c.email ILIKE '%' || p_query || '%' 
       OR p.phone ILIKE '%' || p_query || '%'
    -- Группируем по ID контакта и имени группы, чтобы string_agg сработал правильно
    GROUP BY c.id, g.name;
END;
$$;
