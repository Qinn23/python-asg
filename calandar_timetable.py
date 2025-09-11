import tkinter as tk
from tkinter import messagebox
import calendar
from datetime import datetime
import json
import os


# ===== Inheritance =====
class BaseEvent:
    """Base class for all events"""
    def __init__(self, title, category, time):
        self.title = title
        self.category = category
        self.time = time

    def toDict(self):
        """Convert event into dictionary for JSON saving"""
        return {"title": self.title, "category": self.category, "time": self.time}


class AssignmentEvent(BaseEvent):
    def __init__(self, title, time):
        super().__init__(title, "Assignment", time)


class TimetableEvent(BaseEvent):
    def __init__(self, title, time):
        super().__init__(title, "Timetable", time)


class OtherEvent(BaseEvent):
    def __init__(self, title, time):
        super().__init__(title, "Others", time)


# ===== Main Calendar App =====
class CalendarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📅 Calendar App")
        self.root.geometry("950x700")
        self.root.configure(bg="#f8f9fa")
        self.activeForm = None  # track Add/Edit popup

        # File to save/load events
        self.jsonFile = "calendar_data.json"

        # Load events into memory (dictionary)
        self.events = self.loadEvents()

        # Category colors
        self.categoryColors = {
            "Assignment": "#d68a8a",
            "Timetable": "#6cb287",
            "Others": "#4eb5f0"
        }

        # === Top Frame (Year/Month selection) ===
        topFrame = tk.Frame(root, bg="#f8f9fa")
        topFrame.pack(pady=10)

        tk.Label(topFrame, text="Year:", bg="#f8f9fa").grid(row=0, column=0, padx=5)
        self.yearVar = tk.IntVar(value=datetime.now().year)
        yearOptions = [y for y in range(2000, 2101)]
        yearMenu = tk.OptionMenu(topFrame, self.yearVar, *yearOptions, command=lambda e: self.drawCalendar())
        yearMenu.grid(row=0, column=1, padx=5)

        tk.Label(topFrame, text="Month:", bg="#f8f9fa").grid(row=0, column=2, padx=5)
        self.monthVar = tk.StringVar(value=calendar.month_name[datetime.now().month])
        monthOptions = list(calendar.month_name)[1:]
        monthMenu = tk.OptionMenu(topFrame, self.monthVar, *monthOptions, command=lambda e: self.drawCalendar())
        monthMenu.grid(row=0, column=3, padx=5)

        # === Calendar Frame ===
        self.calendarFrame = tk.Frame(root, bg="#f8f9fa")
        self.calendarFrame.pack(fill="both", expand=True)

        # === Bottom Buttons ===
        bottomFrame = tk.Frame(root, bg="#f8f9fa")
        bottomFrame.pack(pady=10)

        tk.Button(bottomFrame, text="❌ Delete Event", command=self.deleteEvent,
                  bg="#dc3545", fg="white", width=12).grid(row=0, column=1, padx=10)

        self.drawCalendar()

    # === Load events from JSON file ===
    def loadEvents(self):
        try:
            if os.path.exists(self.jsonFile):
                with open(self.jsonFile, "r") as f:
                    return json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load events: {e}")
        return {}

    # === Save events into JSON file ===
    def saveEvents(self):
        try:
            with open(self.jsonFile, "w") as f:
                json.dump(self.events, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save events: {e}")

    # === Draw monthly calendar ===
    def drawCalendar(self):
        # Clear old calendar
        for widget in self.calendarFrame.winfo_children():
            widget.destroy()

        # Month-Year title
        tk.Label(self.calendarFrame, text=f"{self.monthVar.get()} {self.yearVar.get()}",
                 font=("Segoe UI", 16, "bold"), bg="#f8f9fa").grid(row=0, column=0, columnspan=7, pady=10)

        # Weekday header row
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for col, day in enumerate(days):
            tk.Label(self.calendarFrame, text=day, font=("Segoe UI", 10, "bold"),
                     bg="#8e9298", relief="ridge", width=14, height=2).grid(row=1, column=col, sticky="nsew")

        # Generate calendar matrix
        year, month = self.yearVar.get(), list(calendar.month_name).index(self.monthVar.get())
        monthCalendar = calendar.monthcalendar(year, month)

        for row, week in enumerate(monthCalendar, start=2):
            for col, day in enumerate(week):
                if day != 0:
                    dateStr = f"{year}-{month:02d}-{day:02d}"
                    today = datetime.now().date()
                    cellDate = datetime(year, month, day).date()

                    # Highlight background
                    if cellDate == today:
                        dayBg = "#90EE90"
                    elif col in (5, 6):
                        dayBg = "#ADD8E6"
                    else:
                        dayBg = "white"

                    frame = tk.Frame(self.calendarFrame, relief="ridge", bd=1, bg=dayBg)
                    frame.grid(row=row, column=col, sticky="nsew", padx=1, pady=1)

                    tk.Label(frame, text=str(day), anchor="nw", bg=dayBg).pack(fill="x")

                    # Add event labels (clickable for editing)
                    for idx, ev in enumerate(self.events.get(dateStr, [])):
                        label = tk.Label(frame, text=f"{ev['time']} {ev['title']}",
                                         bg=self.categoryColors[ev["category"]], fg="white",
                                         font=("Segoe UI", 9), anchor="w")
                        label.pack(fill="x", padx=2, pady=1)

                        # Bind click → open edit form
                        label.bind("<Button-1>", lambda e, d=dateStr, i=idx, ev=ev: self.openEventForm(d, True, ev, i))

                    # Click empty cell → add new event
                    frame.bind("<Button-1>", lambda e, d=dateStr: self.openEventForm(d))

        for i in range(7):
            self.calendarFrame.grid_columnconfigure(i, weight=1)
        for i in range(len(monthCalendar) + 2):
            self.calendarFrame.grid_rowconfigure(i, weight=1)

    # === Event creation/edit form ===
    def openEventForm(self, dateStr=None, editMode=False, existing=None, eventIndex=None):
        # Prevent multiple popups
        if self.activeForm and tk.Toplevel.winfo_exists(self.activeForm):
            self.activeForm.lift()
            return

        self.activeForm = tk.Toplevel(self.root)
        form = self.activeForm
        form.title("✏️ Edit Event" if editMode else "➕ Add Event")
        form.geometry("300x300")
        form.configure(bg="#f8f9fa")

        # Reset tracker when window is closed
        def onClose():
            self.activeForm = None
            form.destroy()
        form.protocol("WM_DELETE_WINDOW", onClose)

        if not dateStr:
            messagebox.showerror("Error", "Please select a date on the calendar.")
            return

        # --- Input fields ---
        tk.Label(form, text="Title:", bg="#f8f9fa").pack(pady=5)
        titleEntry = tk.Entry(form, width=25)
        titleEntry.pack()

        tk.Label(form, text="Category:", bg="#f8f9fa").pack(pady=5)
        categoryVar = tk.StringVar(value="Assignment")
        tk.OptionMenu(form, categoryVar, *self.categoryColors.keys()).pack()

        tk.Label(form, text="Time (HH:MM):", bg="#f8f9fa").pack(pady=5)
        timeEntry = tk.Entry(form, width=25)
        timeEntry.pack()

        # Pre-fill when editing
        if editMode and existing:
            titleEntry.insert(0, existing["title"])
            categoryVar.set(existing["category"])
            timeEntry.insert(0, existing["time"])

        # --- Save button handler ---
        def saveEvent():
            title = titleEntry.get().strip()
            category = categoryVar.get()
            timeStr = timeEntry.get().strip()

            # Validation
            if not title:
                messagebox.showerror("Error", "Title cannot be empty!")
                return
            if any(char.isdigit() or (not char.isalnum() and char != " ") for char in title):
                messagebox.showerror("Error", "Title cannot contain numbers or symbols!")
                return
            try:
                datetime.strptime(timeStr, "%H:%M")
            except:
                messagebox.showerror("Error", "Invalid time format! Use HH:MM (24-hour).")
                return

            # Save (edit or add)
            if editMode and eventIndex is not None:
                self.events[dateStr][eventIndex] = {
                    "title": title,
                    "category": category,
                    "time": timeStr
                }
            else:
                if dateStr not in self.events:
                    self.events[dateStr] = []
                self.events[dateStr].append({
                    "title": title,
                    "category": category,
                    "time": timeStr
                })

            # Save + refresh
            self.saveEvents()
            self.drawCalendar()
            self.activeForm = None
            form.destroy()

        # --- Save button ---
        tk.Button(form, text="Save Event", command=saveEvent,
                bg="#28a745", fg="white", width=12).pack(pady=15)


    # === Delete events form with category grouping ===
    def deleteEvent(self):
        if self.activeForm and tk.Toplevel.winfo_exists(self.activeForm):
            self.activeForm.lift()
            return

        self.activeForm = tk.Toplevel(self.root)
        form = self.activeForm
        form.title("❌ Delete Event")
        form.geometry("450x300")
        form.configure(bg="#f8f9fa")

        def onClose():
            self.activeForm = None
            form.destroy()
        form.protocol("WM_DELETE_WINDOW", onClose)

        if not self.events:
            messagebox.showinfo("Info", "No events to delete.")
            return

        form.title("❌ Delete Event")
        form.geometry("600x400")
        form.configure(bg="#f8f9fa")

        tk.Label(form, text="Select an event to delete (grouped by category):", bg="#f8f9fa").pack(pady=5)

        eventList = []
        listboxes = {}
        frame = tk.Frame(form, bg="#f8f9fa")
        frame.pack(fill="both", expand=True)

        # Create a Listbox per category
        for idx, category in enumerate(self.categoryColors.keys()):
            catFrame = tk.LabelFrame(frame, text=category, bg="#f8f9fa",
                                    fg=self.categoryColors[category], padx=5, pady=5)
            catFrame.grid(row=0, column=idx, padx=5, pady=5, sticky="nsew")

            lb = tk.Listbox(catFrame, width=30, height=12, selectmode=tk.SINGLE,
                            bg="white", fg="black", highlightbackground=self.categoryColors[category])
            lb.pack()
            listboxes[category] = lb

        # Populate events into correct listbox
        for date, events in self.events.items():
            for idx, ev in enumerate(events):
                line = f"{date} | {ev['time']} | {ev['title']}"
                eventList.append((date, idx, ev))
                listboxes[ev["category"]].insert(tk.END, line)

        def deleteSelected():
            for category, lb in listboxes.items():
                selection = lb.curselection()
                if selection:
                    index = selection[0]
                    chosenDate, evIndex, ev = [(d, i, e) for (d, i, e) in eventList if e["category"] == category][index]
                    try:
                        del self.events[chosenDate][evIndex]
                        if not self.events[chosenDate]:
                            del self.events[chosenDate]
                        self.saveEvents()
                        self.drawCalendar()
                        form.destroy()
                        messagebox.showinfo("Deleted", "Event deleted successfully!")
                        return
                    except Exception as e:
                        messagebox.showerror("Error", f"Could not delete event: {e}")
                        return
            messagebox.showwarning("Warning", "Please select an event to delete.")

        tk.Button(form, text="Delete Selected", command=deleteSelected,
            bg="#dc3545", fg="white").pack(pady=10)


# Run app
if __name__ == "__main__":
    root = tk.Tk()
    app = CalendarApp(root)
    root.mainloop()