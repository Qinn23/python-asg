import json
import os
import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.font import Font

class Homework:
    def __init__(self, subject, title, description, due_date, status):
        self._subject = subject
        self._title = title
        self._description = description
        self._due_date = due_date
        self._status = status

    # subject
    @property
    def subject(self):
        return self._subject

    @subject.setter
    def subject(self, value):
        self._subject = value

    # title
    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value

    # description
    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    # due_date
    @property
    def due_date(self):
        return self._due_date

    @due_date.setter
    def due_date(self, value):
        self._due_date = value

    # status
    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value

    def to_dict(self):
        return {
            'subject': self._subject,
            'title': self._title,
            'description': self._description,
            'due_date': self._due_date,
            'status': self._status
        }

    @classmethod
    def from_dict(cls, d):
        return cls(d['subject'], d['title'], d['description'], d['due_date'], d['status'])


class TimedHomework(Homework):
    def __init__(self, subject, title, description, due_date, status, time_required):
        super().__init__(subject, title, description, due_date, status)
        self._time_required = time_required

    # time_required
    @property
    def time_required(self):
        return self._time_required

    @time_required.setter
    def time_required(self, value):
        self._time_required = value

    def to_dict(self):
        d = super().to_dict()
        d['time_required'] = self._time_required
        d['timed'] = True
        return d

    @classmethod
    def from_dict(cls, d):
        return cls(
            d['subject'],
            d['title'],
            d['description'],
            d['due_date'],
            d['status'],
            d.get('time_required', 0)
        )

	
class HomeworkPlannerApp:
	HOMEWORK_FILE = "homework_data.json"

	def __init__(self, master=None):
		self.master = master
		self.homework_list = []
		self.checked_rows = set()
		self.selected_edit_row = {'idx': None}
		self.load_homework_data()

	def open_homework_planner_window(self):
		hw_win = tk.Toplevel(self.master) if self.master else tk.Toplevel()
		hw_win.title("Homework Planner")
		hw_win.geometry("800x450")
		tk.Label(hw_win, text="Homework Planner", font=("Segoe UI", 16, "bold")).pack(pady=10)

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

		# Add sorting by due date
		self._due_date_sort_asc = True
		def sort_by_due_date():
			# Sort the homework list by due date
			try:
				self.homework_list.sort(
					key=lambda hw: datetime.datetime.strptime(hw.due_date, "%Y-%m-%d"),
					reverse=not self._due_date_sort_asc
				)
			except Exception:
				# If any date is invalid, sort as string fallback
				self.homework_list.sort(
					key=lambda hw: hw.due_date,
					reverse=not self._due_date_sort_asc
				)
			self._due_date_sort_asc = not self._due_date_sort_asc
			self.refresh_homework(tree, search_var.get())
		tree.heading("Due Date", text="Due Date", command=sort_by_due_date)
		tree.heading("Status", text="Status")
		tree.column("Status", width=100, anchor='center')
		tree.heading("Time Required", text="Time Required (min)")
		tree.column("Time Required", width=130, anchor='center')
		tree.pack(fill='both', expand=True, padx=10, pady=10)

		tk.Label(hw_win, text="Tip: Double-click a row (not the checkbox) to view its description.", fg="red").pack(pady=(0, 5))

		def on_tree_click(event):
			region = tree.identify("region", event.x, event.y)
			col = tree.identify_column(event.x)
			row = tree.identify_row(event.y)
			if region == "cell":
				if col == "#1":
					if row:
						idx = int(row)
						if idx in self.checked_rows:
							self.checked_rows.remove(idx)
						else:
							self.checked_rows.add(idx)
						self.refresh_homework(tree, search_var.get())
				else:
					if row:
						idx = int(row)
						self.selected_edit_row['idx'] = idx
						for item in tree.get_children():
							tree.item(item, tags=())
						tree.item(row, tags=('selected',))
					else:
						# Clicked empty area: unselect any row
						self.selected_edit_row['idx'] = None
						for item in tree.get_children():
							tree.item(item, tags=())
		tree.bind("<Button-1>", on_tree_click)
		tree.tag_configure('selected', background='#cce5ff')

		def on_tree_double_click(event):
			region = tree.identify("region", event.x, event.y)
			col = tree.identify_column(event.x)
			row = tree.identify_row(event.y)
			if region == "cell" and col != "#1" and row:
				idx = int(row)
				hw = self.homework_list[idx]
				desc = hw.description if hw.description else "(No description)"
				messagebox.showinfo("Homework Description", desc)
		tree.bind("<Double-1>", on_tree_double_click)

		def on_search(*args):
			self.refresh_homework(tree, search_var.get())
		search_var.trace_add('write', on_search)

		self.refresh_homework(tree)

		btn_frame = tk.Frame(hw_win, bg="#f5f6fa")
		btn_frame.pack(pady=10)

		style = ttk.Style()
		style.theme_use('default')
		style.configure('Modern.TButton',
						font=("Segoe UI", 9, "bold"),
						foreground="#fff",
						background="#2ce3d7",
						borderwidth=2,
						focusthickness=3,
						focuscolor="#2ce3d7",
						padding=4,
						relief="flat",
						bordercolor="#2ce3d7"
		)
		style.map('Modern.TButton',
			background=[('active', '#0097a7'), ('!active', '#00bcd4')],
			bordercolor=[('active', '#007c91'), ('!active', '#0097a7')],
			relief=[('pressed', 'groove'), ('!pressed', 'flat')]
		)

		btn_add = ttk.Button(btn_frame, text="Add Homework", style='Modern.TButton', command=lambda: self.open_add_homework(tree))
		btn_edit = ttk.Button(btn_frame, text="Edit Homework", style='Modern.TButton', command=lambda: self.open_edit_homework(tree))
		btn_delete = ttk.Button(btn_frame, text="Delete Homework", style='Modern.TButton', command=lambda: self.delete_homework(tree))

		for btn in [btn_add, btn_edit, btn_delete]:
			btn.pack(side='left', padx=5)

	def refresh_homework(self, tree, filter_text=""):
		# Configure tags for row colors
		tree.tag_configure('completed', background='#b6fcb6')  # light green
		tree.tag_configure('pending', background='#ffe066')    # golden yellow
		for row in tree.get_children():
			tree.delete(row)
		filter_text = filter_text.lower()
		for idx, hw in enumerate(self.homework_list):
			if (
				filter_text in hw.subject.lower() or
				filter_text in hw.title.lower()
			):
				checked = '☑' if idx in self.checked_rows else '☐'
				time_required = ''
				if isinstance(hw, TimedHomework):
					time_required = str(hw.time_required)
				row_tag = 'completed' if hw.status.lower() == 'completed' else 'pending'
				tree.insert('', 'end', iid=idx, values=(checked, hw.subject, hw.title, hw.due_date, hw.status, time_required), tags=(row_tag,))

	def open_add_homework(self, tree):
		add_win = tk.Toplevel(self.master) if self.master else tk.Toplevel()
		add_win.title("Add Homework")
		add_win.geometry("350x400")

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

		is_timed_var = tk.BooleanVar()
		timed_frame = tk.Frame(add_win)
		timed_frame.pack(fill='x', padx=10, pady=(10,0))
		tk.Checkbutton(timed_frame, text="Timed Homework (add time required)", variable=is_timed_var).pack(anchor='w')
		time_required_label = tk.Label(add_win, text="Time Required (minutes):")
		time_required_entry = tk.Spinbox(add_win, from_=1, to=1440, width=10)

		def toggle_timed():
			if is_timed_var.get():
				time_required_label.pack(anchor='w', padx=10, pady=(10,0))
				time_required_entry.pack(fill='x', padx=10)
			else:
				time_required_label.pack_forget()
				time_required_entry.pack_forget()
		is_timed_var.trace_add('write', lambda *args: toggle_timed())

		tk.Button(add_win, text="Add Homework", command=lambda: self.add_homework(
			subject_entry.get(), title_entry.get(), desc_entry.get(), due_entry.get(), status_var.get(), tree, add_win, is_timed_var.get(), time_required_entry.get() if is_timed_var.get() else None)).pack(pady=15)

	def add_homework(self, subject, title, description, due_date, status, tree, add_win, is_timed, time_required):
		# Validate due date format
		try:
			datetime.datetime.strptime(due_date, "%Y-%m-%d")
		except ValueError:
			messagebox.showwarning("Input Error", "Due Date must be in YYYY-MM-DD format and a valid date.")
			return
		if is_timed:
			try:
				time_required = int(time_required)
			except ValueError:
				messagebox.showwarning("Input Error", "Time Required must be an integer (minutes).")
				return
			hw = TimedHomework(subject, title, description, due_date, status, time_required)
		else:
			hw = Homework(subject, title, description, due_date, status)
		self.homework_list.append(hw)
		self.save_homework_data()
		self.refresh_homework(tree)
		add_win.destroy()

	def open_edit_homework(self, tree):
		idx = self.selected_edit_row.get('idx')
		if idx is None or not isinstance(idx, int) or idx < 0 or idx >= len(self.homework_list):
			messagebox.showwarning("No selection", "Please click a row (not the checkbox) to select a homework entry to edit.")
			return
		hw = self.homework_list[idx]

		edit_win = tk.Toplevel(self.master) if self.master else tk.Toplevel()
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
		if is_timed_var.get():
			time_required_label.pack(anchor='w', padx=10, pady=(10,0))
			time_required_entry.pack(fill='x', padx=10)

		edit_win.is_timed_var = is_timed_var
		edit_win.time_required_entry = time_required_entry

		tk.Button(edit_win, text="Save Changes", command=lambda: self.edit_homework(
			idx, subject_entry.get(), title_entry.get(), desc_entry.get(), due_entry.get(), status_var.get(), tree, edit_win, is_timed_var.get(), time_required_entry.get() if is_timed_var.get() else None)).pack(pady=15)

	def edit_homework(self, idx, subject, title, description, due_date, status, tree, edit_win, is_timed, time_required):
		# Validate due date format
		try:
			datetime.datetime.strptime(due_date, "%Y-%m-%d")
		except ValueError:
			messagebox.showwarning("Input Error", "Due Date must be in YYYY-MM-DD format and a valid date.")
			return
		if is_timed:
			try:
				time_required = int(time_required)
			except ValueError:
				messagebox.showwarning("Input Error", "Time Required must be an integer (minutes).")
				return
			self.homework_list[idx] = TimedHomework(subject, title, description, due_date, status, time_required)
		else:
			self.homework_list[idx] = Homework(subject, title, description, due_date, status)
		self.save_homework_data()
		self.selected_edit_row['idx'] = None
		self.refresh_homework(tree)
		edit_win.destroy()

	def delete_homework(self, tree):
		if not self.checked_rows:
			messagebox.showwarning("No selection", "Please tick the checkbox to select one or more homework entries to delete.")
			return
		if len(self.checked_rows) == 1:
			msg = "Are you sure you want to delete this homework entry?"
		else:
			msg = f"Are you sure you want to delete these {len(self.checked_rows)} homework entries?"
		confirm = messagebox.askyesno("Confirm Delete", msg)
		if confirm:
			for idx in sorted(self.checked_rows, reverse=True):
				del self.homework_list[idx]
			self.checked_rows.clear()
			self.selected_edit_row['idx'] = None
			self.save_homework_data()
			self.refresh_homework(tree)

	def save_homework_data(self):
		try:
			with open(self.HOMEWORK_FILE, 'w') as f:
				json.dump([hw.to_dict() for hw in self.homework_list], f, indent=2)
			return True
		except Exception as e:
			print(f"Error saving homework data: {e}")
			messagebox.showerror("Save Error", f"Failed to save homework data: {e}")
			return False

	def load_homework_data(self):
		try:
			if os.path.exists(self.HOMEWORK_FILE):
				with open(self.HOMEWORK_FILE, 'r') as f:
					data = json.load(f)
					self.homework_list = [TimedHomework.from_dict(d) if d.get('timed') else Homework.from_dict(d) for d in data]
			else:
				self.homework_list = []
		except Exception as e:
			print(f"Error loading homework data: {e}")
			self.homework_list = []


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    app = HomeworkPlannerApp(root)
    app.open_homework_planner_window()
    root.mainloop()