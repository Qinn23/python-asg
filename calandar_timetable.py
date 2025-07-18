import tkinter as tk
from tkinter import messagebox
from datetime import datetime

events = []  # Store events here

def open_calendar_app_window():
    # Create a new window when called from main.py
    cal_win = tk.Toplevel()
    cal_win.title("🗓️ Simple Timetable App")
    cal_win.geometry("450x500")
    cal_win.resizable(False, False)

    # --- Widgets below ---
    tk.Label(cal_win, text="Event Title:").pack()
    title_entry = tk.Entry(cal_win, width=40)
    title_entry.pack()

    tk.Label(cal_win, text="Date (YYYY-MM-DD):").pack()
    date_entry = tk.Entry(cal_win, width=40)
    date_entry.pack()

    tk.Label(cal_win, text="Time (HH:MM):").pack()
    time_entry = tk.Entry(cal_win, width=40)
    time_entry.pack()

    tk.Label(cal_win, text="Category:").pack()
    category_entry = tk.Entry(cal_win, width=40)
    category_entry.pack()

    event_listbox = tk.Listbox(cal_win, width=60, height=15)
    event_listbox.pack(pady=10)

    def add_event():
        title = title_entry.get()
        date = date_entry.get()
        time = time_entry.get()
        category = category_entry.get()

        try:
            dt = datetime.strptime(date + " " + time, "%Y-%m-%d %H:%M")
            events.append({
                "title": title,
                "datetime": dt,
                "category": category
            })
            messagebox.showinfo("Success", "Event added!")
            update_event_list()
            clear_entries()
        except ValueError:
            messagebox.showerror("Error", "Invalid date/time format!")

    def update_event_list():
        event_listbox.delete(0, tk.END)
        for event in sorted(events, key=lambda x: x["datetime"]):
            formatted = f"{event['datetime'].strftime('%Y-%m-%d %H:%M')} - {event['title']} [{event['category']}]"
            event_listbox.insert(tk.END, formatted)

    def clear_entries():
        title_entry.delete(0, tk.END)
        date_entry.delete(0, tk.END)
        time_entry.delete(0, tk.END)
        category_entry.delete(0, tk.END)

    # Button
    tk.Button(cal_win, text="Add Event", command=add_event, bg="#4CAF50", fg="white", width=20).pack(pady=10)
