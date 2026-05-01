-- ПРОЦЕДУРА 1: Добавление телефона к контакту по его имени
CREATE OR REPLACE PROCEDURE add_phone(p_contact_name VARCHAR, p_phone VARCHAR, p_type VARCHAR)
LANGUAGE plpgsql AS $$
DECLARE
    v_id INT; -- Переменная для хранения ID найденного контакта
BEGIN
    -- 1. Ищем ID контакта в таблице contacts, чье имя совпадает с переданным
    SELECT id INTO v_id FROM contacts WHERE name = p_contact_name;
    
    -- 2. Если контакт с таким именем нашелся (v_id не пустой)
    IF v_id IS NOT NULL THEN
        -- Вставляем новый номер в таблицу телефонов, привязывая его к найденному ID
        INSERT INTO phones (contact_id, phone, type) VALUES (v_id, p_phone, p_type);
    END IF;
END;
$$;

-- ПРОЦЕДУРА 2: Перенос контакта в группу (с автоматическим созданием группы)
CREATE OR REPLACE PROCEDURE move_to_group(p_contact_name VARCHAR, p_group_name VARCHAR)
LANGUAGE plpgsql AS $$
DECLARE
    v_group_id INT; -- Переменная для ID группы
BEGIN
    -- 1. Пытаемся добавить новую группу. 
    -- Если группа с таким именем уже есть, 'ON CONFLICT' просто ничего не делает (не выдает ошибку)
    INSERT INTO groups (name) VALUES (p_group_name) ON CONFLICT (name) DO NOTHING;
    
    -- 2. Получаем ID этой группы (неважно, была она создана сейчас или раньше)
    SELECT id INTO v_group_id FROM groups WHERE name = p_group_name;
    
    -- 3. Обновляем запись контакта: меняем его group_id на новый
    UPDATE contacts SET group_id = v_group_id WHERE name = p_contact_name;
END;
$$;
