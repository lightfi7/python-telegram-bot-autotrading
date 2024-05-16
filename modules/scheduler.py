import schedule
import time
from datetime import datetime, timedelta

# Define the tasks and their respective times
tasks = [
    {'name': 'Task 1', 'time': '09:00', 'function': lambda: print("Task 1 executed!")},
    {'name': 'Task 2', 'time': '12:00', 'function': lambda: print("Task 2 executed!")},
    {'name': 'Task 3', 'time': '15:00', 'function': lambda: print("Task 3 executed!")}
]


# Function to schedule tasks
def schedule_tasks():
    for task in tasks:
        task_time = datetime.strptime(task['time'], '%H:%M').time()
        today = datetime.combine(datetime.today(), task_time)
        if today < datetime.now():
            today += timedelta(days=1)
            

# Run the scheduler
def run_scheduler():
    schedule_tasks()
    while True:
        schedule.run_pending()
        time.sleep(1)
