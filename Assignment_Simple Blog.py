import re
import datetime
from tabulate import tabulate
import mysql.connector

# Database connection
databaseobj = mysql.connector.connect(
    host='localhost',
    user='root',
    password='faith',
    database='BlogDb'
)

login = databaseobj.cursor()

# Creating table LoginInfo in database BlogDb
login.execute("""
    CREATE TABLE IF NOT EXISTS LoginInfo(
        userid VARCHAR(50) PRIMARY KEY,
        password VARCHAR(50),
        first_name VARCHAR(50),
        last_name VARCHAR(50)
    )
""")

# Creating table Blog in database BlogDb
login.execute("""
    CREATE TABLE IF NOT EXISTS Blog(
        Blog_id INT AUTO_INCREMENT PRIMARY KEY,
        Title VARCHAR(50),
        Description TEXT,
        Time_and_Date DATETIME,
        userid VARCHAR(50),
        FOREIGN KEY(userid) REFERENCES LoginInfo(userid)
    )
""")


# Function to register a new user
def register():
    while True:
        try:
            global userid
            print("Register your details here")
            while True:
                first_name = input("Enter the first name: ")
                if re.fullmatch("[A-Za-z]{2,25}", first_name):
                    break
                else:
                    print("INVALID!! Enter only alphabets of length 2 to 25.")

            while True:
                last_name = input("Enter the last name: ")
                if re.fullmatch("[A-Za-z]{1,25}", last_name):
                    break
                else:
                    print("INVALID!! Enter only alphabets of length 1 to 25.")

            while True:
                userid = input("Create a user id: ")
                if " " not in userid:
                    if re.fullmatch(r'^(?=.*[A-Za-z])(?=.*\d).{6,16}$', userid):
                        break
                    else:
                        print("Invalid!! Should be an alphanumeric character of length 6 to 16.")
                else:
                    print("Invalid!! User ID should not contain spaces.")

            while True:
                password = input("Enter the password: ")
                if " " not in password:
                    if re.fullmatch(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@#$%^&+!_]).{6,16}$', password):
                        break
                    else:
                        print("""The password should contain:
                                    - At least one uppercase letter
                                    - At least one lowercase letter
                                    - At least one number
                                    - At least one special character [ @ # $ % ^ & + ! _ ]
                                    - Minimum length of 6 characters and maximum 16 characters.""")
                else:
                    print("INVALID!!! Password should not contain spaces.")

            insert_query = "INSERT INTO LoginInfo(userid, password, first_name, last_name) VALUES(%s, %s, %s, %s)"
            login.execute(insert_query, (userid, password, first_name, last_name))
            databaseobj.commit()

            print("You have successfully registered.")
            break
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            print("User ID might already exist.")


# Function to view all blog posts
def viewlist():
    query = 'SELECT * FROM Blog'
    login.execute(query)
    query_result = login.fetchall()
    if query_result:
        print(tabulate(query_result, headers=["Blog_id", "Title", "Description", "Date_and_Time", "userid"]))
    else:
        print("The list is empty.")


# Function to create a new blog post
def create():
    while True:
        title = input("Enter your Blog title: ")
        if title:
            break
        else:
            print("Title cannot be empty!!!")

    while True:
        description = input("Enter the description: ")
        if description:
            break
        else:
            print("Description cannot be empty!!!")

    time_and_date = datetime.datetime.now()
    title = title.upper()
    insert_query = "INSERT INTO Blog(Title, Description, Time_and_Date, userid) VALUES(%s, %s, %s, %s)"
    login.execute(insert_query, (title, description, time_and_date, userid))
    databaseobj.commit()
    print("You have successfully added your new post... :)")


# Function to update a blog post title
def update_title(blog_id):
    while True:
        new_title = input("Enter the new title: ")
        if new_title:
            time_and_date = datetime.datetime.now()
            query = "UPDATE Blog SET Title=%s, Time_and_Date=%s WHERE Blog_id=%s"
            login.execute(query, (new_title, time_and_date, blog_id))
            databaseobj.commit()
            print("Successfully updated the title!!! :)")
            break
        else:
            print("This field cannot be empty.")


# Function to update a blog post description
def update_description(blog_id):
    while True:
        new_description = input("Enter the new description: ")
        if new_description:
            time_and_date = datetime.datetime.now()
            query = "UPDATE Blog SET Description=%s, Time_and_Date=%s WHERE Blog_id=%s"
            login.execute(query, (new_description, time_and_date, blog_id))
            databaseobj.commit()
            print("Successfully updated the description!!! :)")
            break
        else:
            print("This field cannot be empty.")


# Function to update a blog post
def update():
    global userid
    query = 'SELECT Blog_id, Title, Description, Time_and_Date FROM Blog WHERE userid=%s'
    login.execute(query, (userid,))
    query_result = login.fetchall()
    if query_result:
        print(tabulate(query_result, headers=["Blog_id", "Title", "Description", "Date_and_Time"]))
        while True:
            blog_id = input("Enter the blog ID to be edited: ")
            if blog_id.isdigit():
                query = "SELECT * FROM Blog WHERE Blog_id=%s AND userid=%s"
                login.execute(query, (blog_id, userid))
                result = login.fetchone()
                if result:
                    print(f"Details for the selected blog ID ({blog_id}):")
                    print(f" Blog_id: {result[0]}, Title: {result[1]}, Description: {result[2]}, Updated date: {result[3]}, Userid: {result[4]}")
                    while True:
                        print("Choose an option you want to edit:")
                        print("1. Title")
                        print("2. Description")
                        print("3. Go back")
                        choice = input("Enter a number from the above list: ")
                        if choice == "1":
                            update_title(blog_id)
                            break
                        elif choice == "2":
                            update_description(blog_id)
                            break
                        elif choice == "3":
                            return
                        else:
                            print("Invalid!!! Enter numbers from 1 to 3 only...")
                else:
                    print("INVALID!!! Blog ID does not exist. Enter a valid blog ID.")
            else:
                print("Enter a valid numeric Blog ID.")
    else:
        print("The list is empty.")


# Function to delete a blog post
# Function to delete a blog post
def delete():
    global userid
    query = 'SELECT Blog_id, Title, Description, Time_and_Date FROM Blog WHERE userid=%s'
    login.execute(query, (userid,))
    query_result = login.fetchall()
    if query_result:
        print(tabulate(query_result, headers=["Blog_id", "Title", "Description", "Date_and_Time"]))
        while True:
            blog_id = input("Enter the blog ID to be deleted: ")
            if blog_id.isdigit():
                query = "SELECT * FROM Blog WHERE Blog_id=%s AND userid=%s"
                login.execute(query, (blog_id, userid))
                result = login.fetchone()
                if result:
                    print("Are you sure you want to delete this post?")
                    print("1. Yes")
                    print("2. No")
                    choice = input("Enter an option: ")
                    if choice == "1":
                        query = "DELETE FROM Blog WHERE Blog_id=%s"
                        login.execute(query, (blog_id,))
                        databaseobj.commit()
                        print("Successfully deleted the post!!! :)")
                        break
                    elif choice == "2":
                        return
                    else:
                        print("INVALID!!! Enter an option from above [1 or 2].")
                else:
                    print("Blog ID does not exist.")
            else:
                print("Enter a valid numeric Blog ID.")
    else:
        print("The list is empty.")
    # Ensure to break out of the loop after deletion is done
    return

# Function for the main option page after login
def optionpage():
    while True:
        print("""-----------------------------
WELCOME USER
-----------------------------                         
Choose an option to continue:
1. View all posts
2. Create post
3. Update post
4. Delete post
5. Logout""")
        choice = input("Enter your choice: ")
        if choice == "1":
            viewlist()
        elif choice == "2":
            create()
        elif choice == "3":
            update()
        elif choice == "4":
            delete()
        elif choice == "5":
            print("You have been logged out!!!")
            break
        else:
            print("Invalid!!! Enter numbers from 1 to 5 only...")


# Function to login
def loginfun():
    global userid
    while True:
        userid = input("Enter the user ID: ")
        if userid:
            break
        else:
            print("This field cannot be empty.")

    while True:
        password = input("Enter the password: ")
        if password:
            break
        else:
            print("This field cannot be empty.")

    login_query = 'SELECT * FROM LoginInfo WHERE userid=%s AND password=%s'
    login.execute(login_query, (userid, password))
    result = login.fetchone()

    if result:
        optionpage()
    else:
        print("INVALID LOGIN!!!")
        print("The user ID or password is incorrect.")


# Main function to start the program
def main():
    print("Welcome to the Blogging platform!!!")
    while True:
        print("""
Choose one of the following options:
1. Register
2. Login
3. Exit""")
        choice = input("Enter your choice: ")
        if choice == "1":
            register()
        elif choice == "2":
            loginfun()
        elif choice == "3":
            print("Thank you for visiting.")
            break
        else:
            print("Invalid!!! Enter numbers from 1 to 3 only.")


if __name__ == "__main__":
    main()
