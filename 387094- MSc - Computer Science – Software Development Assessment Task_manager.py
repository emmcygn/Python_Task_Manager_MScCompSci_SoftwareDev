#Welcome to the Python Task Manager! This is a simple application to help you manage your tasks.
#This was written by Emmanuel Cuyugan, 2024, for the Software Development Module of the 
#MSc Computer Science (Conversion) at the University of Law.


# Import the relevant modules and classes
import os # Added os module
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide" # Hide pygame support prompt
import time # Added time module
import threading # Added threading module to run due date checks in a separate thread
import traceback # Added traceback module to print exception details in debug mode
import sys # Added sys module to exit the application
import calendar # Added calendar module 
import datetime # Added datetime module 
import logging # Added logging module to log function calls
import schedule # Added schedule module to schedule due date checks
from notifypy import Notify # Added notifypy module to send notifications
from task import Task # Added Task class to create task objects
import pygame # Added pygame module to limit notification sound loops

# Get the relative path to the notification sound file and notification icon
sound_filename = "notify-diskload.wav"
sound_file_path = os.path.join(os.path.dirname(__file__), sound_filename)

sound_filename2 = "crumple.wav"
sound_file_path2 = os.path.join(os.path.dirname(__file__), sound_filename2)

icon_filename = "custom_icon.png"
icon_path = os.path.join(os.path.dirname(__file__), icon_filename)

# Initialise the notification object
notification = Notify()
notification.icon = icon_path

# Define a variable to track whether the notification has been sent
notification_sent = False

# Define the logging decorator to log function calls
def log_function_call(func):
    def wrapper(*args, **kwargs):
        logging.info(f"Running {func.__name__} with args: {args}, kwargs: {kwargs}")
        result = func(*args, **kwargs)
        logging.info(f"{func.__name__} successfully ran. Returned {result}")
        return result
    
    return wrapper

# Define classes to add styles to the text below
def green(text):
    return f"\033[92m{text}\033[00m"

def red(text):
    return f"\033[91m{text}\033[00m"

def gold(text):
    return f"\033[93m{text}\033[00m"

def print_bold(text):
    return "\033[1m" + text + "\033[0m"

# Define a function to handle errors
def error_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as ve:
            print(f"ValueError: {ve}")
            if DEBUG:  # Log traceback in debug mode
                print(f"Exception details: {traceback.format_exc()}")
        except IOError as ioe:
            print(f"IOError: {ioe}")
            if DEBUG:  # Log traceback in debug mode
                print(f"Exception details: {traceback.format_exc()}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            if DEBUG:  # Log traceback in debug mode
                print(f"Exception details: {traceback.format_exc()}")
    
    return wrapper

# MAIN FUNCTION (Define the main function for the task manager)
DEBUG = False  # Set to False in production  # Added debug flag

@error_handler  # Apply the error_handler decorator to the main function
@log_function_call  # Apply the log_function_call decorator to the main function
def main():
    # Configure the logging module
    logging.basicConfig(
        filename="task_manager.log",
        level=logging.DEBUG if DEBUG else logging.INFO,  # Use DEBUG level if in debug mode
        format="%(asctime)s:%(levelname)s:%(message)s",
    )

    print()
    print(f"📌 Welcome To Your Task Manager 📌")
    print()
    task_file_path = "tasks.csv"

    # Start a thread for the due date checks to run in the background
    due_date_thread = threading.Thread(
        target=check_due_dates, args=(task_file_path,), daemon=True
    )
    due_date_thread.start() # Start the due date thread
    due_date_thread.join()  # Wait for the due date thread to finish before exiting the application

    # MAIN MENU (Display the main menu)
    while True:
        print(print_bold("📁 Main Menu:"))
        print()
        print(" 1. 📝 Add a task")
        print(" 2. 📘 View all tasks (by due date)")
        print(" 3. 📙 View all tasks (by category)")
        print(" 4. 📂 Search for a task (by name)")
        print(" 5. ✔  Delete a task")
        print(" 6. ❌ Exit")

        # Debug information in debug mode
        if DEBUG:
            print(f"   [DEBUG MODE] Logging Level: {'DEBUG' if DEBUG else 'INFO'}")
        
        print()  # Add an extra line for better formatting

        # Get user input for menu selection
        while True:
            try:
                menu_selection = int(input("📁 Enter a menu number [1-6]: "))
                if menu_selection in range(1, 7):
                    break
                else:
                    print("Invalid menu selection. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a valid number.")

        print()

        # Process the menu selection and call the relevant functions
        if menu_selection == 1:
            print(green("Add a task"))
            print()
            # Add Task: Get user input for task name, priority, due date, and category
            task = get_user_tasks()
            # Write the task to a file
            save_task_to_file(task, task_file_path)
            print()

        elif menu_selection == 2:
            print(green("View all tasks (Due Date)"))
            # View all tasks by due date
            view_all_tasks_due_date(task_file_path)
            print()

        elif menu_selection == 3:
            print(green("View all tasks (Category)"))
            # View all tasks by category
            view_all_tasks_category(task_file_path)
            print()

        elif menu_selection == 4:
            print(green("Search for a task (by name)"))
            # Search for a task by name or term
            search_term = input("Enter text to search for: ")
            # Call the search_tasks_term function to search for the term
            search_tasks_term(task_file_path, search_term)
            print()

        elif menu_selection == 5:
            print(red("Delete a task"))
            # Delete a task from the file and save the updated tasks back to the file
            delete_task(task_file_path)
            print()

        elif menu_selection == 6:
            print()
            # Exit the application if the user selects 6
            print(print_bold(red("Exiting the application.")))
            print()
            break


# Define a function to get user input for task
@error_handler  # Apply the error_handler decorator to the get_user_tasks function
def get_user_tasks():
    task_name = input("📋 What is the task? ")

    # Get user input for task priority
    while True:
        try:
            task_priority = float(input("📊 What is the task priority? (1Low/5High)"))
            if task_priority.is_integer() and task_priority in range(1, 7):
                break
            else:
                print("Priority must be an integer between 1 and 6.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

    print()
    print(f"📊 Selected Task Priority (1Low/5High): {task_priority}")
    print()

    # Get user input for task category
    task_categories = [
        "📖 Academic Coursework",
        "📤 Academic Deadline",
        "💻 Administrative Work",
        "📲 Personal Task",
        "🔧 Task for Others",
    ]

    # Display the task categories
    while True:
        print("📁 Select a category: ")
        for i, category_name in enumerate(task_categories):
            print(f" {i + 1}. {category_name}")
        print()  # Add an extra line for better formatting

        value_range = f"[1 - {len(task_categories)}]"

        # Get user input for category selection
        while True:
            try:
                selected_index = (
                    int(input(f"📁 Enter a category number {value_range}: ")) - 1
                )
                if selected_index in range(len(task_categories)):
                    selected_category = task_categories[selected_index]
                    break  # Exit the loop if the input is valid
                else:
                    print("📛 Invalid Category. Please Try Again.")
            except ValueError:
                print("📛 Invalid input. Please enter a valid number.")

        print(f"📁 Selected Category: {selected_category}")
        print()

        # Get user input for task due date
        while True:
            try:
                task_due_date = input("📅 When is the task due? (dd/mm/yyyy) ")
                task_due_date = datetime.datetime.strptime(
                    task_due_date, "%d/%m/%Y"
                ).date()

                if task_due_date < datetime.date.today():
                    print("📛 Invalid Date. Please Try Again.")
                    continue
                else:
                    break
            except ValueError:
                print("📛 Invalid input. Please enter a valid date.")

        print(f"📅 Selected Due Date: {task_due_date}")
        print()

        # Create a new task object and return it to the caller function
        new_task = Task(
            name=task_name,
            category=selected_category,
            priority=task_priority,
            due_date=task_due_date,
        )
        return new_task


# Define a function to save the task to a file
def save_task_to_file(task: Task, task_file_path):
    global notification_sent  # Use the global variable to track whether the notification has been sent
    print(gold(f"💾 Saving Task to File: {task} to {task_file_path}"))
    # Write the task to the file in append mode (a)
    with open(task_file_path, "a") as f:
        f.write(f"{task.category},{task.name},{task.priority},{task.due_date}\n")

    if (
        not notification_sent
    ):  # Only send the notification if it hasn't been sent before
        # Create a notification to show that the task has been added successfully
        notification = Notify()
        notification.title = "Task Manager"
        notification.message = f"💾 Task '{task.name}' added successfully!"
        notification.audio = sound_file_path
        notification.send()

        notification_sent = True  # Set the notification_sent variable to True to indicate that the notification has been sent

    print()


# Define a function to read a file and summarize tasks by category and due date
def summarise_all_tasks(task_file_path):
    print(f"📊 Summarising Tasks")
    tasks = []
    with open(task_file_path, "r") as f:
        lines = f.readlines()
        for line in lines:
            stripped_line = line.strip()
            (
                task_category,
                task_name,
                task_priority,
                task_due_date,
            ) = stripped_line.split(",")
            print(task_category, task_name, task_priority, task_due_date)
            line_tasks = Task(
                category=task_category,
                name=task_name,
                priority=float(task_priority),
                due_date=datetime.datetime.strptime(task_due_date, "%Y-%m-%d").date(),
            )
            tasks.append(line_tasks)

    print()

    tasks_by_category = {}
    for task in tasks:
        key = task.category
        if key in tasks_by_category:
            tasks_by_category[key] += 1
        else:
            tasks_by_category[key] = 1

    print("📌 Tasks Summary:")

    # print the tasks by category
    for key, count in tasks_by_category.items():
        print(f"     {key}: {count} task/s")

    print()

    rerun = input(
        gold("🔃 Would you like to go back to the Main Menu? (yes/no): ").lower()
    )

    if rerun == "yes":
        print()
        main()  # Rerun the application
    else:
        print()
        print(red("❌ Exiting the application ❌"))


# Define a function to search for a task by name/term
def search_tasks_term(task_file_path, search_term):
    tasks = read_tasks_from_file(task_file_path)

    matching_tasks = [
        task for task in tasks if search_term.lower() in task.name.lower()
    ]

    if matching_tasks:
        # Sort matching tasks by category
        matching_tasks.sort(key=lambda task: task.category)

        print("➡ Matching tasks (sorted by category):")
        for task in matching_tasks:
            print(
                f" - {task.category} ({task.name}), Priority: {task.priority}, Due Date: {task.due_date}"
            )
            print()
    else:
        print("📛 No matching tasks found.")
        print()


# Function to delete a task
def delete_task(task_file_path):
    try:
        with open(task_file_path, "r") as f:
            lines = f.readlines()

        # Display existing tasks with their numbers
        print(print_bold(gold("📖 Existing Tasks:")))
        for i, line in enumerate(lines, start=1):
            print(f"{i}. {line.strip()}")

        user_input = input(green(
            "✂ Enter the task number you want to delete (or '0' to cancel): "
        ))
        print()

        if user_input == "0":
            print("📛 Deletion canceled.")
        else:
            task_number = int(user_input)
            if 1 <= task_number <= len(lines):
                deleted_task = lines.pop(task_number - 1).strip()

                # Save updated tasks back to the file
                with open(task_file_path, "w") as f:
                    f.writelines(lines)

                notification.title = "Task Manager"
                notification.message = f"✂ Task '{deleted_task}' deleted successfully!"
                notification.audio = sound_file_path2
                notification.send()

                print(red(f"✂ Task '{deleted_task}' deleted successfully!"))
                print()
            else:
                print("📛 Invalid task number!")
    except ValueError:
        print("📛 Invalid input! Task number should be an integer.")
    except IOError:
        print("📛 Error occurred while deleting the task.")


# Define a function to view all tasks by due date
def view_all_tasks_due_date(task_file_path):
    print(f"📅 Loading Tasks by (Due Date)")
    print()
    print(f"📊 Task Summary:")
    print()
    tasks = read_tasks_from_file(task_file_path)

    # Sort tasks by due date
    tasks.sort(key=lambda task: task.due_date)

    # Print the tasks with due date information
    for task in tasks:
        due_date_str = task.due_date.strftime("%A, %d %B %Y")
        days_until_due = (task.due_date - datetime.date.today()).days

        if days_until_due == 0:
            due_info = "📍 due today"
        elif days_until_due == 1:
            due_info = "📫 due tomorrow"
        elif days_until_due > 1:
            due_info = f"📮 due in {days_until_due} days"
        else:
            due_info = "💢 already overdue"

        print(f"    {task.category} ({print_bold(gold(task.name))}) - {due_info}")
        print()


# Define a function to view all tasks by category
def view_all_tasks_category(task_file_path):
    print(f"📝 Loading Tasks by (Category)")
    print(f"📊 Task Summary")
    tasks = read_tasks_from_file(task_file_path)

    # Sort tasks by category
    tasks.sort(key=lambda task: task.category)

    # Print the tasks with due date information
    for task in tasks:
        due_date_str = task.due_date.strftime("%A, %d %B %Y")
        days_until_due = (task.due_date - datetime.date.today()).days

        if days_until_due == 0:
            due_info = "📍 due today"
        elif days_until_due == 1:
            due_info = "📫 due tomorrow"
        elif days_until_due > 1:
            due_info = f"📮 due in {days_until_due} days"
        else:
            due_info = "💢 already overdue"

        print(f"    {task.category} ({print_bold(gold(task.name))}) - {due_info}")
        print()

    print()


# Define a function to check due dates and send notifications
def check_due_dates(task_file_path):
    # Read tasks from the file and check due dates
    tasks = read_tasks_from_file(task_file_path)

    # TODAY Reminders
    today = datetime.date.today()
    due_today = [task for task in tasks if task.due_date == today]

    # TOMORROW Reminders
    tomorrow = today + datetime.timedelta(days=1)
    due_tomorrow = [task for task in tasks if task.due_date == tomorrow]

    # OVERDUE Reminders
    # Get tasks with due dates before today
    due_overdue = [task for task in tasks if task.due_date < today]

    # Send notifications for tasks due today
    for task in due_today:
        send_notification(task)

    # Send notifications for tasks due tomorrow
    for task in due_tomorrow:
        send_notification(task, is_reminder=True)

    # Send notifications for overdue tasks
    for task in due_overdue:
        send_notification(task, is_overdue=True)


def send_notification(task, is_reminder=False, is_overdue=False):
    try:
        global notification_sent
        # Initialize pygame mixer if it hasn't been initialized
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        # Set audio only once for the set of notifications
        if not notification_sent:
            notification_sent = True
            pygame.mixer.music.load(sound_file_path)
            pygame.mixer.music.play()

        # Your code for sending notifications goes here
        # For example, you can use the Notify class from notifypy
        notification = Notify()
        notification.icon = icon_path

        if is_reminder:
            notification.title = "Task Reminder"
        elif is_overdue:
            notification.title = "Task Overdue"
            notification.message = f"Task '{task.name}' is overdue!"
        else:
            notification.title = "Task Due Today"

        notification.message = (
            f"📫 Task '{task.name}' is due tomorrow!"
            if is_reminder
            else f"💢 Task '{task.name}' is overdue!"
            if is_overdue
            else f"📍 Task '{task.name}' is due today!"
        )

        # Set a custom timeout (in milliseconds)
        notification.timeout = 3000

        notification.send()
    except Exception as e:
        print(f"📛 Error sending notification: {e}")


# Define a function to read tasks from the file
def read_tasks_from_file(task_file_path):
    tasks = []
    with open(task_file_path, "r") as f:
        lines = f.readlines()
        for line in lines:
            stripped_line = line.strip()
            (
                task_category,
                task_name,
                task_priority,
                task_due_date,
            ) = stripped_line.split(",")
            task = Task(
                category=task_category,
                name=task_name,
                priority=float(task_priority),
                due_date=datetime.datetime.strptime(task_due_date, "%Y-%m-%d").date(),
            )
            tasks.append(task)
    return tasks


# Define the main function
if __name__ == "__main__":
    main()
