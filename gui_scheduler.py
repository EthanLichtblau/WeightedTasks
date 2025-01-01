import tkinter as tk
from tkinter import messagebox, simpledialog, Toplevel
from datetime import datetime
import random
import json

class Task:
    def __init__(self, name, weight):
        self.name = name
        self.weight = weight  # Importance (1-5)
        self.status = 'Ongoing'  # 'Ongoing', 'Complete', or 'Incomplete'
        self.days_worked = 0
        self.times_completed = 0
        self.times_incomplete = 0
        self.last_updated = datetime.now().date()
        self.is_finished = False  # Indicates if the task is completed overall

    def update_status(self, new_status):
        if new_status == 'Complete':
            self.times_completed += 1
        elif new_status == 'Incomplete':
            self.times_incomplete += 1
        self.status = new_status

    def increment_day(self):
        self.days_worked += 1
        self.last_updated = datetime.now().date()

    def finish_task(self):
        self.is_finished = True

def select_tasks(tasks, num_tasks=5):
    ongoing_tasks = [task for task in tasks if not task.is_finished]
    if not ongoing_tasks:
        return []

    weighted_list = []
    for task in ongoing_tasks:
        weighted_list.extend([task] * task.weight)

    selected_tasks = []
    while ongoing_tasks and len(selected_tasks) < num_tasks and weighted_list:
        task = random.choice(weighted_list)
        if task not in selected_tasks:
            selected_tasks.append(task)
            # Remove task from weighted list to prevent reselection
            weighted_list = [t for t in weighted_list if t != task]
    return selected_tasks

def daily_update(tasks):
    today = datetime.now().date()
    for task in tasks:
        if task.last_updated < today:
            if task.status == 'Ongoing':
                task.update_status('Incomplete')
            task.increment_day()
            task.status = 'Ongoing'

def save_tasks(tasks, filename='tasks.json'):
    with open(filename, 'w') as f:
        json.dump([task.__dict__ for task in tasks], f, default=str)

def load_tasks(filename='tasks.json'):
    tasks = []
    try:
        with open(filename, 'r') as f:
            tasks_data = json.load(f)
            for data in tasks_data:
                task = Task(data['name'], data['weight'])
                task.status = data['status']
                task.days_worked = data['days_worked']
                task.times_completed = data['times_completed']
                task.times_incomplete = data['times_incomplete']
                task.last_updated = datetime.strptime(data['last_updated'], '%Y-%m-%d').date()
                task.is_finished = data['is_finished']
                tasks.append(task)
    except FileNotFoundError:
        pass
    return tasks

class TaskSchedulerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Daily Task Scheduler")
        self.tasks = []
        self.selected_tasks = []
        self.create_widgets()
        self.load_tasks()
        self.refresh_task_list()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        # Task list display
        self.task_listbox = tk.Listbox(self.root, width=50)
        self.task_listbox.pack(padx=10, pady=10)

        # Buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Add Task", command=self.add_task).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Edit Task", command=self.edit_task).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Change Weight", command=self.change_weight).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="Mark Complete", command=self.mark_complete).grid(row=0, column=3, padx=5)
        tk.Button(btn_frame, text="Finish Task", command=self.finish_task).grid(row=0, column=4, padx=5)
        tk.Button(btn_frame, text="View Details", command=self.view_details).grid(row=0, column=5, padx=5)
        tk.Button(btn_frame, text="View All Tasks", command=self.view_all_tasks).grid(row=0, column=6, padx=5)
        tk.Button(btn_frame, text="Refresh Tasks", command=self.refresh_tasks).grid(row=0, column=7, padx=5)

    def load_tasks(self):
        self.tasks = load_tasks()
        if not self.tasks:
            # Initialize with predefined tasks if no tasks are loaded
            self.tasks = [
                Task("Add tasks", 4)
            ]
        daily_update(self.tasks)
        self.selected_tasks = select_tasks(self.tasks)
    
    def refresh_task_list(self):
        self.task_listbox.delete(0, tk.END)
        for task in self.selected_tasks:
            status = f"{task.name} - Weight: {task.weight} - Status: {task.status}"
            self.task_listbox.insert(tk.END, status)

    def add_task(self):
        name = simpledialog.askstring("Add Task", "Task Name:")
        if name:
            weight = simpledialog.askinteger("Add Task", "Importance Weight (1-5):", minvalue=1, maxvalue=5)
            if weight:
                new_task = Task(name, weight)
                self.tasks.append(new_task)
                self.selected_tasks = select_tasks(self.tasks)
                self.refresh_task_list()

    def edit_task(self):
        selected_index = self.task_listbox.curselection()
        if selected_index:
            task = self.selected_tasks[selected_index[0]]
            name = simpledialog.askstring("Edit Task", "Task Name:", initialvalue=task.name)
            if name:
                task.name = name
                self.refresh_task_list()
    
    def change_weight(self):
        selected_index = self.task_listbox.curselection()
        if selected_index:
            task = self.selected_tasks[selected_index[0]]
            weight = simpledialog.askinteger("Change Weight", f"Current Weight: {task.weight}\nEnter new weight (1-5):", minvalue=1, maxvalue=5)
            if weight:
                task.weight = weight
                self.selected_tasks = select_tasks(self.tasks)
                self.refresh_task_list()

    def mark_complete(self):
        selected_index = self.task_listbox.curselection()
        if selected_index:
            task = self.selected_tasks[selected_index[0]]
            task.update_status('Complete')
            self.refresh_task_list()

    def finish_task(self):
        selected_index = self.task_listbox.curselection()
        if selected_index:
            task = self.selected_tasks[selected_index[0]]
            task.finish_task()
            self.selected_tasks = select_tasks(self.tasks)
            self.refresh_task_list()

    def view_details(self):
        selected_index = self.task_listbox.curselection()
        if selected_index:
            task = self.selected_tasks[selected_index[0]]
            details = (
                f"Task Name: {task.name}\n"
                f"Weight: {task.weight}\n"
                f"Status: {task.status}\n"
                f"Days Worked On: {task.days_worked}\n"
                f"Times Completed: {task.times_completed}\n"
                f"Times Incomplete: {task.times_incomplete}\n"
                f"Last Updated: {task.last_updated}\n"
            )
            messagebox.showinfo("Task Details", details)

    def view_all_tasks(self):
        all_tasks_window = Toplevel(self.root)
        all_tasks_window.title("All Tasks")

        # Listbox to display all tasks
        all_tasks_listbox = tk.Listbox(all_tasks_window, width=70)
        all_tasks_listbox.pack(padx=10, pady=10)

        # Populate the listbox with all tasks
        for task in self.tasks:
            status = f"{task.name} - Weight: {task.weight} - Status: {task.status} - Finished: {task.is_finished}"
            all_tasks_listbox.insert(tk.END, status)

        tk.Button(all_tasks_window, text="Close", command=all_tasks_window.destroy).pack(pady=5)

    def refresh_tasks(self):
        daily_update(self.tasks)
        self.selected_tasks = select_tasks(self.tasks)
        self.refresh_task_list()

    def on_closing(self):
        save_tasks(self.tasks)
        self.root.destroy()

def main():
    root = tk.Tk()
    app = TaskSchedulerGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()
