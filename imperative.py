from datetime import date
from mydb import *

# Class to represent a room in the hotel
class Room:
    def __init__(self, room_number, room_type, price):
        self.room_number = room_number  # Room number
        self.room_type = room_type      # Room type (e.g., Single, Double, Suite)
        self.price = price              # Price per night
        self.available = True           # Availability status

    # Mark room as booked
    def book(self):
        self.available = False

    # Release room after check-out
    def release(self):
        self.available = True

    # String representation for the Room object
    def __str__(self):
        return f"{self.room_number} is {self.room_type} for {self.price} a night"


# Class to represent a customer in the hotel
class Customer:
    def __init__(self, name, contact_info, payment_method):
        self.name = name                      # Customer's name
        self.contact_info = contact_info      # Contact information
        self.payment_method = payment_method  # Preferred payment method

    # String representation for the Customer object
    def __str__(self):
        return f"{self.name} {self.contact_info} {self.payment_method}"


# Class to represent a reservation in the hotel
class Reservation:
    def __init__(self, customer, room, start_date, end_date):
        self.customer = customer      # Customer who made the reservation
        self.room = room              # Room assigned to the reservation
        self.start_date = start_date  # Start date of the reservation
        self.end_date = end_date      # End date of the reservation
        self.checked_in = False       # Check-in status

    # Method to check-in the customer and mark room as booked
    def check_in(self):
        self.checked_in = True
        self.room.book()

    # Method to check-out the customer and release the room
    def check_out(self):
        self.checked_in = False
        self.room.release()

    # String representation for the Reservation object
    def __str__(self):
        return f"{self.room.room_number} is for {self.customer.name} from {self.start_date} to {self.end_date}"


# Class to handle billing for a reservation
class Billing:
    @staticmethod
    def generate_bill(reservation):
        # Calculate total cost based on duration of stay
        duration = (reservation.end_date - reservation.start_date).days
        total = duration * reservation.room.price
        return total


# Main system class for hotel management
class HotelManagementSystem:
    def __init__(self):
        self.rooms = []           # List of all rooms in the hotel
        self.customers = []       # List of all customers
        self.reservations = []    # List of all reservations

        # Fetch existing records from the database
        rooms, customers, reservations = get_records()

        # Initialize Room objects
        for room in rooms:
            newRoom = Room(
                room.get("room_number"),
                room.get("room_type"),
                room.get("price"),
            )
            if room.get("available") == False:
                newRoom.book()
            self.rooms.append(newRoom)

        # Initialize Customer objects
        for customer in customers:
            self.customers.append(
                Customer(
                    customer.get("name"),
                    customer.get("contact_info"),
                    customer.get("payment_method")
                )
            )

        # Initialize Reservation objects
        for reservation in reservations:
            reservation_customer = None
            for customer in self.customers:
                if customer.name == reservation.get("customer").get("name"):
                    reservation_customer = customer
                    break

            reservation_room = None
            for room in self.rooms:
                if room.room_number == reservation.get("room").get("room_number"):
                    reservation_room = room
                    break

            # Create reservation
            newReservation = Reservation(reservation_customer, reservation_room, reservation.get(
                "start_date"), reservation.get("end_date"))
            if reservation.get("checked_in"):
                newReservation.check_in()
            if reservation.get("checked_out"):
                newReservation.check_out()

            self.reservations.append(newReservation)

    # Add a new room to the system
    def add_room(self, room_number, room_type, price):
        add_record("rooms", (room_number, room_type, price, True))
        room = Room(room_number, room_type, price)
        self.rooms.append(room)
        print(f"Room {room_number} added.")

    # Add a new customer to the system
    def add_customer(self, name, contact_info, payment_method):
        add_record("customers", (name, contact_info, payment_method))
        customer = Customer(name, contact_info, payment_method)
        self.customers.append(customer)
        print(f"Customer {name} added.")
        return customer

    # Create a new reservation for a customer
    def make_reservation(self, customer, room, start_date, end_date):
        if room.available:  # Check room availability
            room.available = False
            add_record("reservations", (customer.name, room.room_number, start_date, end_date))
            update_record("rooms", f"available = {False}", room.room_number)
            reservation = Reservation(customer, room, start_date, end_date)
            self.reservations.append(reservation)
            room.book()
            print(f"Reservation made for {customer.name} in room {room.room_number}.")
            return reservation
        else:
            print(f"Room {room.room_number} is not available.")
            return None

    # Check-in a customer for an existing reservation
    def check_in(self, reservation):
        update_record("reservations", f"checked_in = 1", reservation.room.room_number)
        update_record("reservations", f"checked_out = 0", reservation.room.room_number)
        reservation.check_in()
        print(f"{reservation.customer.name} checked in to room {reservation.room.room_number}.")

    # Check-out a customer for an existing reservation
    def check_out(self, reservation):
        update_record("reservations", "checked_out = 1", reservation.room.room_number)
        update_record("rooms", "available = True", reservation.room.room_number)
        reservation.check_out()
        print(f"{reservation.customer.name} checked out of room {reservation.room.room_number}.")

    # Generate a report for occupancy and total revenue
    def generate_report(self):
        occupancy = sum(1 for r in self.rooms if not r.available)  # Count occupied rooms
        total_revenue = sum(Billing.generate_bill(res) for res in self.reservations)  # Calculate total revenue
        print(f"Total Rooms: {len(self.rooms)}, Occupied Rooms: {occupancy}, Total Revenue: ${total_revenue:.2f}")


def main():
    # Initialize the hotel management system
    hotel_system = HotelManagementSystem()

    # Menu-driven interface for user interaction
    while True:
        print("\nHotel Management System")
        print("1. Add Room")
        print("2. Add Customer")
        print("3. Make Reservation")
        print("4. Check In")
        print("5. Check Out")
        print("6. Generate Report")
        print("7. Exit")

        choice = input("Choose an option: ")

        if choice == '1':
            # Add a new room
            room_number = int(input("Enter room number: "))
            room_type = input("Enter room type (Single/Double/Suite): ")
            price = float(input("Enter room price: "))
            hotel_system.add_room(room_number, room_type, price)

        elif choice == '2':
            # Add a new customer
            name = input("Enter customer name: ")
            contact_info = input("Enter contact information: ")
            payment_method = input("Enter payment method: ")
            hotel_system.add_customer(name, contact_info, payment_method)

        elif choice == '3':
            # Make a reservation
            customer_name = input("Enter customer name for reservation: ")
            room_number = int(input("Enter room number for reservation: "))
            start_date_str = input("Enter start date (YYYY-MM-DD): ")
            end_date_str = input("Enter end date (YYYY-MM-DD): ")
            start_date = date.fromisoformat(start_date_str)
            end_date = date.fromisoformat(end_date_str)

            customer = next((c for c in hotel_system.customers if c.name == customer_name), None)
            room = next((r for r in hotel_system.rooms if r.room_number == room_number), None)

            if customer and room:
                hotel_system.make_reservation(customer, room, start_date, end_date)
            else:
                print("Invalid customer or room.")

        elif choice == '4':
            # Check-in a customer
            customer_name = input("Enter customer name for check-in: ")
            room_number = int(input("Enter room number for check-in: "))

            reservation = next((res for res in hotel_system.reservations
                                if res.customer.name == customer_name and
                                res.room.room_number == room_number and
                                not res.checked_in), None)

            if reservation:
                hotel_system.check_in(reservation)
            else:
                print("No valid reservation found for this customer and room.")

        elif choice == '5':
            # Check-out a customer
            customer_name = input("Enter customer name for check-out: ")
            room_number = int(input("Enter room number for check-out: "))

            reservation = next((res for res in hotel_system.reservations
                                if res.customer.name == customer_name and
                                res.room.room_number == room_number and
                                res.checked_in), None)

            if reservation:
                hotel_system.check_out(reservation)
                bill = Billing.generate_bill(reservation)
                print(f"Bill for {customer_name} for room {room_number}: ${bill:.2f}")
            else:
                print("No valid check-in found for this customer and room.")

        elif choice == '6':
            # Generate occupancy and revenue report
            hotel_system.generate_report()

        elif choice == '7':
            # Exit the system
            print("Exiting the system. Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
