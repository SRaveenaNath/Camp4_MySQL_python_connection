import mysql.connector
import random
import string
import datetime

class HotelBookingSystem:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="faith",
            database="hotel_booking"
        )
        self.cursor = self.conn.cursor()
        self.cursor.execute("USE hotel_booking")  # Now, use the 'hotel_booking' database

    def create_tables(self):
        """Create tables for room categories and bookings"""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS rooms (
                room_id INT AUTO_INCREMENT PRIMARY KEY,
                room_no VARCHAR(10),
                category VARCHAR(50),
                rate_per_day FLOAT,
                status VARCHAR(20)
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                booking_id VARCHAR(10) PRIMARY KEY,
                room_id INT,
                customer_name VARCHAR(100),
                booking_date DATE,
                occupancy_date DATE,
                num_days INT,
                advance FLOAT,
                total_amount FLOAT,
                FOREIGN KEY (room_id) REFERENCES rooms(room_id)
            )
        """)
        self.conn.commit()

    def display_room_categories(self):
        """Display rooms category-wise with rates per day"""
        self.cursor.execute("SELECT category, room_no, rate_per_day FROM rooms ORDER BY category")
        rooms = self.cursor.fetchall()
        for room in rooms:
            print(f"Category: {room[0]}, Room No: {room[1]}, Rate per day: {room[2]}")

    def list_occupied_rooms(self):
        """List rooms occupied for the next two days"""
        self.cursor.execute("""
            SELECT r.category, r.room_no FROM bookings b
            JOIN rooms r ON b.room_id = r.room_id
            WHERE occupancy_date >= CURDATE() AND occupancy_date <= DATE_ADD(CURDATE(), INTERVAL 2 DAY)
        """)
        rooms = self.cursor.fetchall()
        for room in rooms:
            print(f"Occupied Room: Category - {room[0]}, Room No - {room[1]}")

    def display_rooms_by_rate(self):
        """Display rooms in increasing order of rate per day"""
        self.cursor.execute("SELECT room_no, category, rate_per_day FROM rooms ORDER BY rate_per_day ASC")
        rooms = self.cursor.fetchall()
        for room in rooms:
            print(f"Room No: {room[0]}, Category: {room[1]}, Rate per day: {room[2]}")

    def search_by_booking_id(self, booking_id):
        """Search for room details using booking ID"""
        self.cursor.execute("""
            SELECT b.booking_id, b.customer_name, r.room_no, r.category, b.booking_date, b.occupancy_date, b.num_days 
            FROM bookings b
            JOIN rooms r ON b.room_id = r.room_id
            WHERE b.booking_id = %s
        """, (booking_id,))
        booking = self.cursor.fetchone()
        if booking:
            print(f"Booking ID: {booking[0]}, Customer: {booking[1]}, Room No: {booking[2]}, "
                  f"Category: {booking[3]}, Booking Date: {booking[4]}, Occupancy Date: {booking[5]}, "
                  f"Number of Days: {booking[6]}")
        else:
            print("Booking not found.")

    def display_unoccupied_rooms(self):
        """Display unoccupied rooms"""
        self.cursor.execute("SELECT room_no, category FROM rooms WHERE status = 'Unoccupied'")
        rooms = self.cursor.fetchall()
        for room in rooms:
            print(f"Room No: {room[0]}, Category: {room[1]} is available.")

    def update_room_status(self, room_no):
        """Update room status to Unoccupied when a customer leaves"""
        self.cursor.execute("UPDATE rooms SET status = 'Unoccupied' WHERE room_no = %s", (room_no,))
        self.conn.commit()
        print(f"Room {room_no} is now unoccupied.")

    def prebook_room(self, room_no, customer_name, booking_date, occupancy_date, num_days, advance):
        """Prebook a room"""
        booking_id = self.generate_booking_id()
        self.cursor.execute("SELECT room_id, rate_per_day FROM rooms WHERE room_no = %s AND status = 'Unoccupied'",
                            (room_no,))
        room = self.cursor.fetchone()

        if room:
            room_id, rate_per_day = room
            total_amount = (rate_per_day * num_days) + (
                        rate_per_day * 0.18) + 100  # Example tax and housekeeping charges
            self.cursor.execute("""
                INSERT INTO bookings (booking_id, room_id, customer_name, booking_date, occupancy_date, num_days, advance, total_amount)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (booking_id, room_id, customer_name, booking_date, occupancy_date, num_days, advance, total_amount))
            self.cursor.execute("UPDATE rooms SET status = 'Occupied' WHERE room_id = %s", (room_id,))
            self.conn.commit()
            print(f"Room {room_no} prebooked for {customer_name} with Booking ID: {booking_id}")
        else:
            print("Room not available or already occupied.")

    def generate_booking_id(self):
        """Generate a 5-digit booking ID with 2 character prefix"""
        prefix = ''.join(random.choices(string.ascii_uppercase, k=2))
        digits = ''.join(random.choices(string.digits, k=3))
        return prefix + digits

    def close_connection(self):
        self.conn.close()


if __name__ == "__main__":
    hotel_system = HotelBookingSystem()
    hotel_system.create_tables()

    # Example menu-driven console
    while True:
        print("\n--- Hotel Booking System Menu ---")
        print("1. Display Rooms by Category and Rates")
        print("2. List Occupied Rooms for Next 2 Days")
        print("3. Display Rooms in Increasing Order of Rate")
        print("4. Search Room by Booking ID")
        print("5. Display Unoccupied Rooms")
        print("6. Prebook Room")
        print("7. Update Room to Unoccupied")
        print("8. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            hotel_system.display_room_categories()
        elif choice == "2":
            hotel_system.list_occupied_rooms()
        elif choice == "3":
            hotel_system.display_rooms_by_rate()
        elif choice == "4":
            booking_id = input("Enter Booking ID: ")
            hotel_system.search_by_booking_id(booking_id)
        elif choice == "5":
            hotel_system.display_unoccupied_rooms()
        elif choice == "6":
            room_no = input("Enter Room No: ")
            customer_name = input("Enter Customer Name: ")
            booking_date = input("Enter Booking Date (YYYY-MM-DD): ")
            occupancy_date = input("Enter Occupancy Date (YYYY-MM-DD): ")
            num_days = int(input("Enter Number of Days of Occupancy: "))
            advance = float(input("Enter Advance Amount: "))
            hotel_system.prebook_room(room_no, customer_name, booking_date, occupancy_date, num_days, advance)
        elif choice == "7":
            room_no = input("Enter Room No to update: ")
            hotel_system.update_room_status(room_no)
        elif choice == "8":
            hotel_system.close_connection()
            break
        else:
            print("Invalid choice. Please try again.")
