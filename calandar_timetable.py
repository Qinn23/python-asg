import tkinter as tk
from tkinter import messagebox
import calendar
from datetime import datetime
import json
import os

# =========================================================================
# ===== Inheritance ===================================
# =========================================================================

class BaseEvent:
    """Base class for all events (Encapsulation + Inheritance)"""
    def __init__(self, title, category, time):
        # Private attributes (Encapsulation)
        self.__title = title
        self.__category = category
        self.__time = time

    # Getter and Setter for title
    @property
    def title(self):
        return self.__title
    @title.setter
    def title(self, value):
        self.__title = value

    # Getter and Setter for category
    @property
    def category(self):
        return self.__category
    @category.setter
    def category(self, value):
        self.__category = value

    # Getter and Setter for time
    @property
    def time(self):
        return self.__time
    @time.setter
    def time(self, value):
        self.__time = value

    # Convert event object into dictionary for JSON storage
    def toDict(self):
        return {"title": self.__title, "category": self.__category, "time": self.__time}


class AssignmentEvent(BaseEvent):
    """Subclass for Assignment events (Inheritance)"""
    def __init__(self, title, time, description):
        super().__init__(title, "Assignment", time)
        self.__description = description

    # Getter/Setter for description
    @property
    def description(self):
        return self.__description
    @description.setter
    def description(self, value):
        self.__description = value

    def toDict(self):
        base = super().toDict()
        base["description"] = self.__description
        return base


class TimetableEvent(BaseEvent):
    """Subclass for Timetable events"""
    def __init__(self, title, startTime, endTime):
        super().__init__(title, "Timetable", None)  # don't pass formatted string
        self.__startTime = startTime
        self.__endTime = endTime

    @property
    def startTime(self):
        return self.__startTime
    @startTime.setter
    def startTime(self, value):
        self.__startTime = value

    @property
    def endTime(self):
        return self.__endTime
    @endTime.setter
    def endTime(self, value):
        self.__endTime = value

    @property
    def time(self):  
        """Override parent property dynamically → no duplicate storage"""
        return f"{self.__startTime}-{self.__endTime}"

    def toDict(self):
        base = super().toDict()
        base["startTime"] = self.__startTime
        base["endTime"] = self.__endTime
        return base

#! changes
class CollabEvent(BaseEvent):
    """Subclass for Collaborative events"""
    def __init__(self, title, time, participants=None):
        super().__init__(title, "Collab", time)
        self.__participants = participants if participants else []

    @property
    def participants(self):
        return self.__participants

    def addParticipant(self, name):
        if not name.strip() or any(ch.isdigit() for ch in name):
            raise ValueError("Invalid name")
        self.__participants.append(name.strip())

    def toDict(self):
        base = super().toDict()
        base["participants"] = self.__participants
        return base

# =========================================================================
# ===== Main Calendar App ================================
# =========================================================================

class CalendarApp:
    def __init__(self, root):
        # Window setup (GUI)
        self.root = root
        self.root.title("📅 Calendar App")
        self.root.geometry("950x700")
        self.root.configure(bg="#f8f9fa")
        self.activeForm = None   # Track active form window (to avoid multiple popups)

        # File for saving data (File Processing)
        self.jsonFile = "calendar_data.json"
        self.events = self.loadEvents()   # Load saved events

        # Category colors (Collections: dictionary)
        self.categoryColors = {
            "Assignment": "#d68a8a",
            "Timetable": "#6cb287",
            "Collab": "#4eb5f0"
        }

        # === Top Frame (Selection for Year/Month) ===
        topFrame = tk.Frame(root, bg="#f8f9fa")
        topFrame.pack(pady=10)

        # Year selection (Loop + OptionMenu)
        tk.Label(topFrame, text="Year:", bg="#f8f9fa").grid(row=0, column=0, padx=5)
        self.yearVar = tk.IntVar(value=datetime.now().year)
        yearOptions = [y for y in range(2000, 2101)]
        yearMenu = tk.OptionMenu(topFrame, self.yearVar, *yearOptions,
                                 command=lambda e: self.drawCalendar())
        yearMenu.grid(row=0, column=1, padx=5)

        # Month selection
        tk.Label(topFrame, text="Month:", bg="#f8f9fa").grid(row=0, column=2, padx=5)
        self.monthVar = tk.StringVar(value=calendar.month_name[datetime.now().month])
        monthOptions = list(calendar.month_name)[1:]
        monthMenu = tk.OptionMenu(topFrame, self.monthVar, *monthOptions,
                                  command=lambda e: self.drawCalendar())
        monthMenu.grid(row=0, column=3, padx=5)

        # === Calendar Frame ===
        self.calendarFrame = tk.Frame(root, bg="#f8f9fa")
        self.calendarFrame.pack(fill="both", expand=True)

        # === Bottom Buttons ===
        bottomFrame = tk.Frame(root, bg="#f8f9fa")
        bottomFrame.pack(pady=10)

        tk.Button(bottomFrame, text="❌ Delete Event", command=self.deleteEvent,
                  bg="#dc3545", fg="white", width=12).grid(row=0, column=1, padx=10)

        # Draw the initial calendar
        self.drawCalendar()


    # ===================================================================================
    # === File Handling ============================================================
    # ===================================================================================

    def loadEvents(self):
        """Load events from JSON file (File Processing + Exception Handling)"""
        try:
            if os.path.exists(self.jsonFile):
                with open(self.jsonFile, "r") as f:
                    return json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load events: {e}")
        return {}

    def saveEvents(self):
        """Save events back to JSON file"""
        try:
            with open(self.jsonFile, "w") as f:
                json.dump(self.events, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save events: {e}")


    # ===================================================================================
    # === Calendar Drawing ====================================================
    # ===================================================================================
    def drawCalendar(self):
        """Draw the calendar grid (Loops + Selection statements)"""
        # Clear old calendar
        for widget in self.calendarFrame.winfo_children():
            widget.destroy()

        # Header (Month + Year)
        tk.Label(self.calendarFrame, text=f"{self.monthVar.get()} {self.yearVar.get()}",
                 font=("Segoe UI", 16, "bold"), bg="#f8f9fa").grid(row=0, column=0, columnspan=7, pady=10)

        # Weekday header
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for col, day in enumerate(days):
            tk.Label(self.calendarFrame, text=day, font=("Segoe UI", 10, "bold"),
                     bg="#8e9298", relief="ridge", width=14, height=2).grid(row=1, column=col, sticky="nsew")

        # Generate month days
        year, month = self.yearVar.get(), list(calendar.month_name).index(self.monthVar.get())
        monthCalendar = calendar.monthcalendar(year, month)

        # Loop through weeks and days
        for row, week in enumerate(monthCalendar, start=2):
            for col, day in enumerate(week):
                if day != 0:   # Selection: only draw valid days
                    dateStr = f"{year}-{month:02d}-{day:02d}"
                    today = datetime.now().date()
                    cellDate = datetime(year, month, day).date()

                    # Highlight colors (Selection)
                    if cellDate == today:
                        dayBg = "#90EE90"   # Today
                    elif col in (5, 6):
                        dayBg = "#ADD8E6"   # Weekend
                    else:
                        dayBg = "white"

                    # Day cell frame
                    frame = tk.Frame(self.calendarFrame, relief="ridge", bd=1, bg=dayBg)
                    frame.grid(row=row, column=col, sticky="nsew", padx=1, pady=1)

                    # Day number
                    tk.Label(frame, text=str(day), anchor="nw", bg=dayBg).pack(fill="x")

                    # Show events in that day
                    for idx, ev in enumerate(self.events.get(dateStr, [])):
                        # String Processing: format different text styles per category
                        if ev["category"] == "Assignment":
                            text = f"{ev['time']} {ev['title']} ({ev.get('description','')})"
                        elif ev["category"] == "Timetable":
                            text = f"{ev.get('startTime','?')}-{ev.get('endTime','?')} {ev['title']}"
                        elif ev["category"] == "Collab":
                            participants = ", ".join(ev.get("participants", []))
                            text = f"{ev['time']} {ev['title']} [{participants}]"

                        label = tk.Label(frame, text=text,
                                         bg=self.categoryColors[ev["category"]], fg="white",
                                         font=("Segoe UI", 9), anchor="w")
                        label.pack(fill="x", padx=2, pady=1)

                        # Click event → open edit form
                        label.bind("<Button-1>", lambda e, d=dateStr, i=idx, ev=ev:
                                   self.openEventForm(d, True, ev, i))

                    # Click empty cell → add new event
                    frame.bind("<Button-1>", lambda e, d=dateStr: self.openEventForm(d))

        # Expandable grid
        for i in range(7):
            self.calendarFrame.grid_columnconfigure(i, weight=1)
        for i in range(len(monthCalendar) + 2):
            self.calendarFrame.grid_rowconfigure(i, weight=1)
            


    # =================================================================================
    # === Event Add/Edit UI ======================================================
    # =================================================================================
    def openEventForm(self, dateStr=None, editMode=False, existing=None, eventIndex=None):
        """Form for adding/editing events"""
        # Prevent multiple popup windows
        if self.activeForm and tk.Toplevel.winfo_exists(self.activeForm):
            self.activeForm.lift()
            return

        # Popup window
        self.activeForm = tk.Toplevel(self.root)
        form = self.activeForm
        form.title("✏️ Edit Event" if editMode else "➕ Add Event")
        form.geometry("350x400")
        form.configure(bg="#f8f9fa")

        def onClose():
            self.activeForm = None
            form.destroy()
        form.protocol("WM_DELETE_WINDOW", onClose)

        # Require a valid date
        if not dateStr:
            messagebox.showerror("Error", "Please select a date on the calendar.")
            return

        # === Input fields ===
        tk.Label(form, text="Title:", bg="#f8f9fa").pack(pady=5)
        titleEntry = tk.Entry(form, width=25)
        titleEntry.pack()

        # Category selection
        tk.Label(form, text="Category:", bg="#f8f9fa").pack(pady=5)
        categoryVar = tk.StringVar(value="Assignment")
        tk.OptionMenu(form, categoryVar, *self.categoryColors.keys()).pack()

        # Extra fields (depends on category → Selection)
        extraFrame = tk.Frame(form, bg="#f8f9fa")
        extraFrame.pack(pady=5)
        fields = {}

        def updateFields(*args):
            """Dynamically update form fields based on category"""
            for widget in extraFrame.winfo_children():
                widget.destroy()
            fields.clear()

            if categoryVar.get() == "Assignment":
                tk.Label(extraFrame, text="Time (HH:MM):", bg="#f8f9fa").pack(pady=2)
                timeEntry = tk.Entry(extraFrame, width=25)
                timeEntry.pack()
                tk.Label(extraFrame, text="Description:", bg="#f8f9fa").pack(pady=2)
                descBox = tk.Text(extraFrame, width=25, height=4)
                descBox.pack()
                fields["time"] = timeEntry
                fields["desc"] = descBox

            elif categoryVar.get() == "Timetable":
                tk.Label(extraFrame, text="Start Time (HH:MM):", bg="#f8f9fa").pack(pady=2)
                startEntry = tk.Entry(extraFrame, width=25)
                startEntry.pack()
                tk.Label(extraFrame, text="End Time (HH:MM):", bg="#f8f9fa").pack(pady=2)
                endEntry = tk.Entry(extraFrame, width=25)
                endEntry.pack()
                fields["start"] = startEntry
                fields["end"] = endEntry

            elif categoryVar.get() == "Collab":
                tk.Label(extraFrame, text="Time (HH:MM):", bg="#f8f9fa").pack(pady=2)
                timeEntry = tk.Entry(extraFrame, width=25)
                timeEntry.pack()
                fields["time"] = timeEntry

                tk.Label(extraFrame, text="Participants (eg: gan, ash):", bg="#f8f9fa").pack(pady=2)
                participantsEntry = tk.Entry(extraFrame, width=25)
                participantsEntry.pack()
                fields["participants"] = participantsEntry

        categoryVar.trace("w", updateFields)
        updateFields()

        # === Prefill values if editing ===
        if editMode and existing:
            titleEntry.insert(0, existing["title"])
            categoryVar.set(existing["category"])
            updateFields()  # make sure fields exist for this category

            if existing["category"] == "Assignment":
                fields["time"].insert(0, existing["time"])
                fields["desc"].insert("1.0", existing.get("description", ""))
            elif existing["category"] == "Timetable":
                fields["start"].insert(0, existing.get("startTime", ""))
                fields["end"].insert(0, existing.get("endTime", ""))
            elif existing["category"] == "Collab":
                fields["time"].insert(0, existing.get("time", ""))
                participants = ", ".join(existing.get("participants", []))
                fields["participants"].insert(0, participants)

        # === Save button ===
        def saveEvent():
            """Validate inputs and save event (Selection + Exception Handling)"""
            title = titleEntry.get().strip()
            category = categoryVar.get()

            # Validation: no empty/invalid title
            if not title:
                messagebox.showerror("Error", "Title cannot be empty!")
                return
            if any(char.isdigit() or (not char.isalnum() and char != " ") for char in title):
                messagebox.showerror("Error", "Title cannot contain numbers or symbols!")
                return

            # Category-specific validation
            if category == "Assignment":
                timeStr = fields["time"].get().strip()
                desc = fields["desc"].get("1.0", "end").strip()
                if not desc:
                    messagebox.showerror("Error", "Description cannot be empty!")
                    return
                try:
                    datetime.strptime(timeStr, "%H:%M")
                except:
                    messagebox.showerror("Error", "Invalid time format! Use HH:MM.")
                    return
                newEvent = AssignmentEvent(title, timeStr, desc).toDict()

            elif category == "Timetable":
                startStr = fields["start"].get().strip()
                endStr = fields["end"].get().strip()
                try:
                    start = datetime.strptime(startStr, "%H:%M")
                    end = datetime.strptime(endStr, "%H:%M")
                    if end <= start:
                        messagebox.showerror("Error", "End time must be later than start time!")
                        return
                except:
                    messagebox.showerror("Error", "Invalid time format! Use HH:MM.")
                    return
                newEvent = TimetableEvent(title, startStr, endStr).toDict()

            elif category == "Collab":
                timeStr = fields["time"].get().strip()
                participantsStr = fields["participants"].get().strip()
                try:
                    datetime.strptime(timeStr, "%H:%M")
                except:
                    messagebox.showerror("Error", "Invalid time format! Use HH:MM.")
                    return

                participants = [p.strip() for p in participantsStr.split(",") if p.strip()]
                newEvent = CollabEvent(title, timeStr, participants).toDict()

            # Save into events list
            if editMode and eventIndex is not None:
                self.events[dateStr][eventIndex] = newEvent
            else:
                if dateStr not in self.events:
                    self.events[dateStr] = []
                self.events[dateStr].append(newEvent)

            # Save to file and refresh calendar
            self.saveEvents()
            self.drawCalendar()
            self.activeForm = None
            form.destroy()

        tk.Button(form, text="Save Event", command=saveEvent,
                  bg="#28a745", fg="white", width=12).pack(pady=15)


    # =================================================================================
    # === Delete Event Form ====================================================
    # =================================================================================
    def deleteEvent(self):
        """Delete events (GUI + File Processing + Collections)"""
        if self.activeForm and tk.Toplevel.winfo_exists(self.activeForm):
            self.activeForm.lift()
            return

        self.activeForm = tk.Toplevel(self.root)
        form = self.activeForm
        form.title("❌ Delete Event")
        form.geometry("750x400")
        form.configure(bg="#f8f9fa")

        def onClose():
            self.activeForm = None
            form.destroy()
        form.protocol("WM_DELETE_WINDOW", onClose)

        if not self.events:
            messagebox.showinfo("Info", "No events to delete.")
            return

        tk.Label(form, text="Select an event to delete (grouped by category):",
                 bg="#f8f9fa").pack(pady=5)

        eventList = []   # Store all events for lookup
        listboxes = {}   # Category → listbox
        frame = tk.Frame(form, bg="#f8f9fa")
        frame.pack(fill="both", expand=True)

        # Create Listbox for each category
        for idx, category in enumerate(self.categoryColors.keys()):
            catFrame = tk.LabelFrame(frame, text=category, bg="#f8f9fa",
                                    fg=self.categoryColors[category], padx=5, pady=5)
            catFrame.grid(row=0, column=idx, padx=5, pady=5, sticky="nsew")

            lb = tk.Listbox(catFrame, width=35, height=14, selectmode=tk.SINGLE,
                            bg="white", fg="black",
                            highlightbackground=self.categoryColors[category])
            lb.pack()
            listboxes[category] = lb

        # Fill listboxes with events
        for date, events in self.events.items():
            for idx, ev in enumerate(events):
                # Format event text (String Processing)
                if ev["category"] == "Assignment":
                    line = f"{date} | {ev['time']} | {ev['title']} ({ev.get('description','')})"
                elif ev["category"] == "Timetable":
                    line = f"{date} | {ev.get('startTime','?')} - {ev.get('endTime','?')} | {ev['title']}"
                elif ev["category"] == "Collab":
                    participants = ", ".join(ev.get("participants", []))
                    line = f"{date} | {ev['time']} | {ev['title']} [{participants}]"


                eventList.append((date, idx, ev))
                listboxes[ev["category"]].insert(tk.END, line)

        def deleteSelected():
            """Delete chosen event (Selection + Exception Handling)"""
            for category, lb in listboxes.items():
                selection = lb.curselection()
                if selection:
                    index = selection[0]
                    chosenDate, evIndex, ev = [
                        (d, i, e) for (d, i, e) in eventList if e["category"] == category
                    ][index]
                    try:
                        # Remove event from list
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


# ======================
# ===== Run App ========
# ======================
if __name__ == "__main__":
    root = tk.Tk()
    app = CalendarApp(root)
    root.mainloop()