from connect import get_connection

def show_rows(rows):
    # Print rows in console
    for row in rows:
        print(row)

def search_by_pattern(pattern):
    # Show matching rows here
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM search_phonebook(%s)", (pattern,))
    rows = cur.fetchall()
    show_rows(rows)
    cur.close()
    conn.close()

def add_or_update_user(name, surname, phone):
    # Use procedure for update
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("CALL insert_or_update_user(%s, %s, %s)", (name, surname, phone))
    conn.commit()
    cur.close()
    conn.close()

def add_many_users(names, surnames, phones):
    # Insert many users now
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("CALL insert_many_users(%s, %s, %s)", (names, surnames, phones))
    invalid_data = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return invalid_data[0] if invalid_data else None

def get_page(limit, offset):
    # Get page of data
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM paginate_phonebook(%s, %s)", (limit, offset))
    rows = cur.fetchall()
    show_rows(rows)
    cur.close()
    conn.close()

def delete_data(name=None, phone=None):
    # Delete rows by filter
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("CALL delete_phonebook_data(%s, %s)", (name, phone))
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    # Start simple menu here
    print("PhoneBook started")
