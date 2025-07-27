import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os

homework_list = []  # In-memory storage for homework tasks
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
            filter_text in hw['subject'].lower() or
            filter_text in hw['title'].lower() or
            filter_text in hw['status'].lower()
        ):
            tree.insert('', 'end', iid=idx, values=(hw['subject'], hw['title'], hw['due_date'], hw['status']))

# Function to add homework
def add_homework(subject, title, description, due_entry, status, tree, add_win):
    due_date = due_entry.get()
    if not subject or not title or not due_date:
        messagebox.showwarning("Input Error", "Subject, Title, and Due Date are required.")
        return
    try:
        datetime.strptime(due_date, "%Y-%m-%d")
    except ValueError:
        messagebox.showwarning("Input Error", "Due Date must be in YYYY-MM-DD format.")
        return
    homework_list.append({
        'subject': subject,
        'title': title,
        'description': description,
        'due_date': due_date,
        'status': status
    })
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
    homework_list[idx] = {
        'subject': subject,
        'title': title,
        'description': description,
        'due_date': due_date,
        'status': status
    }
    save_homework_data()  # Save data after editing
    refresh_homework(tree)
    edit_win.destroy()

# Function to delete homework
def delete_homework(tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("No selection", "Please select a homework entry to delete.")
        return
    idx = int(selected[0])
    confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this homework entry?")
    if confirm:
        del homework_list[idx]
        save_homework_data()  # Save data after deleting
        refresh_homework(tree)

# Function to open the add homework window
def open_add_homework(tree):
    add_win = tk.Toplevel()
    add_win.title("Add Homework")
    add_win.geometry("350x300")

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

    tk.Button(add_win, text="Add Homework", command=lambda: add_homework(
        subject_entry.get(), title_entry.get(), desc_entry.get(), due_entry, status_var.get(), tree, add_win)).pack(pady=15)

# Function to open the edit homework window
def open_edit_homework(tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("No selection", "Please select a homework entry to edit.")
        return
    idx = int(selected[0])
    hw = homework_list[idx]

    edit_win = tk.Toplevel()
    edit_win.title("Edit Homework")
    edit_win.geometry("350x300")

    tk.Label(edit_win, text="Subject:").pack(anchor='w', padx=10, pady=(10,0))
    subject_entry = tk.Entry(edit_win)
    subject_entry.insert(0, hw['subject'])
    subject_entry.pack(fill='x', padx=10)

    tk.Label(edit_win, text="Title:").pack(anchor='w', padx=10, pady=(10,0))
    title_entry = tk.Entry(edit_win)
    title_entry.insert(0, hw['title'])
    title_entry.pack(fill='x', padx=10)

    tk.Label(edit_win, text="Description:").pack(anchor='w', padx=10, pady=(10,0))
    desc_entry = tk.Entry(edit_win)
    desc_entry.insert(0, hw['description'])
    desc_entry.pack(fill='x', padx=10)

    tk.Label(edit_win, text="Due Date (YYYY-MM-DD):").pack(anchor='w', padx=10, pady=(10,0))
    due_entry = tk.Entry(edit_win)
    due_entry.insert(0, hw['due_date'])
    due_entry.pack(fill='x', padx=10)

    tk.Label(edit_win, text="Status:").pack(anchor='w', padx=10, pady=(10,0))
    status_var = tk.StringVar(value=hw['status'])
    status_menu = ttk.Combobox(edit_win, textvariable=status_var, values=["Pending", "Completed"], state="readonly")
    status_menu.pack(fill='x', padx=10)

    tk.Button(edit_win, text="Save Changes", command=lambda: edit_homework(
        idx, subject_entry.get(), title_entry.get(), desc_entry.get(), due_entry, status_var.get(), tree, edit_win)).pack(pady=15)

# Function to load homework data from file
def load_homework_data():
    """Load homework data from JSON file"""
    global homework_list
    try:
        if os.path.exists(HOMEWORK_FILE):
            with open(HOMEWORK_FILE, 'r') as f:
                homework_list = json.load(f)
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
            json.dump(homework_list, f, indent=2)
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
    hw_win.geometry("600x450")

    tk.Label(hw_win, text="Homework Planner", font=("Segoe UI", 16, "bold")).pack(pady=10)

    # Search bar
    search_frame = tk.Frame(hw_win)
    search_frame.pack(fill='x', padx=10, pady=(0, 5))
    tk.Label(search_frame, text="Search:").pack(side='left')
    search_var = tk.StringVar()
    search_entry = tk.Entry(search_frame, textvariable=search_var)
    search_entry.pack(side='left', fill='x', expand=True, padx=(5, 0))

    columns = ("Subject", "Title", "Due Date", "Status")
    tree = ttk.Treeview(hw_win, columns=columns, show='headings')
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=120)
    tree.pack(fill='both', expand=True, padx=10, pady=10)

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