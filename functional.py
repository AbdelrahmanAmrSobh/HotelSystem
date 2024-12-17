from datetime import date
from functools import reduce
from mydb import *

# ============================================================
# Helper Functions for CRUD and Business Logic
# ============================================================

# Create a room and add it to the database
def create_room(room_number, room_type, price):
    """Creates and adds a room to the database."""
    add_record("rooms", (room_number, room_type, price, True))
    return {"room_number": room_number, "room_type": room_type, "price": price, "available": True}


# Add a new customer to the database
def create_customer(name, contact_info, payment_method):
    """Adds a new customer to the database."""
    add_record("customers", (name, contact_info, payment_method))
    return {"name": name, "contact_info": contact_info, "payment_method": payment_method}


# Handle the creation of a reservation
def create_reservation(customer, room, start_date, end_date):
    """Creates a reservation and ensures the room is unavailable."""
    add_record("reservations", (customer["name"], room["room_number"], start_date, end_date))
    return {
        "customer": customer,
        "room": room,
        "start_date": start_date,
        "end_date": end_date,
        "checked_in": False,
        "checked_out": False,
    }


# Mark a room as available/unavailable
def update_room_availability(rooms, room_number, available):
    update_record("rooms", f"available = {available}", room_number)
    """Updates room availability recursively without mutation."""
    if not rooms:
        return []
    head, tail = rooms[0], rooms[1:]
    if head["room_number"] == room_number:
        head = {**head, "available": available}
    return [head] + update_room_availability(tail, room_number, available)


# Handle Check-In logic safely without side-effects
def check_in_reservation(reservations, rooms, customer_name, room_number):
    update_record("reservations", f"checked_in = 1", room_number)
    """Check in a reservation only if not already checked in."""
    updated_reservations = [
        {**res, "checked_in": True} if res["customer"]["name"] == customer_name and res["room"]["room_number"] == room_number and not res["checked_in"] else res
        for res in reservations
    ]
    updated_rooms = update_room_availability(rooms, room_number, False)
    return updated_reservations, updated_rooms


# Handle Check-Out logic only if already checked in
def check_out_reservation(reservations, rooms, customer_name, room_number):
    """Checks out only if a reservation has been checked in."""
    reservation_to_checkout = next(
        (res for res in reservations if res["customer"]["name"] == customer_name and res["room"]["room_number"] == room_number and res["checked_in"]),
        None
    )

    if reservation_to_checkout:
        updated_reservations = [
            {**res, "checked_out": True} if res["customer"]["name"] == customer_name and res["room"]["room_number"] == room_number and res["checked_in"] else res
            for res in reservations
        ]
        updated_rooms = update_room_availability(rooms, room_number, True)
        bill = calculate_bill(reservation_to_checkout)
        update_record("reservations", "checked_out = 1", room_number)
        return updated_reservations, updated_rooms, bill
    else:
        print("Customer has not checked in or invalid reservation.")
        return reservations, rooms, 0


# Calculate a bill based on stay duration
def calculate_bill(reservation):
    """Calculates the total cost based on days of stay."""
    duration = (reservation["end_date"] - reservation["start_date"]).days
    return duration * reservation["room"]["price"]


# Report Generation
def generate_report(rooms, reservations, customers):
    """Generates a report showing occupancy, revenue, and statuses."""
    occupied_rooms = reduce(lambda acc, r: acc + (0 if r["available"] else 1), rooms, 0)
    total_revenue = reduce(
        lambda acc, res: acc + calculate_bill(res) if res["checked_in"] or res["checked_out"] else acc,
        reservations,
        0
    )

    print(f"Total Rooms: {len(rooms)}")
    print(f"Occupied Rooms: {occupied_rooms}")
    print(f"Total Revenue: ${total_revenue:.2f}")

    for room_status in rooms:
        print(
            f"Room {room_status['room_number']} - Status: {'Available' if room_status['available'] else 'Occupied'}"
        )
    return rooms, reservations, customers


# ============================================================
# Menu Logic with Recursion
# ============================================================

def menu_system(rooms, customers, reservations):
    """Main menu system using recursion and functional programming principles."""
    print("\nWelcome to the Functional Hotel Management System")
    print("1. Add Room")
    print("2. Add Customer")
    print("3. Make Reservation")
    print("4. Check In")
    print("5. Check Out")
    print("6. Generate Report")
    print("7. Exit")
    choice = input("Choose an option: ")

    # Handle user choice immutably and recursively
    if choice == '1':  # Add Room
        print("\nAdd Room")
        room_number = int(input("Enter room number: "))
        room_type = input("Enter room type (Single/Double/Suite): ")
        price = float(input("Enter room price: "))
        new_room = create_room(room_number, room_type, price)
        # Recursively call menu with the new room added
        return menu_system(rooms + [new_room], customers, reservations)

    elif choice == '2':  # Add Customer
        print("\nAdd Customer")
        name = input("Enter customer name: ")
        contact_info = input("Enter contact information: ")
        payment_method = input("Enter payment method: ")
        new_customer = create_customer(name, contact_info, payment_method)
        # Recursively call menu with the new customer added
        return menu_system(rooms, customers + [new_customer], reservations)

    elif choice == '3':  # Make Reservation
        print("\nMake Reservation")
        customer_name = input("Enter customer name for reservation: ")
        room_number = int(input("Enter room number for reservation: "))
        start_date = date.fromisoformat(input("Enter start date (YYYY-MM-DD): "))
        end_date = date.fromisoformat(input("Enter end date (YYYY-MM-DD): "))

        # Locate customer and room
        customer = next((c for c in customers if c["name"] == customer_name), None)
        room = next((r for r in rooms if r["room_number"] == room_number and r["available"]), None)

        if customer and room:
            new_reservation = create_reservation(customer, room, start_date, end_date)
            updated_rooms = update_room_availability(rooms, room_number, False)
            # Recursively call menu with updated rooms and new reservation
            return menu_system(updated_rooms, customers, reservations + [new_reservation])
        else:
            print("Invalid customer or room.")
            # Return to menu without changes if invalid
            return menu_system(rooms, customers, reservations)

    elif choice == '4':  # Check-In
        print("\nCheck-In")
        customer_name = input("Enter customer name for check-in: ")
        room_number = int(input("Enter room number to check in to: "))
        updated_reservations, updated_rooms = check_in_reservation(
            reservations, rooms, customer_name, room_number
        )
        return menu_system(updated_rooms, customers, updated_reservations)

    elif choice == '5':  # Check-Out
        print("\nCheck-Out")
        customer_name = input("Enter customer name for check-out: ")
        room_number = int(input("Enter room number to check out from: "))
        updated_reservations, updated_rooms, bill = check_out_reservation(
            reservations, rooms, customer_name, room_number
        )
        if bill > 0:
            print(f"Bill for stay: ${bill:.2f}")
        return menu_system(updated_rooms, customers, updated_reservations)

    elif choice == '6':  # Generate Report
        print("\nGenerating report...")
        rooms, reservations, customers = generate_report(rooms, reservations, customers)
        return menu_system(rooms, customers, reservations)

    elif choice == '7':  # Exit the program
        print("Exiting system. Goodbye!")
        return

    else:
        print("\nInvalid choice, please try again.")
        # Call the menu system recursively to retry invalid input
        return menu_system(rooms, customers, reservations)



# ============================================================
# Entry Point
# ============================================================

def main():
    rooms, customers, reservations = get_records()
    menu_system(rooms, customers, reservations)


if __name__ == "__main__":
    main()
