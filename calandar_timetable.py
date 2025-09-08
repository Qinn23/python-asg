import tkinter as tk
from tkinter import messagebox
import calendar
from datetime import datetime
import json
import os


# ===== Inheritance Example =====
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
        self.root.geometry("900x650")
        self.root.configure(bg="#f8f9fa")

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

        tk.Button(bottomFrame, text="➕ Add Event", command=self.openEventForm,
                  bg="#28a745", fg="white", width=12).grid(row=0, column=0, padx=10)
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

        # Generate calendar matrix (weeks x days)
        year, month = self.yearVar.get(), list(calendar.month_name).index(self.monthVar.get())
        monthCalendar = calendar.monthcalendar(year, month)

        for row, week in enumerate(monthCalendar, start=2):
            for col, day in enumerate(week):
                if day != 0:  # Day exists
                    dateStr = f"{year}-{month:02d}-{day:02d}"
                    today = datetime.now().date()
                    cellDate = datetime(year, month, day).date()

                    # === Cell background selection (highlight today/weekends) ===
                    if cellDate == today:
                        dayBg = "#90EE90"  # light green
                    elif col in (5, 6):
                        dayBg = "#ADD8E6"  # light blue for weekends
                    else:
                        dayBg = "white"

                    # === Cell frame ===
                    frame = tk.Frame(self.calendarFrame, relief="ridge", bd=1, bg=dayBg)
                    frame.grid(row=row, column=col, sticky="nsew", padx=1, pady=1)

                    # Day label
                    tk.Label(frame, text=str(day), anchor="nw", bg=dayBg).pack(fill="x")

                    # Event previews in cell
                    for ev in self.events.get(dateStr, []):
                        tk.Label(frame, text=f"{ev['time']} {ev['title']}",
                                 bg=self.categoryColors[ev["category"]], fg="white",
                                 font=("Segoe UI", 9), anchor="w").pack(fill="x", padx=2, pady=1)

                    # Clickable to add/edit events
                    frame.bind("<Button-1>", lambda e, d=dateStr: self.openEventForm(d))

        # Expand grid
        for i in range(7):
            self.calendarFrame.grid_columnconfigure(i, weight=1)
        for i in range(len(monthCalendar) + 2):
            self.calendarFrame.grid_rowconfigure(i, weight=1)

    # === Event creation form ===
    def openEventForm(self, dateStr=None):
        form = tk.Toplevel(self.root)
        form.title("➕ Add Event")
        form.geometry("300x300")
        form.configure(bg="#f8f9fa")

        tk.Label(form, text="Title:", bg="#f8f9fa").pack(pady=5)
        titleEntry = tk.Entry(form, width=25)
        titleEntry.pack()

        tk.Label(form, text="Category:", bg="#f8f9fa").pack(pady=5)
        categoryVar = tk.StringVar(value="Assignment")
        tk.OptionMenu(form, categoryVar, *self.categoryColors.keys()).pack()

        tk.Label(form, text="Time (HH:MM):", bg="#f8f9fa").pack(pady=5)
        timeEntry = tk.Entry(form, width=25)
        timeEntry.pack()

        # Save button
        def saveEvent():
            title = titleEntry.get().strip()
            category = categoryVar.get()
            timeStr = timeEntry.get().strip()

            # === String Processing + Selection ===
            if not title:
                messagebox.showerror("Error", "Title cannot be empty!")
                return
            if any(char.isdigit() or not char.isalnum() and char != " " for char in title):
                messagebox.showerror("Error", "Title cannot contain numbers or symbols!")
                return

            try:
                datetime.strptime(timeStr, "%H:%M")  # validate HH:MM
            except:
                messagebox.showerror("Error", "Invalid time format! Use HH:MM (24-hour).")
                return

            # === Inheritance: Create event based on category ===
            if category == "Assignment":
                event = AssignmentEvent(title, timeStr)
            elif category == "Timetable":
                event = TimetableEvent(title, timeStr)
            else:
                event = OtherEvent(title, timeStr)

            if dateStr not in self.events:
                self.events[dateStr] = []
            self.events[dateStr].append(event.toDict())

            self.saveEvents()
            self.drawCalendar()
            form.destroy()

        tk.Button(form, text="Save Event", command=saveEvent, bg="#28a745", fg="white").pack(pady=20)

    # === Delete events form ===
    def deleteEvent(self):
        if not self.events:
            messagebox.showinfo("Info", "No events to delete.")
            return

        form = tk.Toplevel(self.root)
        form.title("❌ Delete Event")
        form.geometry("450x300")
        form.configure(bg="#f8f9fa")

        tk.Label(form, text="Select an event to delete:", bg="#f8f9fa").pack(pady=5)

        # Build a list of events with details
        eventList = []
        for date, events in self.events.items():
            for idx, ev in enumerate(events):
                line = f"{date} | {ev['time']} | {ev['title']} ({ev['category']})"
                eventList.append((date, idx, line))  # store date + index for deletion

        # Listbox to show all events
        listbox = tk.Listbox(form, width=60, height=10, selectmode=tk.SINGLE)
        listbox.pack(pady=10)
        for _, _, line in eventList:
            listbox.insert(tk.END, line)

        def deleteSelected():
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning("Warning", "Please select an event to delete.")
                return
            index = selection[0]
            date, evIndex, _ = eventList[index]

            # Remove that specific event
            try:
                del self.events[date][evIndex]
                if not self.events[date]:
                    del self.events[date]  # clean empty dates
                self.saveEvents()
                self.drawCalendar()
                form.destroy()
                messagebox.showinfo("Deleted", "Event deleted successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete event: {e}")

        tk.Button(form, text="Delete Selected", command=deleteSelected,
                  bg="#dc3545", fg="white").pack(pady=10)

# Run app
if __name__ == "__main__":
    root = tk.Tk()
    app = CalendarApp(root)
    root.mainloop()
