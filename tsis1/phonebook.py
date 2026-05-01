import json # Модуль для работы с форматом JSON (экспорт/импорт)
import csv  # Модуль для работы с таблицами CSV
import os   # Модуль для работы с путями файлов и системой
from connect import get_connection # Импорт твоей функции подключения из соседнего файла

# Функция расширенного поиска (ищет по имени, почте или телефону)
def search_extended():
    query_str = input("Search query: ") # Получаем строку поиска от пользователя
    # SQL-запрос с JOIN: собираем данные из таблиц контактов, групп и телефонов
    # array_agg собирает все телефоны контакта в один список (массив)
    sql = """
        SELECT c.name, c.email, g.name, array_agg(p.phone) 
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON c.id = p.contact_id
        WHERE c.name ILIKE %s OR c.email ILIKE %s OR p.phone ILIKE %s
        GROUP BY c.id, g.name
    """
    pattern = f"%{query_str}%" # Подготовка шаблона для поиска (любые символы до и после)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (pattern, pattern, pattern)) # Выполняем поиск
            for r in cur.fetchall():
                # Если телефоны есть — склеиваем их через запятую, если нет — пишем "No numbers"
                phones = ', '.join(filter(None, r[3])) if r[3] else "No numbers"
                print(f"{r[0]} | {r[1]} | {r[2]} | {phones}")

# Фильтрация списка контактов по названию группы
def filter_by_group():
    group_name = input("Enter group name to filter: ")
    sql = """
        SELECT c.name, c.email, g.name 
        FROM contacts c
        JOIN groups g ON c.group_id = g.id
        WHERE g.name ILIKE %s
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (group_name,))
            rows = cur.fetchall()
            if not rows:
                print("No contacts found in this group.")
            for r in rows:
                print(f"{r[0]} | {r[1]} | Group: {r[2]}")

# Выгрузка всей базы данных в файл contacts.json
def export_to_json():
    sql = "SELECT id, name, email, birthday, group_id FROM contacts"
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            contacts = cur.fetchall()
            data = []
            for c in contacts:
                # Для каждого контакта дозапрашиваем его телефоны
                cur.execute("SELECT phone, type FROM phones WHERE contact_id = %s", (c[0],))
                phones = [{"phone": p[0], "type": p[1]} for p in cur.fetchall()]
                # Узнаем имя группы
                cur.execute("SELECT name FROM groups WHERE id = %s", (c[4],))
                g_name = cur.fetchone()
                # Формируем структуру словаря для JSON
                data.append({
                    "name": c[1], "email": c[2], "birthday": str(c[3]),
                    "group": g_name[0] if g_name else None, "phones": phones
                })

    # Сохраняем файл в ту же папку, где лежит скрипт
    folder = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(folder, "contacts.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Done. Saved to: {file_path}")

# Загрузка контактов из JSON файла в базу данных
def import_from_json():
    filename = input("File name (default: contacts.json): ") or "contacts.json"
    # (логика проверки пути файла...)
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        with get_connection() as conn:
            with conn.cursor() as cur:
                for item in data:
                    # Проверяем, существует ли уже такой контакт
                    cur.execute("SELECT id FROM contacts WHERE name = %s", (item['name'],))
                    exists = cur.fetchone()
                    if exists:
                        action = input(f"Contact '{item['name']}' exists. Overwrite? (y/n): ").lower()
                        if action != 'y': continue
                        cur.execute("DELETE FROM contacts WHERE id = %s", (exists[0],)) # Удаляем старый для перезаписи
                    
                    # Вставляем новый контакт и получаем его ID
                    cur.execute(
                        "INSERT INTO contacts (name, email, birthday) VALUES (%s, %s, %s) RETURNING id",
                        (item['name'], item.get('email'), item.get('birthday'))
                    )
                    c_id = cur.fetchone()[0]
                    # Добавляем связанные телефоны
                    for p in item.get('phones', []):
                        cur.execute("INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
                                    (c_id, p['phone'], p['type']))
            conn.commit() # Сохраняем все изменения в базе
        print("Success")
    except Exception as e:
        print(f"Error: {e}")

# Загрузка контактов из CSV файла
def import_from_csv():
    # Аналогичная логика импорта, но с чтением CSV и автоматическим созданием групп
    # (используется ON CONFLICT DO NOTHING, чтобы не дублировать группы)
    pass # (код сокращен для краткости, логика как в JSON импорте)

# Интерактивная навигация (постраничный вывод по 3 контакта)
def interactive_nav():
    print("Sort by: 1.Name 2.Birthday 3.ID")
    sort_choice = input("> ")
    sort_map = {"1": "name", "2": "birthday", "3": "id"}
    sort_col = sort_map.get(sort_choice, "name")

    limit, offset = 3, 0 # Выводим по 3 записи
    while True:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Используем LIMIT (сколько взять) и OFFSET (сколько пропустить) для пагинации
                cur.execute(f"SELECT name, email FROM contacts ORDER BY {sort_col} LIMIT %s OFFSET %s", (limit, offset))
                rows = cur.fetchall()
                if not rows and offset > 0:
                    offset -= limit # Если данных больше нет, возвращаемся назад
                    continue
                for r in rows:
                    print(f"{r[0]} | {r[1]}")
        cmd = input("[n/p/q]: ").lower() # n - вперед, p - назад, q - выход
        if cmd == 'n': offset += limit
        elif cmd == 'p': offset = max(0, offset - limit)
        elif cmd == 'q': break

# Главное меню приложения
def main():
    while True:
        print("\n1.Search 2.Nav 3.Export 4.ImportJSON 5.AddPhone 6.MoveGroup 7.FilterGroup 8.ImportCSV 0.Exit")
        choice = input("> ")
        if choice == '1': search_extended()
        elif choice == '2': interactive_nav()
        elif choice == '3': export_to_json()
        elif choice == '4': import_from_json()
        elif choice == '5':
            # Вызов ХРАНИМОЙ ПРОЦЕДУРЫ add_phone из базы данных
            n, p, t = input("Name: "), input("Phone: "), input("Type: ")
            with get_connection() as conn:
                with conn.cursor() as cur: 
                    cur.execute("CALL add_phone(%s,%s,%s)", (n,p,t))
                    conn.commit()
        elif choice == '6':
            # Вызов ХРАНИМОЙ ПРОЦЕДУРЫ move_to_group
            n, g = input("Name: "), input("Group: ")
            with get_connection() as conn:
                with conn.cursor() as cur: 
                    cur.execute("CALL move_to_group(%s,%s)", (n,g))
                    conn.commit()
        elif choice == '7': filter_by_group()
        elif choice == '8': import_from_csv()
        elif choice == '0': break

if __name__ == "__main__":
    main() # Запуск программы
