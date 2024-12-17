from datetime import date
import mysql.connector


def connect_to_mysql():
    try:
        conn = mysql.connector.connect(
            user='root',
            password='admin',
            host='localhost'
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def create_database(cursor):
    try:
        cursor.execute("CREATE DATABASE IF NOT EXISTS hotelSystem")
        cursor.execute("USE hotelSystem")
    except mysql.connector.Error as err:
        print(f"Error creating database: {err}")

def create_tables(cursor):
    rooms_table = '''
    CREATE TABLE IF NOT EXISTS rooms (
        number INT PRIMARY KEY,
        type VARCHAR(50),
        price DECIMAL(10, 2),
        available BOOLEAN DEFAULT TRUE
    );
    '''
    
    customers_table = '''
    CREATE TABLE IF NOT EXISTS customers (
        name VARCHAR(100) PRIMARY KEY,
        contact_info VARCHAR(255),
        payment_method VARCHAR(50)
    );
    '''
    
    reservations_table = '''
    CREATE TABLE IF NOT EXISTS reservations (
        customer_name VARCHAR(100),
        room_number INT,
        start_date DATE,
        end_date DATE,
        checked_in BOOLEAN DEFAULT FALSE,
        checked_out BOOLEAN DEFAULT FALSE,
        PRIMARY KEY (customer_name, room_number, start_date),
        FOREIGN KEY (customer_name) REFERENCES customers(name) ON DELETE CASCADE,
        FOREIGN KEY (room_number) REFERENCES rooms(number) ON DELETE CASCADE
    );
    '''
    
    try:
        cursor.execute(rooms_table)
        cursor.execute(customers_table)
        cursor.execute(reservations_table)
    except mysql.connector.Error as err:
        print(f"Error creating tables: {err}")

def add_record(table, data):
    conn = connect_to_mysql()
    cursor = conn.cursor()
    create_database(cursor)
    create_tables(cursor)
    if table == 'rooms':
        query = "INSERT INTO rooms (number, type, price, available) VALUES (%s, %s, %s, %s)"
    elif table == 'customers':
        query = "INSERT INTO customers (name, contact_info, payment_method) VALUES (%s, %s, %s)"
    elif table == 'reservations':
        query = "INSERT INTO reservations (customer_name, room_number, start_date, end_date) VALUES (%s, %s, %s, %s)"
    try:
        cursor.execute(query, data)
        conn.commit()
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        print(f"Error adding record to {table}: {err}")

def remove_record(table, condition):
    conn = connect_to_mysql()
    cursor = conn.cursor()
    create_database(cursor)
    create_tables(cursor)
    try:
        if table == 'rooms':
            query = f"DELETE FROM rooms WHERE number = {condition}"
        elif table == 'customers':
            query = f"DELETE FROM customers WHERE name = '{condition}'"
        elif table == 'reservations':
            query = f"DELETE FROM reservations WHERE customer_name = '{condition}'"
        cursor.execute(query)
        conn.commit()
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        print(f"Error removing record from {table}: {err}")

def update_record(table, updates, condition):
    conn = connect_to_mysql()
    cursor = conn.cursor()
    create_database(cursor)
    create_tables(cursor)
    try:
        if table == 'rooms':
            query = f"UPDATE rooms SET {updates} WHERE number = {condition}"
        elif table == 'reservations':
            query = f"UPDATE reservations SET {updates} WHERE room_number = '{condition}'"
        cursor.execute(query)
        conn.commit()
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        print(f"Error updating record in {table}: {err}")

def get_records():
    conn = connect_to_mysql()
    cursor = conn.cursor()
    create_database(cursor)
    create_tables(cursor)
    try:
        cursor.execute("SELECT * FROM rooms")
        rooms_db = cursor.fetchall()
        cursor.execute("SELECT * FROM customers")
        customers_db = cursor.fetchall()
        cursor.execute("SELECT * FROM reservations")
        reservations_db = cursor.fetchall()

        rooms = []
        customers = []
        reservations = []

        for room_db in rooms_db:
            rooms.append(
                {
                    "room_number": int(room_db[0]),
                    "room_type": str(room_db[1]),
                    "price": float(room_db[2]),
                    "available": bool(room_db[3])
                }
            )
        for customer_db in customers_db:
            customers.append(
                {
                    "name": str(customer_db[0]),
                    "contact_info": str(customer_db[1]),
                    "payment_method": str(customer_db[2])
                }
            )
        for reservation_db in reservations_db:
            customer_name = str(reservation_db[0])
            room_number = int(reservation_db[1])
            start_date = date.fromisoformat(str(reservation_db[2]))
            end_date = date.fromisoformat(str(reservation_db[3]))
            checked_in = bool(reservation_db[4])
            checked_out = bool(reservation_db[5])
            reservation_room = None
            reservation_customer = None
            for room in rooms:
                if room.get("room_number") == room_number:
                    reservation_room = room
                    break
            for customer in customers:
                if customer.get("name") == customer_name:
                    reservation_customer = customer
                    break
            reservations.append(
                {
                    "customer": reservation_customer,
                    "room": reservation_room,
                    "start_date": start_date,
                    "end_date": end_date,
                    "checked_in": checked_in,
                    "checked_out": checked_out
                }
            )
        cursor.close()
        conn.close()
        return rooms, customers, reservations
    except mysql.connector.Error as err:
        print(f"Error getting records: {err}")
