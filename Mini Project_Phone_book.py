import mysql.connector
from tabulate import tabulate
import re
import hashlib
import datetime

# Database connection
databaseobj = mysql.connector.connect(
    host='localhost',
    user='root',
    password='faith',
    database='PhoneBookDb'
)

cursor = databaseobj.cursor()

# Create the Users and Contacts tables if they don't exist

cursor.execute("""
    CREATE TABLE IF NOT EXISTS Users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(100) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS Contacts (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        phone_number VARCHAR(15) NOT NULL UNIQUE,
        address VARCHAR(255),
        email VARCHAR(100) UNIQUE,
        user_id INT,
        FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS UserLogs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        action VARCHAR(255),
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
    )
""")


# Helper function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# Function to register a new user
def register():
    while True:
        username = input("Enter a username: ")
        if re.fullmatch(r'[A-Za-z0-9_]{1,100}', username):
            cursor.execute("SELECT * FROM Users WHERE username=%s", (username,))
            if cursor.fetchone():
                print("Username already exists! Please choose another.")
            else:
                break
        else:
            print("Invalid username! Only letters, numbers, and underscores are allowed, and it must be between 1 and 100 characters.")

    while True:
        password = input("Enter a password: ")
        if len(password) >= 8:
            hashed_password = hash_password(password)
            break
        else:
            print("Password must be at least 8 characters long.")

    cursor.execute("INSERT INTO Users (username, password) VALUES (%s, %s)", (username, hashed_password))
    databaseobj.commit()
    print("User registered successfully.")


# Function to log user actions
def log_action(user_id, action):
    cursor.execute("INSERT INTO UserLogs (user_id, action) VALUES (%s, %s)", (user_id, action))
    databaseobj.commit()


# Function to log in an existing user
def login():
    while True:
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        hashed_password = hash_password(password)
        cursor.execute("SELECT id FROM Users WHERE username=%s AND password=%s", (username, hashed_password))
        user = cursor.fetchone()
        if user:
            print(f"Login successful. Welcome to Phone Book, {username}!")
            log_action(user[0], "Login")
            return user[0]
        else:
            print("Invalid username or password. Please try again.")


# Function to list all contacts for a user
def list_contacts(user_id):
    cursor.execute("SELECT id, name, phone_number, address, email FROM Contacts WHERE user_id=%s ORDER BY name", (user_id,))
    contacts = cursor.fetchall()
    if contacts:
        print(tabulate(contacts, headers=["ID", "Name", "Phone Number", "Address", "Email"]))
    else:
        print("No contacts found.")



# Function to add a new contact for a user
def add_contact(user_id):
    while True:
        name = input("Enter the contact's name: ")
        if re.fullmatch(r'[A-Za-z\s]{1,100}', name):
            break
        else:
            print("Invalid name! Only letters and spaces are allowed, and the name must be between 1 and 100 characters.")

    while True:
        phone_number = input("Enter the contact's phone number: ")
        if re.fullmatch(r'\+?\d{10,15}', phone_number):
            break
        else:
            print("Invalid phone number! It must be between 10 and 15 digits long. You can optionally include a leading '+'.")

    while True:
        address = input("Enter the contact's address: ")
        if len(address) <= 200:
            break
        else:
            print("Invalid address! It must be up to 200 characters long.")

    while True:
        email = input("Enter the contact's email: ")
        if re.fullmatch(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', email):
            break
        else:
            print("Invalid email format!")

    try:
        cursor.execute("INSERT INTO Contacts (name, phone_number, address, email, user_id) VALUES (%s, %s, %s, %s, %s)",
                       (name, phone_number, address, email, user_id))
        databaseobj.commit()
        log_action(user_id, f"Added contact: {name}")
        print("Contact added successfully.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")


# Function to delete a contact for a user
def delete_contact(user_id):
    while True:
        contact_id = input("Enter the ID of the contact to delete: ")
        if contact_id.isdigit():
            contact_id = int(contact_id)
            cursor.execute("SELECT * FROM Contacts WHERE id=%s AND user_id=%s", (contact_id, user_id))
            contact = cursor.fetchone()
            if contact:
                print(f"Contact to delete: ID={contact[0]}, Name={contact[1]}, Phone Number={contact[2]}")
                while True:
                    confirm = input("Are you sure you want to delete this contact? (yes/no): ").lower()
                    if confirm == "yes":
                        cursor.execute("DELETE FROM Contacts WHERE id=%s AND user_id=%s", (contact_id, user_id))
                        databaseobj.commit()
                        log_action(user_id, f"Deleted contact: {contact[1]}")
                        print("Contact deleted successfully.")
                        return
                    elif confirm == "no":
                        return
                    else:
                        print("Invalid input! Please enter 'yes' or 'no'.")
            else:
                print("Contact ID not found.")
        else:
            print("Invalid ID! Please enter a numeric ID.")


# Function to search contacts by name for a user
def search_by_name(user_id):
    while True:
        name = input("Enter the name to search for: ")
        cursor.execute("SELECT * FROM Contacts WHERE name LIKE %s AND user_id=%s ORDER BY name", ('%' + name + '%', user_id))
        contacts = cursor.fetchall()
        if contacts:
            print(tabulate(contacts, headers=["ID", "Name", "Phone Number", "Address", "Email"]))
        else:
            print("No contacts found with that name.")
        return


# Function to search contacts by phone number for a user
def search_by_number(user_id):
    while True:
        phone_number = input("Enter the phone number to search for: ")
        cursor.execute("SELECT * FROM Contacts WHERE phone_number=%s AND user_id=%s", (phone_number, user_id))
        contact = cursor.fetchone()
        if contact:
            print(tabulate([contact], headers=["ID", "Name", "Phone Number", "Address", "Email"]))
        else:
            print("No contact found with that phone number.")
        return


# Function for the main menu after login
def main_menu(user_id):
    while True:
        print("""
        Phone Book Menu:
        1. List all contacts
        2. Add a new contact
        3. Delete a contact
        4. Search by name
        5. Search by phone number
        6. Logout
        7. Exit""")
        choice = input("Enter your choice: ")
        if choice == "1":
            list_contacts(user_id)
        elif choice == "2":
            add_contact(user_id)
        elif choice == "3":
            delete_contact(user_id)
        elif choice == "4":
            search_by_name(user_id)
        elif choice == "5":
            search_by_number(user_id)
        elif choice == "6":
            log_action(user_id, "Logout")
            print("Logging out...")
            break
        elif choice == "7":
            log_action(user_id, "Exit")
            print("Exiting the phone book.")
            exit()
        else:
            print("Invalid choice! Please enter a number between 1 and 7.")


# Function for the initial menu (login, register, exit)
def initial_menu():
    while True:
        print("""
        Welcome to the Phone Book:
        1. Register
        2. Login
        3. Exit""")
        choice = input("Enter your choice: ")
        if choice == "1":
            register()
        elif choice == "2":
            user_id = login()
            if user_id:
                main_menu(user_id)
        elif choice == "3":
            print("Exiting phone book")
            exit()
        else:
            print("Invalid choice! Please enter a number between 1 and 3.")


if __name__ == "__main__":
    initial_menu()
