import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.font import Font

# Encapsulate homework data in a class
class Homework:
    def __init__(self, subject, title, description, due_date, status):
        self.subject = subject
        self.title = title
        self.description = description
        self.due_date = due_date
        self.status = status

    def to_dict(self):
        return {
            'type': 'Homework',
            'subject': self.subject,
            'title': self.title,
            'description': self.description,
            'due_date': self.due_date,
            'status': self.status
        }

    @staticmethod
    def from_dict(d):
        if d.get('type') == 'TimedHomework':
            return TimedHomework.from_dict(d)
        return Homework(d['subject'], d['title'], d['description'], d['due_date'], d['status'])

# Inheritance: TimedHomework subclass
class TimedHomework(Homework):
    def __init__(self, subject, title, description, due_date, status, time_required):
        super().__init__(subject, title, description, due_date, status)
        self.time_required = time_required  # in minutes

    def to_dict(self):
        d = super().to_dict()
        d['type'] = 'TimedHomework'
        d['time_required'] = self.time_required
        return d

    @staticmethod
    def from_dict(d):
        return TimedHomework(
            d['subject'], d['title'], d['description'], d['due_date'], d['status'], d.get('time_required', 0)
        )
from datetime import datetime
import json
import os

homework_list = []  # In-memory storage for Homework objects
# Store checked state for each row (by index)
checked_rows = set()
selected_edit_row = {'idx': None}
HOMEWORK_FILE = "homework_data.json"  # File to store homework data

# Helper for date selection
def get_date_from_combobox(year_var, month_var, day_var):
    return f"{year_var.get()}-{month_var.get()}-{day_var.get()}"

# Function to refresh the homework list display, with optional filter
def refresh_homework(tree, filter_text=""):
    for row in tree.get_children():
        tree.delete(row)
    filter_text = filter_text.lower()
    for idx, hw in enumerate(homework_list):
        if (
            filter_text in hw.subject.lower() or
            filter_text in hw.title.lower() or
            filter_text in hw.status.lower()
        ):
            checked = '☑' if idx in checked_rows else '☐'
            time_required = ''
            if isinstance(hw, TimedHomework):
                time_required = str(hw.time_required)
            tree.insert('', 'end', iid=idx, values=(checked, hw.subject, hw.title, hw.due_date, hw.status, time_required))

# Function to add homework
def add_homework(subject, title, description, due_entry, status, tree, add_win, is_timed=False, time_required_entry=None):
    due_date = due_entry.get()
    if not subject or not title or not due_date:
        messagebox.showwarning("Input Error", "Subject, Title, and Due Date are required.")
        return
    try:
        datetime.strptime(due_date, "%Y-%m-%d")
    except ValueError:
        messagebox.showwarning("Input Error", "Due Date must be in YYYY-MM-DD format.")
        return
    if is_timed and time_required_entry is not None:
        try:
            time_required = int(time_required_entry.get())
        except ValueError:
            messagebox.showwarning("Input Error", "Time Required must be an integer (minutes).")
            return
        homework_list.append(TimedHomework(subject, title, description, due_date, status, time_required))
    else:
        homework_list.append(Homework(subject, title, description, due_date, status))
    save_homework_data()  # Save data after adding
    refresh_homework(tree)
    add_win.destroy()

# Function to edit homework
def edit_homework(idx, subject, title, description, due_entry, status, tree, edit_win):
    due_date = due_entry.get()
    if not subject or not title or not due_date:
        messagebox.showwarning("Input Error", "Subject, Title, and Due Date are required.")
        return
    try:
        datetime.strptime(due_date, "%Y-%m-%d")
    except ValueError:
        messagebox.showwarning("Input Error", "Due Date must be in YYYY-MM-DD format.")
        return
    # Check if user wants TimedHomework
    is_timed = getattr(edit_win, 'is_timed_var', None)
    if is_timed and is_timed.get():
        try:
            time_required = int(edit_win.time_required_entry.get())
        except ValueError:
            messagebox.showwarning("Input Error", "Time Required must be an integer (minutes).")
            return
        homework_list[idx] = TimedHomework(subject, title, description, due_date, status, time_required)
    else:
        homework_list[idx] = Homework(subject, title, description, due_date, status)
    save_homework_data()  # Save data after editing
    refresh_homework(tree)
    edit_win.destroy()

# Function to delete homework
def delete_homework(tree):
    if not checked_rows:
        messagebox.showwarning("No selection", "Please check one or more homework entries to delete.")
        return
    if len(checked_rows) == 1:
        msg = "Are you sure you want to delete this homework entry?"
    else:
        msg = f"Are you sure you want to delete these {len(checked_rows)} homework entries?"
    confirm = messagebox.askyesno("Confirm Delete", msg)
    if confirm:
        for idx in sorted(checked_rows, reverse=True):
            del homework_list[idx]
        checked_rows.clear()
        save_homework_data()  # Save data after deleting
        refresh_homework(tree)

# Function to open the add homework window
def open_add_homework(tree):
    add_win = tk.Toplevel()
    add_win.title("Add Homework")
    add_win.geometry("350x420")  # Increased height for better visibility

    tk.Label(add_win, text="Subject:").pack(anchor='w', padx=10, pady=(10,0))
    subject_entry = tk.Entry(add_win)
    subject_entry.pack(fill='x', padx=10)

    tk.Label(add_win, text="Title:").pack(anchor='w', padx=10, pady=(10,0))
    title_entry = tk.Entry(add_win)
    title_entry.pack(fill='x', padx=10)

    tk.Label(add_win, text="Description:").pack(anchor='w', padx=10, pady=(10,0))
    desc_entry = tk.Entry(add_win)
    desc_entry.pack(fill='x', padx=10)

    tk.Label(add_win, text="Due Date (YYYY-MM-DD):").pack(anchor='w', padx=10, pady=(10,0))
    due_entry = tk.Entry(add_win)
    due_entry.pack(fill='x', padx=10)

    tk.Label(add_win, text="Status:").pack(anchor='w', padx=10, pady=(10,0))
    status_var = tk.StringVar(value="Pending")
    status_menu = ttk.Combobox(add_win, textvariable=status_var, values=["Pending", "Completed"], state="readonly")
    status_menu.pack(fill='x', padx=10)

    # Option to add TimedHomework
    is_timed_var = tk.BooleanVar()
    timed_frame = tk.Frame(add_win)
    timed_frame.pack(fill='x', padx=10, pady=(10,0))
    tk.Checkbutton(timed_frame, text="Timed Homework (add time required)", variable=is_timed_var).pack(anchor='w')
    time_required_label = tk.Label(add_win, text="Time Required (minutes):")
    # Use Spinbox for user-friendly time input
    time_required_entry = tk.Spinbox(add_win, from_=1, to=1440, width=10)

    def toggle_timed():
        if is_timed_var.get():
            time_required_label.pack(anchor='w', padx=10, pady=(10,0))
            time_required_entry.pack(fill='x', padx=10)
        else:
            time_required_label.pack_forget()
            time_required_entry.pack_forget()
    is_timed_var.trace_add('write', lambda *args: toggle_timed())

    tk.Button(add_win, text="Add Homework", command=lambda: add_homework(
        subject_entry.get(), title_entry.get(), desc_entry.get(), due_entry, status_var.get(), tree, add_win, is_timed_var.get(), time_required_entry if is_timed_var.get() else None)).pack(pady=15)

# Function to open the edit homework window
def open_edit_homework(tree):
    global selected_edit_row
    idx = selected_edit_row.get('idx')
    if idx is None:
        messagebox.showwarning("No selection", "Please click a row (not the checkbox) to select a homework entry to edit.")
        return
    hw = homework_list[idx]

    edit_win = tk.Toplevel()
    edit_win.title("Edit Homework")
    edit_win.geometry("350x400")

    tk.Label(edit_win, text="Subject:").pack(anchor='w', padx=10, pady=(10,0))
    subject_entry = tk.Entry(edit_win)
    subject_entry.insert(0, hw.subject)
    subject_entry.pack(fill='x', padx=10)

    tk.Label(edit_win, text="Title:").pack(anchor='w', padx=10, pady=(10,0))
    title_entry = tk.Entry(edit_win)
    title_entry.insert(0, hw.title)
    title_entry.pack(fill='x', padx=10)

    tk.Label(edit_win, text="Description:").pack(anchor='w', padx=10, pady=(10,0))
    desc_entry = tk.Entry(edit_win)
    desc_entry.insert(0, hw.description)
    desc_entry.pack(fill='x', padx=10)

    tk.Label(edit_win, text="Due Date (YYYY-MM-DD):").pack(anchor='w', padx=10, pady=(10,0))
    due_entry = tk.Entry(edit_win)
    due_entry.insert(0, hw.due_date)
    due_entry.pack(fill='x', padx=10)

    tk.Label(edit_win, text="Status:").pack(anchor='w', padx=10, pady=(10,0))
    status_var = tk.StringVar(value=hw.status)
    status_menu = ttk.Combobox(edit_win, textvariable=status_var, values=["Pending", "Completed"], state="readonly")
    status_menu.pack(fill='x', padx=10)

    # Checkbox to enable/disable TimedHomework
    is_timed_var = tk.BooleanVar(value=isinstance(hw, TimedHomework))
    timed_frame = tk.Frame(edit_win)
    timed_frame.pack(fill='x', padx=10, pady=(10,0))
    tk.Checkbutton(timed_frame, text="Timed Homework (add time required)", variable=is_timed_var).pack(anchor='w')
    time_required_label = tk.Label(edit_win, text="Time Required (minutes):")
    time_required_entry = tk.Spinbox(edit_win, from_=1, to=1440, width=10)
    if isinstance(hw, TimedHomework):
        time_required_entry.delete(0, 'end')
        time_required_entry.insert(0, hw.time_required)
    else:
        time_required_entry.delete(0, 'end')
        time_required_entry.insert(0, 30)

    def toggle_timed():
        if is_timed_var.get():
            time_required_label.pack(anchor='w', padx=10, pady=(10,0))
            time_required_entry.pack(fill='x', padx=10)
        else:
            time_required_label.pack_forget()
            time_required_entry.pack_forget()
    is_timed_var.trace_add('write', lambda *args: toggle_timed())
    # Initial state
    if is_timed_var.get():
        time_required_label.pack(anchor='w', padx=10, pady=(10,0))
        time_required_entry.pack(fill='x', padx=10)

    # Attach toplevel attributes for access in edit_homework
    edit_win.is_timed_var = is_timed_var
    edit_win.time_required_entry = time_required_entry

    tk.Button(edit_win, text="Save Changes", command=lambda: edit_homework(
        idx, subject_entry.get(), title_entry.get(), desc_entry.get(), due_entry, status_var.get(), tree, edit_win)).pack(pady=15)

# Function to load homework data from file
def load_homework_data():
    """Load homework data from JSON file"""
    global homework_list
    try:
        if os.path.exists(HOMEWORK_FILE):
            with open(HOMEWORK_FILE, 'r') as f:
                data = json.load(f)
                homework_list = [Homework.from_dict(d) for d in data]
        else:
            homework_list = []
    except Exception as e:
        print(f"Error loading homework data: {e}")
        homework_list = []

# Function to save homework data to file
def save_homework_data():
    """Save homework data to JSON file"""
    try:
        with open(HOMEWORK_FILE, 'w') as f:
            json.dump([hw.to_dict() for hw in homework_list], f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving homework data: {e}")
        messagebox.showerror("Save Error", f"Failed to save homework data: {e}")
        return False

# Main Homework Planner window
def open_homework_planner_window():
    # Load homework data when window opens
    load_homework_data()
    
    hw_win = tk.Toplevel()
    hw_win.title("Homework Planner")
    hw_win.geometry("800x450")  # Increased width for better column visibility

    tk.Label(hw_win, text="Homework Planner", font=("Segoe UI", 16, "bold")).pack(pady=10)

    # Search bar
    search_frame = tk.Frame(hw_win)
    search_frame.pack(fill='x', padx=10, pady=(0, 5))
    tk.Label(search_frame, text="Search:").pack(side='left')
    search_var = tk.StringVar()
    search_entry = tk.Entry(search_frame, textvariable=search_var)
    search_entry.pack(side='left', fill='x', expand=True, padx=(5, 0))


    columns = ("Select", "Subject", "Title", "Due Date", "Status", "Time Required")
    tree = ttk.Treeview(hw_win, columns=columns, show='headings', selectmode='none')
    tree.heading("Select", text="☐", anchor='center')
    tree.column("Select", width=40, anchor='center', stretch=False)
    tree.heading("Subject", text="Subject")
    tree.column("Subject", width=120, anchor='center')
    tree.heading("Title", text="Title")
    tree.column("Title", width=180, anchor='center')
    tree.heading("Due Date", text="Due Date")
    tree.column("Due Date", width=110, anchor='center')
    tree.heading("Status", text="Status")
    tree.column("Status", width=100, anchor='center')
    tree.heading("Time Required", text="Time Required (min)")
    tree.column("Time Required", width=130, anchor='center')
    tree.pack(fill='both', expand=True, padx=10, pady=10)

    # Add click event to toggle checkbox
    def on_tree_click(event):
        region = tree.identify("region", event.x, event.y)
        col = tree.identify_column(event.x)
        row = tree.identify_row(event.y)
        if region == "cell":
            if col == "#1":  # Checkbox column
                if row:
                    idx = int(row)
                    if idx in checked_rows:
                        checked_rows.remove(idx)
                    else:
                        checked_rows.add(idx)
                    refresh_homework(tree, search_var.get())
            else:
                # Select row for editing
                if row:
                    idx = int(row)
                    global selected_edit_row
                    selected_edit_row['idx'] = idx
                    # Remove selection from all rows
                    for item in tree.get_children():
                        tree.item(item, tags=())
                    # Highlight selected row
                    tree.item(row, tags=('selected',))
    tree.bind("<Button-1>", on_tree_click)
    tree.tag_configure('selected', background='#cce5ff')

    def on_search(*args):
        refresh_homework(tree, search_var.get())

    search_var.trace_add('write', on_search)

    refresh_homework(tree)

    btn_frame = tk.Frame(hw_win)
    btn_frame.pack(pady=10)
    tk.Button(btn_frame, text="Add Homework", command=lambda: open_add_homework(tree)).pack(side='left', padx=5)
    tk.Button(btn_frame, text="Edit Homework", command=lambda: open_edit_homework(tree)).pack(side='left', padx=5)
    tk.Button(btn_frame, text="Delete Homework", command=lambda: delete_homework(tree)).pack(side='left', padx=5)
    tk.Button(btn_frame, text="Save Data", command=lambda: save_homework_data() and messagebox.showinfo("Success", "Homework data saved successfully!")).pack(side='left', padx=5)

# For main.py: import and call open_homework_planner_window() 