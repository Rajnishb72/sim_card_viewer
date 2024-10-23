import tkinter as tk
from tkinter import messagebox, Toplevel
import sqlite3
import datetime
import pytz
import phonenumbers
from phonenumbers import timezone, geocoder, carrier

# Create or connect to a database
conn = sqlite3.connect('user_info.db')
c = conn.cursor()

# Create table for users if it doesn't exist
c.execute("""CREATE TABLE IF NOT EXISTS users (
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL)""")
conn.commit()

# Create table for saved phone numbers
c.execute("""CREATE TABLE IF NOT EXISTS saved_numbers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_number TEXT NOT NULL,
            is_valid INTEGER,
            timezone TEXT,
            carrier TEXT,
            location TEXT,
            datetime TEXT)""")
conn.commit()

def signup():
    def register():
        username = username_entry.get()
        password = password_entry.get()

        if username and password:  # Simple validation
            try:
                c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                conn.commit()
                messagebox.showinfo("Success", "Account created successfully!")
                signup_window.destroy()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Username already exists!")
        else:
            messagebox.showerror("Error", "Username and password cannot be empty!")

    signup_window = Toplevel(root)
    signup_window.title("Signup")
    signup_window.geometry("400x300")
    signup_window.configure(bg='light blue')

    username_label = tk.Label(signup_window, text="Username:", font=("Helvetica", 10), bg='light blue')
    username_label.pack(pady=5)
    username_entry = tk.Entry(signup_window)
    username_entry.pack(pady=5)

    password_label = tk.Label(signup_window, text="Password:", font=("Helvetica", 10), bg='light blue')
    password_label.pack(pady=5)
    password_entry = tk.Entry(signup_window, show="*")
    password_entry.pack(pady=5)

    signup_btn = tk.Button(signup_window, text="Signup", command=register, bg='light blue')
    signup_btn.pack(pady=10)

def login():
    def validate_login():
        username = username_entry.get()
        password = password_entry.get()

        c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        if c.fetchone():
            messagebox.showinfo("Success", "You are logged in")
            login_window.destroy()
            show_main_window()
        else:
            messagebox.showerror("Error", "Invalid username or password")

    login_window = Toplevel(root)
    login_window.title("Login")
    login_window.geometry("400x300")
    login_window.configure(bg='light blue')

    username_label = tk.Label(login_window, text="Username:", bg='light blue')
    username_label.pack(pady=5)
    username_entry = tk.Entry(login_window)
    username_entry.pack(pady=5)

    password_label = tk.Label(login_window, text="Password:", bg='light blue')
    password_label.pack(pady=5)
    password_entry = tk.Entry(login_window, show="*")
    password_entry.pack(pady=5)

    login_btn = tk.Button(login_window, text="Login", command=validate_login, bg='light blue')
    login_btn.pack(pady=10)

def show_main_window():
    def save_number_info():
        number = phone_entry.get()
        if number:
            get_phone_number_info(phone_entry)
        else:
            messagebox.showerror("Error", "Please enter a phone number first!")

    def open_history_window():
        history_window = Toplevel(root)
        history_window.title("Phone Number History")
        history_window.geometry("600x400")
        history_window.configure(bg='light blue')

        # Fetch data from the database
        c.execute("SELECT * FROM saved_numbers")
        saved_numbers = c.fetchall()

        # Create a text widget to display the history
        history_text = tk.Text(history_window, height=20, width=60)
        history_text.pack(pady=10, padx=10)

        # Display the history in the text widget
        for saved_number in saved_numbers:
            history_text.insert(tk.END, f"ID: {saved_number[0]}\n")
            history_text.insert(tk.END, f"Phone Number: {saved_number[1]}\n")
            history_text.insert(tk.END, f"Is Valid: {'Yes' if saved_number[2] else 'No'}\n")
            history_text.insert(tk.END, f"Timezone: {saved_number[3]}\n")
            history_text.insert(tk.END, f"Carrier: {saved_number[4]}\n")
            history_text.insert(tk.END, f"Location: {saved_number[5]}\n")
            history_text.insert(tk.END, f"Date and Time: {saved_number[6]}\n\n")

    main_window = Toplevel(root)
    main_window.title("Phone Number Info")
    main_window.geometry("400x200")
    main_window.configure(bg='light blue')

    # Input field for phone number
    phone_label = tk.Label(main_window, text="Enter your phone number:", bg='light blue')
    phone_label.pack(pady=5)
    phone_entry = tk.Entry(main_window)
    phone_entry.pack(pady=5)

    # Button to get info
    info_button = tk.Button(main_window, text="Get Info", command=lambda: get_phone_number_info(phone_entry), bg='light blue')
    info_button.pack(pady=5)

    # Button to save number info
    save_button = tk.Button(main_window, text="Save", command=save_number_info, bg='light blue')
    save_button.pack(pady=5)

    # Button to view history
    history_button = tk.Button(main_window, text="View History", command=open_history_window, bg='light blue')
    history_button.pack(pady=5)

def get_phone_number_info(phone_entry):
    number = phone_entry.get()
    try:
        parsed = phonenumbers.parse("+91" + number)
        Valid_number = phonenumbers.is_possible_number(parsed)
        time_zone = ', '.join(timezone.time_zones_for_number(parsed))
        car = carrier.name_for_number(parsed, "en")
        reg = geocoder.description_for_number(parsed, "en")
        current_datetime = datetime.datetime.now(pytz.timezone('Asia/Calcutta'))

        # Convert datetime to string
        current_datetime_str = current_datetime.strftime('%Y-%m-%d %H:%M:%S')

        # Insert data into database
        c.execute("""INSERT INTO saved_numbers (phone_number, is_valid, timezone, carrier, location, datetime)
                     VALUES (?, ?, ?, ?, ?, ?)""",
                  (number, Valid_number, time_zone, car, reg, current_datetime_str))
        conn.commit()

        messagebox.showinfo("Phone Number Information",
                            f"Phone Number: {parsed}\n"
                            f"Is Valid: {Valid_number}\n"
                            f"Timezone: {time_zone}\n"
                            f"Carrier: {car}\n"
                            f"Location: {reg}\n"
                            f"Current Date and Time: {current_datetime.strftime('%d-%m-%y %H:%M:%S %Z')}")
    except phonenumbers.phonenumberutil.NumberParseException:
        messagebox.showerror("Error", "Invalid phone number format!")

# Create main window
root = tk.Tk()
root.title("Simcard Viewer")
root.geometry("400x300")
root.configure(bg='light blue')

# Label indicating "Simcard Viewer"
simcard_label = tk.Label(root, text="Simcard Viewer", font=("Helvetica", 30), bg='light blue')
simcard_label.pack(pady=15)

# Login and Signup buttons
login_button = tk.Button(root, text="Login", command=login, bg='light blue')
login_button.pack(pady=60)

signup_button = tk.Button(root, text="Signup", command=signup, bg='light blue')
signup_button.pack(pady=0)

# Run the application
root.mainloop()

# Close the connection to the database when the application is closed
conn.close()
