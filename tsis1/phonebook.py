def import_from_csv():
    filename = input("CSV file name (e.g., contacts.csv): ")
    if not os.path.exists(filename):
        print("File not found!")
        return

    try:
        with open(filename, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            with get_connection() as conn:
                with conn.cursor() as cur:
                    for row in reader:
                        # 1. Добавляем группу, если её нет
                        cur.execute("INSERT INTO groups (name) VALUES (%s) ON CONFLICT (name) DO NOTHING", (row['group'],))
                        
                        # 2. Добавляем контакт (или обновляем почту, если имя уже есть)
                        cur.execute("""
                            INSERT INTO contacts (name, email, birthday, group_id) 
                            VALUES (%s, %s, %s, (SELECT id FROM groups WHERE name = %s))
                            ON CONFLICT (name) DO UPDATE SET email = EXCLUDED.email
                            RETURNING id
                        """, (row['name'], row['email'], row['birthday'], row['group']))
                        
                        c_id = cur.fetchone()[0]
                        
                        # 3. Добавляем телефон
                        cur.execute("INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)", 
                                    (c_id, row['phone'], row['type']))
                conn.commit()
        print("CSV Import successful!")
    except Exception as e:
        print(f"CSV Error: {e}")
