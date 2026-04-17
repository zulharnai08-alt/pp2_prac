from connect import get_connection


def print_rows(rows):
    # Show rows in console.
    if not rows:
        print("No data.")
        return

    for row in rows:
        print(row)


def search_phonebook(pattern):
    # Search by text.
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM search_phonebook(%s)", (pattern,))
            return cur.fetchall()


def paginate_phonebook(limit, offset):
    # Get one page.
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM paginate_phonebook(%s, %s)", (limit, offset))
            return cur.fetchall()


def upsert_user(name, phone, surname=None):
    # Save one user.
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "CALL upsert_phonebook_user(%s, %s, %s)",
                (name, phone, surname),
            )
        conn.commit()


def insert_many_users(names, phones, surnames=None):
    # Save many users.
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "CALL insert_many_phonebook_users(%s, %s, %s)",
                (names, phones, surnames),
            )
            cur.execute(
                "SELECT name, surname, phone, reason FROM invalid_phonebook_data"
            )
            bad_rows = cur.fetchall()
        conn.commit()
    return bad_rows


def delete_user(name=None, phone=None):
    # Delete one user.
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "CALL delete_phonebook_data(%s, %s)",
                (name, phone),
            )
        conn.commit()


def main():
    # Simple test menu.
    while True:
        print("\n1 Search")
        print("2 Page")
        print("3 Add or update")
        print("4 Add many")
        print("5 Delete")
        print("0 Exit")

        choice = input("Choose: ").strip()

        if choice == "1":
            pattern = input("Pattern: ").strip()
            rows = search_phonebook(pattern)
            print_rows(rows)

        elif choice == "2":
            limit = int(input("Limit: ").strip())
            offset = int(input("Offset: ").strip())
            rows = paginate_phonebook(limit, offset)
            print_rows(rows)

        elif choice == "3":
            name = input("Name: ").strip()
            phone = input("Phone: ").strip()
            surname = input("Surname or empty: ").strip() or None
            upsert_user(name, phone, surname)
            print("Done.")

        elif choice == "4":
            names = input("Names by comma: ").split(",")
            phones = input("Phones by comma: ").split(",")
            surnames_text = input("Surnames by comma or empty: ").strip()

            names = [x.strip() for x in names if x.strip()]
            phones = [x.strip() for x in phones if x.strip()]

            if surnames_text:
                surnames = [x.strip() for x in surnames_text.split(",")]
            else:
                surnames = None

            bad_rows = insert_many_users(names, phones, surnames)
            print("Bad rows:")
            print_rows(bad_rows)

        elif choice == "5":
            name = input("Name or empty: ").strip() or None
            phone = input("Phone or empty: ").strip() or None
            delete_user(name, phone)
            print("Done.")

        elif choice == "0":
            break

        else:
            print("Bad choice.")


if __name__ == "__main__":
    main()
