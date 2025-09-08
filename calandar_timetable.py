import tkinter as tk
from tkinter import simpledialog, messagebox, Toplevel
import calendar
from datetime import datetime

class CalendarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📅 Calendar / Timetable App")
        self.root.geometry("700x550")
        self.root.config(bg="#f4f4f4")
        self.events = {}  # { "YYYY-MM-DD": [{"title": "...", "category": "..."}] }

        self.current_year = datetime.now().year
        self.current_month = datetime.now().month
        self.today = datetime.now().strftime("%Y-%m-%d")

        # Header
        self.header = tk.Label(root, text="", font=("Segoe UI", 20, "bold"), bg="#f4f4f4", fg="#333")
        self.header.pack(pady=15)

        # Navigation
        nav_frame = tk.Frame(root, bg="#f4f4f4")
        nav_frame.pack()
        tk.Button(nav_frame, text="◀ Prev", command=self.prev_month, width=10, bg="#ddd").grid(row=0, column=0, padx=10)
        tk.Button(nav_frame, text="Next ▶", command=self.next_month, width=10, bg="#ddd").grid(row=0, column=1, padx=10)
        tk.Button(nav_frame, text="Jump to Date", command=self.jump_to_date, bg="#aaa", fg="white").grid(row=0, column=2, padx=10)

        # Calendar Grid
        self.calendar_frame = tk.Frame(root, bg="#f4f4f4")
        self.calendar_frame.pack(pady=20)

        # Upcoming Events
        self.events_frame = tk.Frame(root, bg="#ffffff", bd=2, relief="groove")
        self.events_frame.pack(fill="x", padx=20, pady=10)
        tk.Label(self.events_frame, text="📌 Upcoming Events", font=("Arial", 12, "bold"), bg="white").pack(anchor="w", padx=10, pady=5)
        self.upcoming_list = tk.Listbox(self.events_frame, height=5)
        self.upcoming_list.pack(fill="x", padx=10, pady=5)

        self.draw_calendar()
        self.update_upcoming_events()

    def draw_calendar(self):
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        # Update header
        self.header.config(text=f"{calendar.month_name[self.current_month]} {self.current_year}")

        # Weekday labels
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for col, day in enumerate(days):
            tk.Label(self.calendar_frame, text=day, font=("Arial", 10, "bold"), bg="#f4f4f4").grid(row=0, column=col, padx=5, pady=5)

        # Dates
        month_calendar = calendar.monthcalendar(self.current_year, self.current_month)
        for row, week in enumerate(month_calendar, start=1):
            for col, day in enumerate(week):
                if day != 0:
                    date_str = f"{self.current_year}-{self.current_month:02d}-{day:02d}"
                    btn = tk.Button(
                        self.calendar_frame,
                        text=str(day),
                        width=8,
                        height=3,
                        relief="groove",
                        bg="white",
                        command=lambda d=date_str: self.open_day(d)
                    )

                    # Highlight today
                    if date_str == self.today:
                        btn.config(bg="#4CAF50", fg="white")

                    # Weekends in light blue
                    if col == 5 or col == 6:
                        btn.config(bg="#e3f2fd")

                    btn.grid(row=row, column=col, padx=3, pady=3)

    def open_day(self, date_str):
        top = Toplevel(self.root)
        top.title(f"Events on {date_str}")
        top.geometry("350x350")

        tk.Label(top, text=f"Events on {date_str}", font=("Arial", 12, "bold")).pack(pady=10)

        events = self.events.get(date_str, [])
        listbox = tk.Listbox(top, width=45, height=12)
        listbox.pack(pady=10)
        for ev in events:
            listbox.insert(tk.END, f"{ev['title']} [{ev['category']}]")

        def add_event():
            title = simpledialog.askstring("Add Event", "Enter event title:")
            category = simpledialog.askstring("Category", "Enter category (Class, Meeting, etc):")
            if title:
                self.events.setdefault(date_str, []).append({"title": title, "category": category or "General"})
                listbox.insert(tk.END, f"{title} [{category}]")
                self.update_upcoming_events()

        def delete_event():
            selection = listbox.curselection()
            if selection:
                idx = selection[0]
                del self.events[date_str][idx]
                listbox.delete(idx)
                self.update_upcoming_events()

        tk.Button(top, text="Add Event", command=add_event, bg="#4CAF50", fg="white").pack(side="left", padx=20, pady=10)
        tk.Button(top, text="Delete Event", command=delete_event, bg="#f44336", fg="white").pack(side="right", padx=20, pady=10)

    def update_upcoming_events(self):
        self.upcoming_list.delete(0, tk.END)
        all_events = []
        for date, items in self.events.items():
            for ev in items:
                all_events.append((date, ev["title"], ev["category"]))

        all_events.sort(key=lambda x: x[0])
        for d, title, cat in all_events[:5]:  # Show only next 5
            self.upcoming_list.insert(tk.END, f"{d}: {title} [{cat}]")

    def jump_to_date(self):
        year = simpledialog.askinteger("Jump to Date", "Enter year (YYYY):")
        month = simpledialog.askinteger("Jump to Date", "Enter month (1-12):")
        if year and month and 1 <= month <= 12:
            self.current_year = year
            self.current_month = month
            self.draw_calendar()

    def prev_month(self):
        self.current_month -= 1
        if self.current_month == 0:
            self.current_month = 12
            self.current_year -= 1
        self.draw_calendar()

    def next_month(self):
        self.current_month += 1
        if self.current_month == 13:
            self.current_month = 1
            self.current_year += 1
        self.draw_calendar()

# Run App
if __name__ == "__main__":
    root = tk.Tk()
    app = CalendarApp(root)
    root.mainloop()
