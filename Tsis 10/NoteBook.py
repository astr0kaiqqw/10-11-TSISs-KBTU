import psycopg2
import csv

conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="TaikpanovRus12",
    host="localhost",
    port="1501"
)
cur = conn.cursor()

def create_table():
    cur.execute("""
        CREATE TABLE IF NOT EXISTS PhoneBook (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100),
            phone VARCHAR(15)
        );
    """)
    conn.commit()


def insert_user(username, phone):
    cur.execute("INSERT INTO PhoneBook (username, phone) VALUES (%s, %s);", (username, phone))
    conn.commit()


def insert_from_csv(filename):
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        next(reader)  
        for row in reader:
            cur.execute("INSERT INTO PhoneBook (username, phone) VALUES (%s, %s);", (row[0], row[1]))
    conn.commit()


def update_user(old_username=None, old_phone=None, new_username=None, new_phone=None):
    if old_username:
        if new_username:
            cur.execute("UPDATE PhoneBook SET username = %s WHERE username = %s;", (new_username, old_username))
        if new_phone:
            cur.execute("UPDATE PhoneBook SET phone = %s WHERE username = %s;", (new_phone, old_username))
    elif old_phone:
        if new_username:
            cur.execute("UPDATE PhoneBook SET username = %s WHERE phone = %s;", (new_username, old_phone))
        if new_phone:
            cur.execute("UPDATE PhoneBook SET phone = %s WHERE phone = %s;", (new_phone, old_phone))
    conn.commit()


def query_data(filter_by=None, value=None):
    if filter_by == 'username':
        cur.execute("SELECT * FROM PhoneBook WHERE username = %s;", (value,))
    elif filter_by == 'phone':
        cur.execute("SELECT * FROM PhoneBook WHERE phone = %s;", (value,))
    else:
        cur.execute("SELECT * FROM PhoneBook;")
    rows = cur.fetchall()
    for row in rows:
        print(row)


def delete_user(username=None, phone=None):
    if username:
        cur.execute("DELETE FROM PhoneBook WHERE username = %s;", (username,))
    if phone:
        cur.execute("DELETE FROM PhoneBook WHERE phone = %s;", (phone,))
    conn.commit()


def close():
    cur.close()
    conn.close()


if __name__ == '__main__':
    create_table()

   
    insert_user("Alice", "123456789")
    insert_user("Bob", "987654321")

    
    update_user(old_username="Alice", new_phone="111111111")

    
    print("All entries:")
    query_data()
    print("Filtered by username = Bob:")
    query_data(filter_by='username', value='Bob')

    
    delete_user(username="Bob")


    print("After deletion:")
    query_data()

    close()
