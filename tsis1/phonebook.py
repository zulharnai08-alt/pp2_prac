def import_from_csv():  
    # Объявляем функцию для импорта данных из CSV-файла

    filename = input("CSV file name (e.g., contacts.csv): ")  
    # Запрашиваем у пользователя имя CSV-файла

    if not os.path.exists(filename):  
        # Проверяем, существует ли файл по указанному пути
        print("File not found!")  
        # Если файла нет — выводим сообщение
        return  
        # И выходим из функции

    try:  
        # Начинаем блок обработки ошибок

        with open(filename, mode='r', encoding='utf-8') as f:  
            # Открываем файл для чтения в кодировке UTF-8

            reader = csv.DictReader(f)  
            # Создаём объект, который читает CSV как словари (ключи — заголовки колонок)

            with get_connection() as conn:  
                # Получаем соединение с базой данных

                with conn.cursor() as cur:  
                    # Создаём курсор для выполнения SQL-запросов

                    for row in reader:  
                        # Проходим по каждой строке CSV-файла (как словарь)

                        # 1. Добавляем группу, если её нет
                        cur.execute(
                            "INSERT INTO groups (name) VALUES (%s) ON CONFLICT (name) DO NOTHING",
                            (row['group'],)
                        )  
                        # Пытаемся вставить группу
                        # Если группа с таким именем уже есть — ничего не делаем

                        # 2. Добавляем контакт (или обновляем почту, если имя уже есть)
                        cur.execute("""
                            INSERT INTO contacts (name, email, birthday, group_id) 
                            VALUES (%s, %s, %s, (SELECT id FROM groups WHERE name = %s))
                            ON CONFLICT (name) DO UPDATE SET email = EXCLUDED.email
                            RETURNING id
                        """, (row['name'], row['email'], row['birthday'], row['group']))  
                        # Добавляем контакт:
                        # - name, email, birthday берём из CSV
                        # - group_id получаем через подзапрос
                        # Если контакт с таким именем уже есть — обновляем email
                        # RETURNING id возвращает ID контакта

                        c_id = cur.fetchone()[0]  
                        # Получаем ID вставленного или обновлённого контакта

                        # 3. Добавляем телефон
                        cur.execute(
                            "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
                            (c_id, row['phone'], row['type'])
                        )  
                        # Добавляем номер телефона, связанный с контактом

                conn.commit()  
                # Сохраняем все изменения в базе данных

        print("CSV Import successful!")  
        # Сообщаем об успешном завершении

    except Exception as e:  
        # Если произошла ошибка — ловим её
        print(f"CSV Error: {e}")  
        # Выводим сообщение об ошибке
