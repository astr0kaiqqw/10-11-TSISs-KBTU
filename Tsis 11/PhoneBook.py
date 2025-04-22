import psycopg2
import csv






# ПОДКЛЮЧЕНИЕ К БАЗЕ 
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="TaikpanovRus12",
    host="localhost",
    port="1501"
)
cur = conn.cursor()

  


#СОЗДАЕМ ТАБЛИЦУ
def create_table():
    cur.execute("""
        CREATE TABLE IF NOT EXISTS PhoneBook (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100),
            phone VARCHAR(15)
        );
    """)
    conn.commit()




# Функция для добавления нового пользователя
def insert_user(username, phone):
    cur.execute("INSERT INTO PhoneBook (username, phone) VALUES (%s, %s);", (username, phone))
    conn.commit()




# Функция для обновления телефона пользователя
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




# Функция для запроса данных с фильтром
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




# Функция для удаления данных по имени или телефону   ПЯТЫЙ КРИТЕРИЙ !!!!
def delete_user(username=None, phone=None):
    if username:
        cur.execute("DELETE FROM PhoneBook WHERE username = %s;", (username,))
    elif phone:
        cur.execute("DELETE FROM PhoneBook WHERE phone = %s;", (phone,))
    conn.commit()




# Функция для поиска записей по шаблону    ПЕРВЫЙ КРИТЕРИЙ!!
def query_by_pattern(pattern):
    cur.execute("SELECT * FROM PhoneBook WHERE username LIKE %s OR phone LIKE %s;", (f"%{pattern}%", f"%{pattern}%"))
    rows = cur.fetchall()
    for row in rows:
        print(row)




# Функция для вставки нового или обновления пользователя    ВТОРОЙ КРИТЕРИЙ !!!!
def insert_or_update_user(username, phone):
    cur.execute("SELECT * FROM PhoneBook WHERE username = %s;", (username,))
    if cur.fetchone():  # Если пользователь уже существует, обновляем номер телефона
        cur.execute("UPDATE PhoneBook SET phone = %s WHERE username = %s;", (phone, username))
    else:
        cur.execute("INSERT INTO PhoneBook (username, phone) VALUES (%s, %s);", (username, phone))
    conn.commit()




# вставкa нескольких пользователей с проверкой правильности телефона    ТРЕТИЙ КРИТЕРИЙ !!!!
def insert_multiple_users(users):
    incorrect_data = []
    for username, phone in users:
        if len(phone) != 15 or not phone.isdigit():  #проверка корректности номера
            incorrect_data.append((username, phone))
        else:
            cur.execute("INSERT INTO PhoneBook (username, phone) VALUES (%s, %s);", (username, phone))
    conn.commit()
    if incorrect_data:
        print("Некорректные данные:")
        for data in incorrect_data:
            print(data)
    return incorrect_data




# Функция для пагинации   ЧЕТВЕРТЫЙ КРИТЕРИЙ !!!!
def query_with_pagination(limit, offset):
    cur.execute("SELECT * FROM PhoneBook LIMIT %s OFFSET %s;", (limit, offset))
    rows = cur.fetchall()
    for row in rows:
        print(row)

def close():
    cur.close()
    conn.close()

if __name__ == '__main__':
    create_table()

    # Примеры 
    insert_user("Alice", "123456789")
    insert_user("Bob", "987654321")

    # Обновление телефона пользователя
    update_user(old_username="Alice", new_phone="111111111")

    # Пример запроса с шаблоном
    print("Записи по шаблону 'Bob':")
    query_by_pattern('Bob')

    # Пример вставки/обновления пользователя
    insert_or_update_user("Charlie", "555555555")

    # Пример вставки нескольких пользователей с проверкой
    users = [("David", "123456789012345"), ("Eve", "wrongphone"), ("Frank", "987654321012345")]
    insert_multiple_users(users)

    # Пример пагинации
    print("Записи с пагинацией (limit=2, offset=0):")
    query_with_pagination(2, 0)

    # Удаление пользователя по имени
    delete_user(username="Bob")

    # Удаление пользователя по телефону
    delete_user(phone="987654321012345")

    # После удаления
    print("После удаления:")
    query_data()

    close()
 
