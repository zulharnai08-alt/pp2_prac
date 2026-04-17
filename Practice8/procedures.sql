-- Save one user.
CREATE OR REPLACE PROCEDURE upsert_phonebook_user(
    p_name TEXT,
    p_phone TEXT,
    p_surname TEXT DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM phonebook WHERE name = p_name) THEN
        UPDATE phonebook
        SET phone = p_phone,
            surname = COALESCE(p_surname, surname)
        WHERE name = p_name;
    ELSE
        INSERT INTO phonebook (name, surname, phone)
        VALUES (p_name, p_surname, p_phone);
    END IF;
END;
$$;

-- Save many users.
CREATE OR REPLACE PROCEDURE insert_many_phonebook_users(
    p_names TEXT[],
    p_phones TEXT[],
    p_surnames TEXT[] DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    i INT;
    v_name TEXT;
    v_phone TEXT;
    v_surname TEXT;
    v_names_len INT;
    v_phones_len INT;
    v_surnames_len INT;
BEGIN
    CREATE TEMP TABLE IF NOT EXISTS invalid_phonebook_data (
        name TEXT,
        surname TEXT,
        phone TEXT,
        reason TEXT
    ) ON COMMIT PRESERVE ROWS;

    TRUNCATE invalid_phonebook_data;

    v_names_len := COALESCE(array_length(p_names, 1), 0);
    v_phones_len := COALESCE(array_length(p_phones, 1), 0);
    v_surnames_len := COALESCE(array_length(p_surnames, 1), 0);

    IF v_names_len = 0 OR v_phones_len = 0 THEN
        RAISE EXCEPTION 'Names and phones must not be empty';
    END IF;

    IF v_names_len <> v_phones_len THEN
        RAISE EXCEPTION 'Names and phones count must be equal';
    END IF;

    IF p_surnames IS NOT NULL AND v_surnames_len <> v_names_len THEN
        RAISE EXCEPTION 'Surnames count must be equal';
    END IF;

    FOR i IN 1..v_names_len LOOP
        v_name := p_names[i];
        v_phone := p_phones[i];

        IF p_surnames IS NOT NULL THEN
            v_surname := p_surnames[i];
        ELSE
            v_surname := NULL;
        END IF;

        IF v_name IS NULL OR btrim(v_name) = '' THEN
            INSERT INTO invalid_phonebook_data
            VALUES (v_name, v_surname, v_phone, 'Bad name');
        ELSIF v_phone IS NULL OR v_phone !~ '^[+0-9][0-9 ()-]{6,19}$' THEN
            INSERT INTO invalid_phonebook_data
            VALUES (v_name, v_surname, v_phone, 'Bad phone');
        ELSIF EXISTS (SELECT 1 FROM phonebook WHERE name = v_name) THEN
            UPDATE phonebook
            SET phone = v_phone,
                surname = COALESCE(v_surname, surname)
            WHERE name = v_name;
        ELSE
            INSERT INTO phonebook (name, surname, phone)
            VALUES (v_name, v_surname, v_phone);
        END IF;
    END LOOP;
END;
$$;

-- Delete user data.
CREATE OR REPLACE PROCEDURE delete_phonebook_data(
    p_name TEXT DEFAULT NULL,
    p_phone TEXT DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF p_name IS NULL AND p_phone IS NULL THEN
        RAISE EXCEPTION 'Need name or phone';
    END IF;

    DELETE FROM phonebook
    WHERE (p_name IS NOT NULL AND name = p_name)
       OR (p_phone IS NOT NULL AND phone = p_phone);
END;
$$;
