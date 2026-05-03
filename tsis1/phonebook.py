import json
import csv
import os
from t1connect import get_connection  # импорт функции подключения к PostgreSQL


def search_extended():
    query_str = input("Search query (name / email / phone): ").strip()
    with get_connection() as conn:  # открываем соединение с БД
        with conn.cursor() as cur:  # создаём курсор для выполнения SQL
            # вызываем хранимую функцию search_contacts, ищет по имени/email/телефону
            cur.execute("SELECT * FROM search_contacts(%s::text)", (query_str,))
            rows = cur.fetchall()  # получаем все найденные строки
    if not rows:
        print("Nothing found.")
        return
    print(f"\n{'Name':<20} {'Email':<25} {'Group':<12} {'Phones'}")
    print("-" * 75)
    for r in rows:
        phones = r[3] if r[3] else "-"  # если телефонов нет — ставим прочерк
        print(f"{r[0]:<20} {str(r[1]):<25} {str(r[2]):<12} {phones}")


def search_by_email():
    query = input("Email search: ").strip()
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT c.name, c.email, g.name
                FROM contacts c
                LEFT JOIN groups g ON c.group_id = g.id  -- присоединяем группу контакта
                WHERE c.email ILIKE %s                   -- ILIKE = поиск без учёта регистра
                ORDER BY c.name
            """, (f"%{query}%",))  # %...% означает "содержит" подстроку
            rows = cur.fetchall()
    if not rows:
        print("Nothing found.")
        return
    print(f"\n{'Name':<20} {'Email':<25} {'Group'}")
    print("-" * 55)
    for r in rows:
        print(f"{r[0]:<20} {str(r[1]):<25} {str(r[2])}")


def filter_by_group():
    group_name = input("Group name (Friends / Work / Family / Other): ").strip()
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT c.name, c.email, g.name,
                       string_agg(p.phone, ', ') AS phones  -- склеивает все телефоны через запятую
                FROM contacts c
                JOIN groups g ON c.group_id = g.id          -- только контакты с группой
                LEFT JOIN phones p ON c.id = p.contact_id   -- телефоны если есть
                WHERE g.name ILIKE %s
                GROUP BY c.id, c.name, c.email, g.name      -- группируем чтобы string_agg работал
                ORDER BY c.name
            """, (f"%{group_name}%",))
            rows = cur.fetchall()
    if not rows:
        print("No contacts found in this group.")
        return
    print(f"\n{'Name':<20} {'Email':<25} {'Group':<12} {'Phones'}")
    print("-" * 75)
    for r in rows:
        phones = r[3] if r[3] else "-"
        print(f"{r[0]:<20} {str(r[1]):<25} {r[2]:<12} {phones}")


def interactive_nav():
    print("\nSort by:  1. Name   2. Birthday   3. Date added (ID)")
    sort_map = {"1": "name", "2": "birthday", "3": "id"}  # маппинг выбора к колонке
    sort_col = sort_map.get(input("> ").strip(), "name")   # если неверный ввод — сортируем по имени

    limit, offset = 3, 0  # limit = сколько записей на странице, offset = с какой начинать
    while True:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    # f-строка для подстановки колонки сортировки 
                    f"SELECT name, email, birthday FROM contacts"
                    f" ORDER BY {sort_col} LIMIT %s OFFSET %s",
                    (limit, offset)
                )
                rows = cur.fetchall()

        if not rows:
            if offset == 0:
                print("No contacts found.")
                break
            print("No more contacts.")
            offset = max(0, offset - limit)  # возвращаемся на предыдущую страницу
            continue

        print(f"\n{'Name':<20} {'Email':<25} {'Birthday'}")
        print("-" * 60)
        for r in rows:
            print(f"{r[0]:<20} {str(r[1]):<25} {str(r[2])}")

        cmd = input("\n[n] next  [p] prev  [q] quit: ").strip().lower()
        if cmd == 'n':
            offset += limit          # следующая страница — сдвигаем offset вперёд
        elif cmd == 'p':
            offset = max(0, offset - limit)  # предыдущая, но не меньше 0
        elif cmd == 'q':
            break


def export_to_json():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, email, birthday, group_id FROM contacts")
            contacts = cur.fetchall()
            data = []
            for c in contacts:
                # для каждого контакта отдельно получаем его телефоны
                cur.execute("SELECT phone, type FROM phones WHERE contact_id = %s", (c[0],))
                phones = [{"phone": p[0], "type": p[1]} for p in cur.fetchall()]
                # получаем название группы по group_id
                cur.execute("SELECT name FROM groups WHERE id = %s", (c[4],))
                g = cur.fetchone()
                data.append({
                    "name":     c[1],
                    "email":    c[2],
                    "birthday": str(c[3]) if c[3] else None,  # дату конвертируем в строку
                    "group":    g[0] if g else None,
                    "phones":   phones
                })

    # сохраняем файл в ту же папку где лежит скрипт
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "contacts.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)  # ensure_ascii=False — сохраняет кириллицу
    print(f"Exported {len(data)} contacts to {file_path}")


def import_from_json():
    filename = input("File name (default: contacts.json): ").strip() or "contacts.json"
    if not os.path.isabs(filename):  # если путь не абсолютный — ищем рядом со скриптом
        filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    if not os.path.exists(filename):
        print(f"File not found: {filename}")
        return

    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)  # загружаем весь JSON в список словарей

        with get_connection() as conn:
            with conn.cursor() as cur:
                for item in data:
                    # проверяем, существует ли уже такой контакт
                    cur.execute("SELECT id FROM contacts WHERE name = %s", (item['name'],))
                    exists = cur.fetchone()
                    if exists:
                        ans = input(f"'{item['name']}' already exists. Overwrite? (y/n): ").lower()
                        if ans != 'y':
                            continue  # пропускаем этот контакт
                        cur.execute("DELETE FROM contacts WHERE id = %s", (exists[0],))  # удаляем старый

                    group_name = item.get('group') or 'Other'  # если группа не указана — Other
                    # ON CONFLICT DO NOTHING — не падаем если группа уже есть
                    cur.execute("INSERT INTO groups (name) VALUES (%s) ON CONFLICT (name) DO NOTHING", (group_name,))
                    cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
                    g_id = cur.fetchone()[0]

                    birthday = item.get('birthday')
                    if birthday in (None, 'None', ''):  # обрабатываем все варианты пустой даты
                        birthday = None

                    cur.execute(
                        "INSERT INTO contacts (name, email, birthday, group_id)"
                        " VALUES (%s, %s, %s, %s) RETURNING id",  # RETURNING id — сразу получаем id новой записи
                        (item['name'], item.get('email'), birthday, g_id)
                    )
                    c_id = cur.fetchone()[0]
                    for p in item.get('phones', []):  # если phones отсутствует — берём пустой список
                        cur.execute(
                            "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
                            (c_id, p['phone'], p['type'])
                        )
            conn.commit()  # сохраняем все изменения в БД
        print("Import from JSON complete.")
    except Exception as e:
        print(f"Error: {e}")  # выводим ошибку если что-то пошло не так


def import_from_csv():
    filename = input("CSV file name (default: contacts.csv): ").strip() or "contacts.csv"
    if not os.path.isabs(filename):
        filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    if not os.path.exists(filename):
        print(f"File not found: {filename}")
        return

    try:
        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)  # читаем CSV как список словарей (первая строка = заголовки)
            with get_connection() as conn:
                with conn.cursor() as cur:
                    for row in reader:  # каждая строка CSV = один контакт
                        cur.execute("SELECT id FROM contacts WHERE name = %s", (row['name'],))
                        exists = cur.fetchone()
                        if exists:
                            ans = input(f"'{row['name']}' already exists. Overwrite? (y/n): ").lower()
                            if ans != 'y':
                                continue
                            cur.execute("DELETE FROM contacts WHERE id = %s", (exists[0],))

                        group_name = row.get('group') or 'Other'
                        cur.execute("INSERT INTO groups (name) VALUES (%s) ON CONFLICT (name) DO NOTHING", (group_name,))
                        cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
                        g_id = cur.fetchone()[0]

                        birthday = row.get('birthday') or None
                        if birthday == '':
                            birthday = None

                        cur.execute(
                            "INSERT INTO contacts (name, email, birthday, group_id)"
                            " VALUES (%s, %s, %s, %s) RETURNING id",
                            (row['name'], row.get('email'), birthday, g_id)
                        )
                        c_id = cur.fetchone()[0]

                        if row.get('phone'):  # телефон в CSV только один (в отличие от JSON)
                            cur.execute(
                                "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
                                (c_id, row['phone'], row.get('phone_type', 'mobile'))  # тип по умолчанию mobile
                            )
                conn.commit()
        print("Import from CSV complete.")
    except Exception as e:
        print(f"Error: {e}")


def add_phone():
    name  = input("Contact name: ").strip()
    phone = input("Phone number: ").strip()
    ptype = input("Type (home / work / mobile): ").strip() or "mobile"
    with get_connection() as conn:
        with conn.cursor() as cur:
            # вызываем хранимую процедуру PostgreSQL вместо прямого INSERT
            cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, ptype))
        conn.commit()
    print("Phone added.")


def move_group():
    name  = input("Contact name: ").strip()
    group = input("New group name: ").strip()
    with get_connection() as conn:
        with conn.cursor() as cur:
            # хранимая процедура создаёт группу если её нет и переносит контакт
            cur.execute("CALL move_to_group(%s, %s)", (name, group))
        conn.commit()
    print("Group updated.")


def add_contact():
    name     = input("Name: ").strip()
    email    = input("Email: ").strip() or None       # пустой ввод = None (NULL в БД)
    birthday = input("Birthday (YYYY-MM-DD) or Enter to skip: ").strip() or None
    group    = input("Group (Friends / Work / Family / Other): ").strip() or "Other"
    phone    = input("Phone: ").strip() or None
    ptype    = input("Phone type (home / work / mobile): ").strip() or "mobile"

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # создаём группу если её ещё нет
                cur.execute("INSERT INTO groups (name) VALUES (%s) ON CONFLICT (name) DO NOTHING", (group,))
                cur.execute("SELECT id FROM groups WHERE name = %s", (group,))
                g_id = cur.fetchone()[0]

                cur.execute(
                    "INSERT INTO contacts (name, email, birthday, group_id)"
                    " VALUES (%s, %s, %s, %s) RETURNING id",  # RETURNING id нужен чтобы добавить телефон
                    (name, email, birthday, g_id)
                )
                c_id = cur.fetchone()[0]  # id только что добавленного контакта

                if phone:  # телефон добавляем только если он был введён
                    cur.execute(
                        "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
                        (c_id, phone, ptype)
                    )
            conn.commit()  # фиксируем транзакцию
        print(f"Contact '{name}' added.")
    except Exception as e:
        print(f"Error: {e}")


def main():
    # словарь: ключ = номер пункта меню, значение = функция которую вызвать
    actions = {
        '1':  search_extended,
        '2':  search_by_email,
        '3':  filter_by_group,
        '4':  interactive_nav,
        '5':  export_to_json,
        '6':  import_from_json,
        '7':  import_from_csv,
        '8':  add_phone,
        '9':  move_group,
        '10': add_contact,
    }

    while True:  # бесконечный цикл — программа работает пока не выберешь 0
        print("\n--- PhoneBook TSIS1 ---")
        print("1.  Search (name / email / phone)")
        print("2.  Search by email")
        print("3.  Filter by group")
        print("4.  Navigate (pagination)")
        print("5.  Export to JSON")
        print("6.  Import from JSON")
        print("7.  Import from CSV")
        print("8.  Add phone (Procedure)")
        print("9.  Move to group (Procedure)")
        print("10. Add contact (manual)")
        print("0.  Exit")

        choice = input("> ").strip()
        if choice == '0':
            break  # выход из цикла = завершение программы
        elif choice in actions:
            actions[choice]()  # вызываем нужную функцию по ключу
        else:
            print("Invalid choice, try again.")


if __name__ == "__main__":
    main()  # запускаем только если файл запущен напрямую, не импортирован
