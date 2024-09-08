import mysql.connector
from datetime import datetime, timedelta
import re
import time

# Connect to MySQL database
db = mysql.connector.connect(
    host='localhost',
    user='root',
    password='faith',
    database="LibraryManagementSystem"
)
cursor = db.cursor()


# Email validation function
def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None


# Password strength validation function
def is_strong_password(password):
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    if not re.search(r'[\W_]', password):
        return False
    return True


# Consolidated view plans function
def view_plans():
    cursor.execute("SELECT * FROM membership_plans")
    plans = cursor.fetchall()

    print("\nAvailable Membership Plans:")
    for plan in plans:
        print(f"Plan ID: {plan[0]}, Name: {plan[1]}, Duration: {plan[2]} days, Price: Rs{plan[3]}")


def is_valid_account_number(account_number):
    return re.match(r'^\d{10,15}$', account_number) is not None
def is_valid_expiry_date(expiry_date):
    try:
        expiry_date = datetime.strptime(expiry_date, '%m/%y')
        return expiry_date > datetime.now()
    except ValueError:
        return False
def is_valid_cvv(cvv):
    return re.match(r'^\d{3}$', cvv) is not None
def process_payment(amount):
    print(f"Processing payment of Rs{amount}...")

    # Collect and validate account number
    while True:
        account_number = input("Enter your account number (10-15 digits): ")
        if is_valid_account_number(account_number):
            break
        print("Invalid account number. It should be 10 to 15 digits long.")

    # Collect and validate card expiry date
    while True:
        card_expiry_date = input("Enter your card expiry date (MM/YY): ")
        if is_valid_expiry_date(card_expiry_date):
            break
        print("Invalid expiry date. It should be in MM/YY format and not expired.")

    # Collect and validate CVV
    while True:
        cvv = input("Enter your CVV (3 digits): ")
        if is_valid_cvv(cvv):
            break
        print("Invalid CVV. It should be exactly 3 digits long.")

    # Simulating payment processing
    print("Processing payment details...")
    # Add additional payment validation or processing logic here if needed

    print("Payment successful!")
    return True


def view_plans2():
    cursor.execute("SELECT * FROM membership_plans")
    plans = cursor.fetchall()

    for plan in plans:
        print(f"Plan ID: {plan[0]}, Name: {plan[1]}, Duration: {plan[2]} days, Price: Rs{plan[3]}")


# Purchase membership plan
def purchase_membership(user):
    view_plans2()
    plan_id = int(input("Enter the Plan ID to purchase: "))
    cursor.execute("SELECT plan_price FROM membership_plans WHERE plan_id=%s", (plan_id,))
    plan = cursor.fetchone()

    if plan and process_payment(plan[0]):
        cursor.execute("UPDATE users SET membership_plan_id=%s WHERE user_id=%s", (plan_id, user[0]))
        db.commit()
        print("Membership plan added successfully!")
    else:
        print("Invalid plan ID or payment failed.")


# User Registration


def register_user():
    # Validation functions
    def is_valid_name(name):
        return name.replace(" ", "").isalpha()

    def is_valid_phone_number(phone):
        return re.match(r'^[789]\d{9}$', phone) is not None

    def is_valid_username(username):
        return username[0].isupper() and username.isalpha()

    def is_valid_email(email):
        return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email) is not None

    def is_strong_password(password):
        return (len(password) >= 8 and
                re.search(r'[A-Z]', password) and
                re.search(r'[a-z]', password) and
                re.search(r'\d', password) and
                re.search(r'[!@#$%^&*(),.?":{}|<>]', password))

    # Input and validation with re-prompting
    while True:
        first_name = input("Enter first name: ")
        if not is_valid_name(first_name):
            print("First name must contain only letters.")
        else:
            break

    while True:
        last_name = input("Enter last name: ")
        if not is_valid_name(last_name):
            print("Last name must contain only letters and spaces.")
        else:
            break

    while True:
        email = input("Enter email: ")
        if not is_valid_email(email):
            print("Invalid email format.")
        else:
            # Check if email already exists
            cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
            if cursor.fetchone():
                print("Email already exists in users.")
            else:
                break

    while True:
        phone_number = input("Enter phone number: ")
        if not is_valid_phone_number(phone_number):
            print("Phone number must be 10 digits long and start with 9, 8, or 7.")
        else:
            break

    while True:
        username = input("Create username: ")
        if not is_valid_username(username):
            print("Username must contain only letters and the first letter must be capital.")
        else:
            # Check if username already exists
            cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
            if cursor.fetchone():
                print("Username already exists in users.")
            else:
                break

    while True:
        password = input("Create password: ")
        if not is_strong_password(password):
            print("Password must be at least 8 characters long, include an uppercase letter, a lowercase letter, a number, and a special character.")
        else:
            break

    # Insert user into the database
    try:
        cursor.execute(
            "INSERT INTO users (first_name, last_name, email, phone_number, username, password) VALUES (%s, %s, %s, %s, %s, %s)",
            (first_name, last_name, email, phone_number, username, password)
        )
        db.commit()
        print("Registration successful.")
    except mysql.connector.errors.IntegrityError as e:
        print(f"Failed to register user: {e}")
        return

    # Execute purchase_membership function after successful registration
    purchase_membership((cursor.lastrowid,))  # Passing user ID as tuple
    login()

# User Login
def login():
    attempt_count = 0  # Counter for failed login attempts

    while attempt_count < 3:
        username = input("Enter username: ")
        password = input("Enter password: ")

        # Check in the users table
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()

        if user:
            print(f"Welcome User, {username}!")
            user_menu(user)  # Assuming user[0] is user_id
            return  # Exit the function after successful login
        else:
            # Check in the admins table if not found in users
            cursor.execute("SELECT * FROM admins WHERE username=%s AND password=%s", (username, password))
            admin = cursor.fetchone()

            if admin:
                print(f"Welcome, Admin {username}!")
                admin_menu(admin)  # Assuming admin[0] is admin_id
                return  # Exit the function after successful login
            else:
                attempt_count += 1
                print("Invalid username or password.")

                if attempt_count == 3:
                    print("Too many failed attempts. Please try again after 15 seconds.")
                    time.sleep(15)  # Lock out for 15 seconds
                    attempt_count = 0  # Reset the attempt counter


# Now you can call login() to start the login process
                    login()


# Admin Menu
def admin_menu(admin_user):
    while True:
        print("\nAdmin Menu")
        print("1. Manage Users")
        print("2. Manage Books")
        print("3. Manage Membership Plans")
        print("4. View Borrowed Books")
        # print("5. Manage Fines")
        print("5. View Reviews")
        print("6. Send Notifications")
        print("7. Exit")

        choice = input("Enter choice: ")

        if choice == '1':
            manage_users()
        elif choice == '2':
            manage_books()
        elif choice == '3':
            manage_membership_plans()
        elif choice == '4':
            view_borrowed_books()
        # elif choice == '5':
        #      manage_fines()
        elif choice == '5':
            view_and_comment_reviews()
        elif choice =='6':
            send_notifications(admin=None)
        elif choice == '7':
            print("Exiting admin menu...")
            return main()# Return to the main menu or exit
        else:
            print("Invalid choice. Please try again.")


def view_books2():
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()

    if books:
        print("\nAvailable Books:")
        for book in books:
            print(f"Book ID: {book[0]}")
            print(f"Title: {book[1]}")
            print(f"Author: {book[2]}")
            print(f"Genre: {book[3]}")
            print(f"Available Copies: {book[4]}")
            print(f"Price: Rs{book[5]}")
            print("-" * 40)
        return user_menu(user=None)
    else:
        print("No books found.")
        return user_menu(user=None)


# User Menu
def user_menu(user):
    """Display the user menu."""
    if user is None:
        print(" ")
        return  # Exit the function or redirect to login

    while True:

        print("\nUser Menu")
        print("1. View Notifications")
        print("2. Borrow Books")
        print("3. Search Books")
        print("4. View Books")
        print("5. Submit Reviews")
        print("6. View Borrowing History")
        # print("7. View Fines")
        print("7. Update Profile")
        print("8. LogOut")

        choice = input("Enter choice: ").strip()
        if choice == '1':
            view_notifications(user)
        if choice == '2':
            borrow_books(user)
        elif choice == '3':
            search_books(user)
        elif choice == '4':
            view_books2()
        elif choice == '5':
            submit_reviews(user)
        elif choice == '6':
            view_borrowing_history(user)
        # elif choice == '7':
        #     view_fines(user)
        elif choice =='7':
            update_user()
        elif choice == '8':
            return main()
        else:
            print("Invalid choice. Please try again.")


def view_users():
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    if users:
        print("\nRegistered Users:")
        for user in users:
            print(f"User ID: {user[0]}")
            print(f"First Name: {user[1]}")
            print(f"Last Name: {user[2]}")
            print(f"Email: {user[3]}")
            print(f"Phone Number: {user[4]}")
            print(f"Username: {user[5]}")
            print("-" * 40)

    else:
        print("No users found.")

    return manage_users()  # Return to User Management menu after displaying all users


# Function to search a specific user's details (Admin)
def search_user():
    user_id = int(input("Enter User ID to view: "))

    cursor.execute("SELECT * FROM users WHERE user_id=%s", (user_id,))
    user = cursor.fetchone()

    if user:
        print(f"User ID: {user[0]}")
        print(f"First Name: {user[1]}")
        print(f"Last Name: {user[2]}")
        print(f"Email: {user[3]}")
        print(f"Phone Number: {user[4]}")
        print(f"Username: {user[5]}")
        return manage_users()
        # You might also want to include additional information, such as borrowing history
    else:
        print(f"User with ID {user_id} does not exist.")
        return search_user()


# Function to delete a user (Admin)
def delete_user():
    try:
        user_id = int(input("Enter User ID to delete: "))

        # Check if the user exists
        cursor.execute("SELECT * FROM users WHERE user_id=%s", (user_id,))
        user = cursor.fetchone()

        if user:
            # Delete related data (e.g., notifications, reviews, borrowed books)
            cursor.execute("DELETE FROM notifications WHERE user_id=%s", (user_id,))
            cursor.execute("DELETE FROM reviews WHERE user_id=%s", (user_id,))
            cursor.execute("DELETE FROM borrowed_books WHERE user_id=%s", (user_id,))

            # Now delete the user
            cursor.execute("DELETE FROM users WHERE user_id=%s", (user_id,))
            db.commit()
            print(f"User with ID {user_id} has been deleted successfully.")
        else:
            print(f"User with ID {user_id} does not exist.")

        return manage_users()

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        db.rollback()  # Roll back any changes if there's an error

    return manage_users()


# Function to update a user (Admin)
def update_user():
    user_id = int(input("Enter User ID to update: "))

    # Fetch current user details
    cursor.execute("SELECT * FROM users WHERE user_id=%s", (user_id,))
    user = cursor.fetchone()

    if user:
        print(f"Current details: First Name: {user[1]}, Last Name: {user[2]}, Username: {user[5]}")

        # Collect new details from the admin
        new_first_name = input("Enter new first name (press Enter to keep current): ") or user[1]
        new_last_name = input("Enter new last name (press Enter to keep current): ") or user[2]
        new_username = input("Enter new username (press Enter to keep current): ") or user[5]

        # Check if the new username is already taken
        if new_username != user[5]:
            cursor.execute("SELECT * FROM users WHERE username=%s", (new_username,))
            if cursor.fetchone():
                print("Username already exists. Please choose a different username.")
                return

        # Update user details
        cursor.execute("""
            UPDATE users 
            SET first_name=%s, last_name=%s, username=%s 
            WHERE user_id=%s
        """, (new_first_name, new_last_name, new_username, user_id))
        db.commit()
        print("User details updated successfully.")
        return user_menu(user=None)
    else:
        print(f"User with ID {user_id} does not exist.")
        update_user()


# Placeholder Functions for Admin and User Management
def manage_users():
    print("\nUser Management")
    print("1. View Users")
    print("2. Search User")
    print("3. Exit")
    choice = input("Enter choice: ")
    if choice == '1':
        view_users()
    elif choice == '2':
        search_user()
    elif choice == '3':
        admin_menu(admin_user=None)
    else:
        print("Invalid Choice!Try Again")
        return manage_users()


def view_books():
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()

    if books:
        print("\nAvailable Books:")
        for book in books:
            print(f"Book ID: {book[0]}")
            print(f"Title: {book[1]}")
            print(f"Author: {book[2]}")
            print(f"Genre: {book[3]}")
            print(f"Available Copies: {book[4]}")
            print(f"Price: Rs{book[5]}")
            print("-" * 40)
        return manage_books()
    else:
        print("No books found.")
        return manage_books()


def add_book():
    title = input("Enter book title: ")
    author = input("Enter book author: ")
    genre = input("Enter book genre: ")
    price = float(input("Enter book price: "))
    available_copies = int(input("Enter number of available copies: "))

    cursor.execute("INSERT INTO books (title, author, genre, available_copies, price) VALUES (%s, %s, %s, %s, %s)",
                   (title, author, genre, available_copies, price))
    db.commit()
    print("Book added successfully.")
    return manage_books()


def delete_book():
    book_id = int(input("Enter book ID to delete: "))

    # Check if the book exists
    cursor.execute("SELECT * FROM books WHERE book_id=%s", (book_id,))
    book = cursor.fetchone()

    if book:
        cursor.execute("DELETE FROM borrowed_books WHERE book_id=%s", (book_id,))
        cursor.execute("DELETE FROM books WHERE book_id=%s", (book_id,))
        db.commit()
        print(f"Book with ID {book_id} has been deleted successfully.")
        return manage_books()
    else:
        print(f"Book with ID {book_id} does not exist.")
        return manage_books()


def update_book():
    book_id = int(input("Enter book ID to update: "))

    # Fetch current book details
    cursor.execute("SELECT * FROM books WHERE book_id=%s", (book_id,))
    book = cursor.fetchone()

    if book:
        print(
            f"Current details: Title: {book[1]}, Author: {book[2]}, Genre: {book[3]}, Available Copies: {book[4]}, Price: Rs{book[5]}")

        # Collect new details from the admin
        new_title = input("Enter new title (press Enter to keep current): ") or book[1]
        new_author = input("Enter new author (press Enter to keep current): ") or book[2]
        new_genre = input("Enter new genre (press Enter to keep current): ") or book[3]
        new_price = input("Enter new price (press Enter to keep current): ")
        new_available_copies = input("Enter new number of available copies (press Enter to keep current): ")

        if new_price:
            new_price = float(new_price)
        else:
            new_price = book[5]

        if new_available_copies:
            new_available_copies = int(new_available_copies)
        else:
            new_available_copies = book[4]

        # Update book details
        cursor.execute("""
            UPDATE books 
            SET title=%s, author=%s, genre=%s, available_copies=%s, price=%s 
            WHERE book_id=%s
        """, (new_title, new_author, new_genre,new_available_copies, new_price, book_id))
        db.commit()
        print("Book details updated successfully.")
        return manage_books()
    else:
        print(f"Book with ID {book_id} does not exist.")
        return manage_books()


def manage_books():
    print("\nBook Management")
    print("1. View Books")
    print("2. Add Book")
    print("3. Delete Book")
    print("4. Update Book")
    print("5. Back")
    choice = input("Enter choice: ")
    if choice == '1':
        view_books()
    elif choice == '2':
        add_book()
    elif choice == '3':
        delete_book()
    elif choice == '4':
        update_book()
    elif choice == '5':
        return admin_menu(admin_user=None)


# Function to view membership plans (Admin)
def view_plans():
    # Execute the query to fetch membership plans
    cursor.execute("SELECT * FROM membership_plans")
    plans = cursor.fetchall()

    # Loop through and print each plan
    for plan in plans:
        print(f"Plan ID: {plan[0]}, Name: {plan[1]}, Duration: {plan[2]} days, Price: Rs{plan[3]}")

    # Return to the manage membership plans menu after displaying all plans
    return manage_membership_plans()


# Function to add a new membership plan (Admin)
def add_plan():
    name = input("Enter plan name: ")
    duration = int(input("Enter plan duration in days: "))
    price = float(input("Enter plan price: "))

    cursor.execute("INSERT INTO membership_plans (plan_name, plan_duration, plan_price) VALUES (%s, %s, %s)",
                   (name, duration, price))
    db.commit()
    print("Membership plan added successfully.")
    return manage_membership_plans()

# Function to update a membership plan (Admin)
def update_plan():
    plan_id = int(input("Enter plan ID to update: "))

    # Fetch current plan details
    cursor.execute("SELECT * FROM membership_plans WHERE plan_id=%s", (plan_id,))
    plan = cursor.fetchone()

    if plan:
        print(f"Current details: Name: {plan[1]}, Duration: {plan[2]} days, Price: Rs{plan[3]}")

        # Collect new details from the admin
        new_name = input("Enter new name (press Enter to keep current): ") or plan[1]
        new_duration = input("Enter new duration in days (press Enter to keep current): ")
        new_price = input("Enter new price (press Enter to keep current): ")

        if new_duration:
            new_duration = int(new_duration)
        else:
            new_duration = plan[2]

        if new_price:
            new_price = float(new_price)
        else:
            new_price = plan[3]

        # Update plan details
        cursor.execute("""
            UPDATE membership_plans 
            SET plan_name=%s, plan_duration=%s, plan_price=%s 
            WHERE plan_id=%s
        """, (new_name, new_duration, new_price, plan_id))
        db.commit()
        print("Membership plan updated successfully.")
        return manage_membership_plans()
    else:
        print(f"Membership plan with ID {plan_id} does not exist.")
        return manage_membership_plans()


def manage_membership_plans():
    print("\nMembership Plan Management")
    print("1. View plans")
    print("2. Add Plan")
    print("3. Update Plan")
    print("4. Back")
    choice = input("Enter choice: ")
    if choice == '1':
        view_plans()
    elif choice == '2':
        add_plan()
    elif choice == '3':
        update_plan()
    elif choice == '4':
        return admin_menu(admin_user=None)


def view_borrowed_books():
    cursor.execute("""
                SELECT bb.borrow_id, u.username, b.title, bb.borrow_date, bb.due_date, bb.return_date
                FROM borrowed_books bb
                JOIN users u ON bb.user_id = u.user_id
                JOIN books b ON bb.book_id = b.book_id
                ORDER BY bb.borrow_date DESC
            """)
    borrowed_books = cursor.fetchall()

    if borrowed_books:
        print("\nBorrowed Books:")
        for book in borrowed_books:
            borrow_id = book[0]
            username = book[1]
            title = book[2]
            borrow_date = book[3].strftime('%Y-%m-%d')
            due_date = book[4].strftime('%Y-%m-%d') if book[4] else "Not set"
            return_date = book[5].strftime('%Y-%m-%d') if book[5] else "Not returned"

            print(f"Borrow ID: {borrow_id}")
            print(f"Username: {username}")
            print(f"Title: {title}")
            print(f"Borrow Date: {borrow_date}")
            print(f"Due Date: {due_date}")
            print(f"Return Date: {return_date}")
            print("-" * 40)
    else:
        print("No books have been borrowed.")


def manage_fines():
    while True:
        print("\nManage Fines")
        print("1. View All Fines")
        print("2. Search Fines by User")
        print("3. Search Fines by Book Title")
        print("4. Update Fine Amount")
        print("5. Delete Fine Record")
        print("6. Add Fine Amount")
        print("7. Back")
        choice = input("Enter choice: ")

        if choice == "1":
            view_all_fines()
        elif choice == "2":
            search_fines_by_user()
        elif choice == "3":
            search_fines_by_book_title()
        elif choice == "4":
            update_fine_amount()
        elif choice == "5":
            delete_fine_record()
        elif choice == "6":
            add_fine_amount()
        elif choice == "7":
            break
        else:
            print("Invalid choice. Please try again.")


def view_all_fines():
    cursor.execute("""
        SELECT f.fine_id, u.username, b.title, f.amount, f.date_issued
        FROM fines f
        JOIN users u ON f.user_id = u.user_id
        JOIN books b ON f.book_id = b.book_id
    """)
    fines = cursor.fetchall()

    if fines:
        print("\nAll Fines:")
        for fine in fines:
            fine_id = fine[0]
            username = fine[1]
            book_title = fine[2]
            amount = fine[3]
            date_issued = fine[4].strftime('%Y-%m-%d')

            print(f"Fine ID: {fine_id}")
            print(f"Username: {username}")
            print(f"Book Title: {book_title}")
            print(f"Amount: Rs{amount}")
            print(f"Date Issued: {date_issued}")
            print("-" * 40)
    else:
        print("No fines found.")


def search_fines_by_user():
    username = input("Enter the username to search for fines: ")

    cursor.execute("""
        SELECT f.fine_id, u.username, b.title, f.amount, f.date_issued
        FROM fines f
        JOIN users u ON f.user_id = u.user_id
        JOIN books b ON f.book_id = b.book_id
        WHERE u.username = %s
    """, (username,))
    fines = cursor.fetchall()

    if fines:
        print(f"\nFines for User '{username}':")
        for fine in fines:
            fine_id = fine[0]
            book_title = fine[2]
            amount = fine[3]
            date_issued = fine[4].strftime('%Y-%m-%d')

            print(f"Fine ID: {fine_id}")
            print(f"Book Title: {book_title}")
            print(f"Amount: Rs{amount}")
            print(f"Date Issued: {date_issued}")
            print("-" * 40)
    else:
        print(f"No fine records found for user '{username}'.")


def search_fines_by_book_title():
    book_title = input("Enter the book title to search for fines: ")

    cursor.execute("""
        SELECT f.fine_id, u.username, b.title, f.amount, f.date_issued
        FROM fines f
        JOIN users u ON f.user_id = u.user_id
        JOIN books b ON f.book_id = b.book_id
        WHERE b.title = %s
    """, (book_title,))
    fines = cursor.fetchall()

    if fines:
        print(f"\nFines for Book Title '{book_title}':")
        for fine in fines:
            fine_id = fine[0]
            username = fine[1]
            amount = fine[3]
            date_issued = fine[4].strftime('%Y-%m-%d')

            print(f"Fine ID: {fine_id}")
            print(f"Username: {username}")
            print(f"Amount: Rs{amount}")
            print(f"Date Issued: {date_issued}")
            print("-" * 40)
    else:
        print(f"No fine records found for the book title '{book_title}'.")


def update_fine_amount():
    fine_id = input("Enter the Fine ID to update: ")
    new_amount = input("Enter the new amount: ")

    try:
        new_amount = float(new_amount)
        cursor.execute("""
            UPDATE fines
            SET amount = %s
            WHERE fine_id = %s
        """, (new_amount, fine_id))

        if cursor.rowcount > 0:
            db.commit()  # Use 'db' instead of 'db_connection'
            print("Fine amount updated successfully.")
        else:
            print("No fine record found with the provided Fine ID.")
    except ValueError:
        print("Invalid amount. Please enter a valid number.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")


def delete_fine_record():
    fine_id = input("Enter the Fine ID to delete: ")

    cursor.execute("""
        DELETE FROM fines
        WHERE fine_id = %s
    """, (fine_id,))
    db.commit()  # Use 'db' instead of 'db_connection'

    if cursor.rowcount > 0:
        print("Fine record deleted successfully.")
    else:
        print("No fine record found with that ID.")


def add_fine_amount():
    user_id = input("Enter the User ID: ")
    book_id = input("Enter the Book ID: ")
    amount = input("Enter the amount: ")

    try:
        amount = float(amount)
        cursor.execute("""
            INSERT INTO fines (user_id, book_id, amount, date_issued)
            VALUES (%s, %s, %s, NOW())
        """, (user_id, book_id, amount))
        db.commit()  # Use 'db' instead of 'db_connection'
        print("Fine added successfully.")
    except ValueError:
        print("Invalid amount. Please enter a valid number.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")


def view_and_comment_reviews():
    cursor.execute("""
        SELECT r.review_id, u.username, b.title, r.rating, r.admin_comment
        FROM reviews r
        JOIN users u ON r.user_id = u.user_id
        JOIN books b ON r.book_id = b.book_id
    """)

    reviews = cursor.fetchall()

    if reviews:
        print("\nReviews:")
        for review in reviews:
            review_id = review[0]
            username = review[1]
            book_title = review[2]
            rating = review[3]
            admin_comment = review[4]

            print(f"Review ID: {review_id}")
            print(f"Username: {username}")
            print(f"Book Title: {book_title}")
            print(f"Rating: {rating}")
            print(f"Comment: {admin_comment if admin_comment else 'No comment'}")
            print("-" * 40)

        # Option to add a comment to a review
        comment_on_review()
    else:
        print("No reviews found.")


def comment_on_review():
    review_id = int(input("Enter the Review ID to comment on (or 0 to skip): "))

    if review_id == 0:
        # Return to Admin Menu if the admin chooses to skip
        admin_menu(admin_user=None)
        return

    # Check if the review exists
    cursor.execute("SELECT * FROM reviews WHERE review_id=%s", (review_id,))
    review = cursor.fetchone()

    if review:
        new_comment = input("Enter your comment (or press Enter to skip): ")

        if new_comment.strip() == "":
            print("No comment added.")
        else:
            cursor.execute("""
                UPDATE reviews 
                SET admin_comment=%s 
                WHERE review_id=%s
            """, (new_comment, review_id))
            db.commit()
            print("Comment added successfully!")
    else:
        print(f"Review with ID {review_id} does not exist.")

    # Return to Admin Menu
    admin_menu(admin_user=None)


def send_notifications(admin):
    try:
        # Prompt admin for the user ID and notification details
        user_id = input("Enter the User ID to send the notification to: ")
        message = input("Enter the notification message: ")

        # Validate message
        if not message.strip():
            print("Notification message cannot be empty.")
            return

        # Validate and check if user_id is a valid integer
        if not user_id.isdigit():
            print("Invalid User ID. It must be a number.")
            return

        # Check if the user exists
        cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
        if not cursor.fetchone():
            print("User ID not found.")
            return

        # Insert notification for the specified user
        cursor.execute("INSERT INTO notifications (user_id, message, date_created) VALUES (%s, %s, CURDATE())",
                       (user_id, message))
        db.commit()

        print("Notification sent successfully to user ID:", user_id)

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    # Return to the admin menu
    admin_menu(admin)

def search_books(user):
    while True:
        print("1. Search by title")
        print("2. Search by Author")
        print("3. Search by Genre")
        print("4. Back")
        choice = input("Enter choice: ")

        if choice == '1':
            search_by_title(user)
        elif choice == '2':
            search_by_author(user)
        elif choice == '3':
            search_by_genre(user)
        elif choice == '4':
            return user_menu(user)
        else:
            print("Invalid Option! Try Again")

def search_by_title(user):
    title = input("Enter book title to search: ")
    cursor.execute("SELECT * FROM books WHERE title LIKE %s", ('%' + title + '%',))
    books = cursor.fetchall()

    if not books:
        print("No books found with that title.")
    else:
        print("\nSearch Results:")
        for book in books:
            print(f"Book ID: {book[0]}")
            print(f"Title: {book[1]}")
            print(f"Author: {book[2]}")
            print(f"Genre: {book[3]}")
            print(f"Available Copies: {book[4]}")
            print(f"Price: Rs{book[5]}")
            print("-" * 40)
    return search_books(user)

def search_by_author(user):
    author = input("Enter author name to search: ")
    cursor.execute("SELECT * FROM books WHERE author LIKE %s", ('%' + author + '%',))
    books = cursor.fetchall()

    if not books:
        print("No books found by that author.")
    else:
        print("\nSearch Results:")
        for book in books:
            print(f"Book ID: {book[0]}")
            print(f"Title: {book[1]}")
            print(f"Author: {book[2]}")
            print(f"Genre: {book[3]}")
            print(f"Available Copies: {book[4]}")
            print(f"Price: Rs{book[5]}")
            print("-" * 40)
    return search_books(user)

def search_by_genre(user):
    genre = input("Enter genre to search: ")
    cursor.execute("SELECT * FROM books WHERE genre LIKE %s", ('%' + genre + '%',))
    books = cursor.fetchall()

    if not books:
        print("No books found in that genre.")
    else:
        print("\nSearch Results:")
        for book in books:
            print(f"Book ID: {book[0]}")
            print(f"Title: {book[1]}")
            print(f"Author: {book[2]}")
            print(f"Genre: {book[3]}")
            print(f"Available Copies: {book[4]}")
            print(f"Price: Rs{book[5]}")
            print("-" * 40)
    return search_books(user)


def process_payment1(price, account_number, expiry_date, cvv):
    # Implement your payment processing logic here
    # This is a placeholder example
    print(f"Processing payment of {price} using account {account_number}.")
    print(f"Expiry Date: {expiry_date}, CVV: {cvv}")

    # Return True to indicate payment success or False to indicate failure
    return True


def borrow_books(user):
    # Display available books
    cursor.execute("SELECT book_id, title, author, genre, available_copies, price FROM books WHERE available_copies > 0")
    books = cursor.fetchall()

    if not books:
        print("No books available for borrowing.")
        return

    print("\nAvailable Books:")
    for book in books:
        print(f"Book ID: {book[0]}, Title: {book[1]}, Author: {book[2]}, Genre: {book[3]}, Available Copies: {book[4]}, Price: ₹{book[5]}")

    # Prompt user to select a book
    book_id = input("Enter the Book ID of the book you wish to borrow: ")

    # Check if the selected book is available
    cursor.execute("SELECT available_copies, price FROM books WHERE book_id = %s", (book_id,))
    book = cursor.fetchone()

    if not book:
        print("Invalid Book ID. Please try again.")
        return

    if book[0] < 1:
        print("Sorry, this book is currently unavailable.")
        return

    # Display the borrowing fee and confirm payment
    price = book[1]
    print(f"The borrowing fee for this book is: ₹{price}")

    # Payment details input and validation
    while True:
        account_number = input("Enter your account  number: ")
        if not is_valid_account_number(account_number):
            print("Invalid account number. It must be 10-15 digits.")
        else:
            break

    while True:
        expiry_date = input("Enter the expiry date (MM/YY): ")
        if not is_valid_expiry_date(expiry_date):
            print("Invalid expiry date. Ensure it follows the MM/YY format and is a future date.")
        else:
            break

    while True:
        cvv = input("Enter the 3-digit CVV: ")
        if not is_valid_cvv(cvv):
            print("Invalid CVV. It must be 3 digits.")
        else:
            break

    payment_confirmed = input("Do you want to proceed with the payment? (yes/no): ").strip().lower()

    if payment_confirmed != 'yes':
        print("Payment not confirmed. Book borrowing canceled.")
        return

    # Process payment (this is a placeholder, replace with actual payment processing)
    if not process_payment1(price, account_number, expiry_date, cvv):
        print("Payment failed. Please try again.")
        return

    # Calculate due date (e.g., 14 days from today)
    due_date = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')

    # Insert into borrowed_books table
    cursor.execute("""
        INSERT INTO borrowed_books (user_id, book_id, borrow_date, due_date) 
        VALUES (%s, %s, CURDATE(), %s)
    """, (user[0], book_id, due_date))
    db.commit()

    # Update available copies of the book
    cursor.execute("UPDATE books SET available_copies = available_copies - 1 WHERE book_id = %s", (book_id,))
    db.commit()

    print(f"Book borrowed successfully! It is due on {due_date}.")

    # Optionally, print the borrowed book details
    cursor.execute("""
        SELECT b.title, b.author, bb.borrow_date, bb.due_date
        FROM borrowed_books bb
        JOIN books b ON bb.book_id = b.book_id
        WHERE bb.user_id = %s AND bb.book_id = %s
    """, (user[0], book_id))
    borrowed_book = cursor.fetchone()

    if borrowed_book:
        print("\nBorrowed Book Details:")
        print(f"Title: {borrowed_book[0]}")
        print(f"Author: {borrowed_book[1]}")
        print(f"Borrow Date: {borrowed_book[2]}")
        print(f"Due Date: {borrowed_book[3]}")

    user_menu(user)  # Return to the main menu for the user


def view_notifications(user):
    try:
        # Ensure user[0] is wrapped in a tuple
        cursor.execute("SELECT notification_id, message, date_created FROM notifications WHERE user_id = %s ORDER BY date_created DESC", (user[0],))
        notifications = cursor.fetchall()

        if not notifications:
            print("You have no notifications.")
            return

        print("\nYour Notifications:")
        for notification in notifications:
            print(f"Notification ID: {notification[0]}")
            print(f"Message: {notification[1]}")
            print(f"Date Created: {notification[2]}")
            print("-" * 40)

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    # Return to the user menu
    user_menu(user)

def submit_reviews(user):
    try:
        # Display available books for review
        cursor.execute("SELECT book_id, title FROM books")
        books = cursor.fetchall()

        if not books:
            print("No books available for review.")
            return

        print("\nAvailable Books:")
        for book in books:
            print(f"Book ID: {book[0]}, Title: {book[1]}")

        # Prompt user to select a book
        book_id = input("Enter the Book ID you want to review: ")

        # Validate if the book exists
        cursor.execute("SELECT book_id FROM books WHERE book_id = %s", (book_id,))
        if not cursor.fetchone():
            print("Invalid Book ID. Please try again.")
            return

        # Get the rating and review content from the user
        rating = input("Enter your rating for the book (1 to 5): ")

        if not rating.isdigit() or int(rating) < 1 or int(rating) > 5:
            print("Invalid rating. Rating must be a number between 1 and 5.")
            return

        review_text = input("Enter your review comments: ")

        # Insert the review into the database
        cursor.execute("""
            INSERT INTO reviews (user_id, book_id, rating, review_text, admin_comment)
            VALUES (%s, %s, %s, %s, NULL)
        """, (user[0], book_id, rating, review_text,))
        db.commit()

        print("Review submitted successfully!")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    # Return to the user menu
    user_menu(user)



def view_borrowing_history(user):
    try:
        # Fetch the user's borrowing history
        cursor.execute("""
            SELECT bb.borrow_id, b.title, bb.borrow_date, bb.due_date, bb.return_date
            FROM borrowed_books bb
            JOIN books b ON bb.book_id = b.book_id
            WHERE bb.user_id = %s
            ORDER BY bb.borrow_date DESC
        """, (user[0],))
        borrowed_books = cursor.fetchall()

        if borrowed_books:
            print("\nYour Borrowing History:")
            for book in borrowed_books:
                borrow_id = book[0]
                title = book[1]
                borrow_date = book[2].strftime('%Y-%m-%d')
                due_date = book[3].strftime('%Y-%m-%d') if book[3] else "Not set"
                return_date = book[4].strftime('%Y-%m-%d') if book[4] else "Not returned"

                print(f"Borrow ID: {borrow_id}")
                print(f"Title: {title}")
                print(f"Borrow Date: {borrow_date}")
                print(f"Due Date: {due_date}")
                print(f"Return Date: {return_date}")
                print("-" * 40)
        else:
            print("You have no borrowing history.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    # Return to the user menu
    user_menu(user)
def view_fines(user):
    try:
        # Fetch the user's outstanding fines
        cursor.execute("""
            SELECT f.fine_id, b.title, f.amount, f.date_issued
            FROM fines f
            JOIN books b ON f.book_id = b.book_id
            WHERE f.user_id = %s AND f.paid = FALSE
            ORDER BY f.date_issued DESC
        """, (user[0],))
        fines = cursor.fetchall()

        if not fines:
            print("You have no outstanding fines.")
            return

        print("\nYour Outstanding Fines:")
        for fine in fines:
            fine_id = fine[0]
            title = fine[1]
            amount = fine[2]
            date_issued = fine[3].strftime('%Y-%m-%d')

            print(f"Fine ID: {fine_id}")
            print(f"Book Title: {title}")
            print(f"Amount: ${amount:.2f}")
            print(f"Date Issued: {date_issued}")
            print("-" * 40)

    except mysql.connector.Error as err:
        print(f"Error: {err}")

def view_plans1():
    cursor.execute("SELECT * FROM membership_plans")
    plans = cursor.fetchall()

    for plan in plans:
        print(f"Plan ID: {plan[0]}, Name: {plan[1]}, Duration: {plan[2]} days, Price: Rs{plan[3]}")
    return main()


def view_books1():
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()

    if books:
        print("\nAvailable Books:")
        for book in books:
            print(f"Book ID: {book[0]}")
            print(f"Title: {book[1]}")
            print(f"Author: {book[2]}")
            print(f"Genre: {book[3]}")
            print(f"Available Copies: {book[4]}")
            print(f"Price: Rs{book[5]}")
            print("-" * 40)
        return main()
    else:
        print("No books found.")
        return main()


# Main Application
def main():
    print("Welcome to Library Management System")
    print("1. Register User")
    print("2. Login")
    print("3. Membership_plans")
    print("4. Books")
    print("5. Exit")

    choice = input("Enter choice: ")
    if choice == '1':
        register_user()
    elif choice == '2':
        login()
    elif choice == '3':
        view_plans1()
    elif choice == '4':
        view_books1()
    elif choice == '5':
        print("Exiting...")
        db.close()
    else:
        print("Invalid choice. Please try again.")
        return main()

if __name__ == "__main__":
    main()
