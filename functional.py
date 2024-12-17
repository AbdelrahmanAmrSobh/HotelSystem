from datetime import date
from mydb import *

# Functional helpers


def create_room(room_number, room_type, price):
    add_record("rooms", (room_number, room_type, price, True))
    return {
        "room_number": room_number,
        "room_type": room_type,
        "price": price,
        "available": True
    }


def create_customer(name, contact_info, payment_method):
    add_record("customers", (name, contact_info, payment_method))
    return {
        "name": name,
        "contact_info": contact_info,
        "payment_method": payment_method
    }


def create_reservation(customer, room, start_date, end_date):
    add_record("reservations", (customer.get("name"),
               room.get("room_number"), start_date, end_date))
    return {
        "customer": customer,
        "room": room,
        "start_date": start_date,
        "end_date": end_date,
        "checked_in": False,
        "checked_out": False
    }


def update_room_availability(rooms, room_number, available):
    update_record("rooms", f"available = {available}", room_number)
    return [
        {**room,
            "available": available} if room["room_number"] == room_number else room
        for room in rooms
    ]


def check_in_reservation(reservations, rooms, customer_name, room_number):
    update_record("reservations", f"checked_in = 1", room_number)
    updated_reservations = [
        {**res, "checked_in": True} if res["customer"]["name"] == customer_name
        and res["room"]["room_number"] == room_number
        and not res["checked_in"] else res
        for res in reservations
    ]
    updated_rooms = update_room_availability(rooms, room_number, False)
    return updated_reservations, updated_rooms


def check_out_reservation(reservations, rooms, customer_name, room_number):
    update_record("reservations", f"checked_out = 1", room_number)
    updated_reservations = [
        {**res, "checked_in": False, "checked_out": True} if res["customer"]["name"] == customer_name
        and res["room"]["room_number"] == room_number
        and res["checked_in"] else res
        for res in reservations
    ]
    updated_rooms = update_room_availability(rooms, room_number, True)
    return updated_reservations, updated_rooms


def calculate_bill(reservation):
    duration = (reservation["end_date"] - reservation["start_date"]).days
    total = duration * reservation["room"]["price"]
    return total


def generate_report(rooms, reservations, customers):
    occupied_rooms = sum(1 for r in rooms if not r["available"])
    total_revenue = sum(
        calculate_bill(res) for res in reservations if res["checked_in"] or res["checked_out"]
    )

    room_statuses = [
        {
            "room_number": r["room_number"],
            "status": (
                "Checked In" if any(res["room"]["room_number"] == r["room_number"] and res["checked_in"] for res in reservations)
                else "Reserved" if any(res["room"]["room_number"] == r["room_number"] and not res["checked_in"] for res in reservations)
                else "Available"
            ),
            "customer": next(
                (res["customer"]["name"] for res in reservations if res["room"]
                 ["room_number"] == r["room_number"] and res["checked_in"]),
                None
            ),
        }
        for r in rooms
    ]

    customer_details = [
        {
            "name": c["name"],
            "contact_info": c["contact_info"],
            "payment_method": c["payment_method"]
        }
        for c in customers
    ]

    return len(rooms), occupied_rooms, total_revenue, room_statuses, customer_details


# Functional pipeline for the system
def main():
    rooms, customers, reservations = get_records()
    while True:
        print("\nFunctional Hotel Management System")
        print("1. Add Room")
        print("2. Add Customer")
        print("3. Make Reservation")
        print("4. Check In")
        print("5. Check Out")
        print("6. Generate Report")
        print("7. Exit")

        choice = input("Choose an option: ")

        if choice == '1':
            room_number = int(input("Enter room number: "))
            room_type = input("Enter room type (Single/Double/Suite): ")
            price = float(input("Enter room price: "))
            room = create_room(room_number, room_type, price)
            rooms.append(room)
            print(f"Room {room_number} added.")

        elif choice == '2':
            name = input("Enter customer name: ")
            contact_info = input("Enter contact information: ")
            payment_method = input("Enter payment method: ")
            customer = create_customer(name, contact_info, payment_method)
            customers.append(customer)
            print(f"Customer {name} added.")

        elif choice == '3':
            customer_name = input("Enter customer name for reservation: ")
            room_number = int(input("Enter room number for reservation: "))
            start_date_str = input("Enter start date (YYYY-MM-DD): ")
            end_date_str = input("Enter end date (YYYY-MM-DD): ")
            start_date = date.fromisoformat(start_date_str)
            end_date = date.fromisoformat(end_date_str)

            customer = next(
                (c for c in customers if c["name"] == customer_name), None)
            room = next(
                (r for r in rooms if r["room_number"] == room_number and r["available"]), None)

            if customer and room:
                reservation = create_reservation(
                    customer, room, start_date, end_date)
                reservations.append(reservation)
                rooms = update_room_availability(rooms, room_number, False)
                print(f"Reservation made for {
                      customer_name} in room {room_number}.")
            else:
                print("Invalid customer or room.")

        elif choice == '4':
            customer_name = input("Enter customer name for check-in: ")
            room_number = int(input("Enter room number for check-in: "))

            updated_reservations, rooms = check_in_reservation(
                reservations, rooms, customer_name, room_number)
            reservations = updated_reservations
            print(f"{customer_name} checked in to room {room_number}.")

        elif choice == '5':
            customer_name = input("Enter customer name for check-out: ")
            room_number = int(input("Enter room number for check-out: "))

            updated_reservations, rooms = check_out_reservation(
                reservations, rooms, customer_name, room_number)
            reservations = updated_reservations
            bill = next((calculate_bill(
                res) for res in reservations if res["customer"]["name"] == customer_name and res["room"]["room_number"] == room_number), 0)
            print(f"Bill for {customer_name} for room {
                  room_number}: ${bill:.2f}")

        elif choice == '6':
            total_rooms, occupied_rooms, total_revenue, room_statuses, customer_details = generate_report(
                rooms, reservations, customers)

            print(f"Total Rooms: {total_rooms}")
            print(f"Occupied Rooms: {occupied_rooms}")
            print(f"Total Revenue: ${total_revenue:.2f}")

            print("\nRooms Status:")
            for room in room_statuses:
                print(
                    f"Room {room['room_number']}: {room['status']}" +
                    (f" (Customer: {room['customer']
                                    })" if room['customer'] else "")
                )

            print("\nCustomers in the System:")
            for customer in customer_details:
                print(
                    f"Name: {customer['name']}, Contact Info: {
                        customer['contact_info']}, "
                    f"Payment Method: {customer['payment_method']}"
                )

        elif choice == '7':
            print("Exiting the system. Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
