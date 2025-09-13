import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import json
import shutil
import os
import winsound
import random
from threading import Thread
import pygame
import webbrowser
from PIL import Image, ImageTk

class Timer:
    # Timer base class for countdown logic
    def __init__(self, duration=0):
        self.duration = duration  # in seconds
        self._remaining_time = duration
        self.is_running = False

    def start(self):
        self.is_running = True

    def pause(self):
        self.is_running = False

    def reset(self):
        self._remaining_time = self.duration

class ToolTip:
    # Tooltip helper for Tkinter widgets
    def __init__(self, widget, text, delay=500):
        self.widget = widget
        self.text = text
        self.delay = delay  # milliseconds before showing
        self.tip_window = None
        self.id = None
        self.widget.bind("<Enter>", self.schedule)
        self.widget.bind("<Leave>", self.hide_tip)

    def schedule(self, event=None):
        # Schedule the tooltip to appear after a delay
        self.unschedule()
        self.id = self.widget.after(self.delay, self.show_tip)

    def unschedule(self):
        # Cancel scheduled tooltip if mouse leaves early
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None

    def show_tip(self):
        # Display the tooltip
        if self.tip_window or not self.text:
            return
    
        # Position tooltip relative to the widget
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() - 20 

        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)  # Remove window decorations
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify='left',
                        background="#ffffe0", relief='solid', borderwidth=1,
                        font=("Arial", 9))
        label.pack(ipadx=5, ipady=3)

        self.widget.after(5000, self.hide_tip)

    def hide_tip(self, event=None):
        # Hide the tooltip
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None
    
class PomodoroTimer(Timer):
    # Main Pomodoro Timer class with UI and gamification
    def __init__(self, root):
        # Initialize the Pomodoro timer window and variables
        super().__init__(duration=25*60)
        self.root = root
        self.root.title("Purr-odoro Timer")
        self.root.configure(bg='#f5f5f5')
        self.center_window(800, 600)

        # Load settings or create default
        self.load_settings()

        # Initialize variables
        self.is_running = False
        self._is_focus = True
        self._remaining_time = self.settings['focus_time'] * 60
        self._pomodoro_count = 0
        self._coins = 10  # Starting coins
        self._current_task = ""
        self._tasks = [] 
        self._cat_state = "normal"  # normal, sleeping, happy
        self._focus_sessions_in_cycle = 0

        self._timer_after_id = None
        self._current_duration = self.settings['focus_time'] * 60
        self._remaining_time = self._current_duration

        # Setup UI
        self.setup_ui()

    # Properties for protected variables
    @property
    def is_focus(self):
        return self._is_focus

    @is_focus.setter
    def is_focus(self, value):
        self._is_focus = value

    @property
    def pomodoro_count(self):
        return self._pomodoro_count

    @pomodoro_count.setter
    def pomodoro_count(self, value):
        self._pomodoro_count = value

    @property
    def coins(self):
        return self._coins

    @coins.setter
    def coins(self, value):
        self._coins = value

    @property
    def current_task(self):
        return self._current_task

    @current_task.setter
    def current_task(self, value):
        self._current_task = value

    @property
    def tasks(self):
        return self._tasks

    @tasks.setter
    def tasks(self, value):
        self._tasks = value

    @property
    def cat_state(self):
        return self._cat_state

    @cat_state.setter
    def cat_state(self, value):
        self._cat_state = value

    @property
    def focus_sessions_in_cycle(self):
        return self._focus_sessions_in_cycle

    @focus_sessions_in_cycle.setter
    def focus_sessions_in_cycle(self, value):
        self._focus_sessions_in_cycle = value

    @property
    def timer_after_id(self):
        return self._timer_after_id

    @timer_after_id.setter
    def timer_after_id(self, value):
        self._timer_after_id = value

    @property
    def current_duration(self):
        return self._current_duration

    @current_duration.setter
    def current_duration(self, value):
        self._current_duration = value

    def load_settings(self):
        # Load settings from JSON or create defaults
        try:
            if os.path.exists('pomodoro_settings.json'):
                with open('pomodoro_settings.json', 'r') as f:
                    self.settings = json.load(f)
            else:
                self.create_default_settings()
        except:
            self.create_default_settings()
        
        # Load default sounds first time if not set
        default_folder = "pomodoro_defaultsound"
        self.settings['focus_sound'] = self.settings.get('focus_sound') or os.path.join(default_folder, "focus.mp3")
        self.settings['break_sound'] = self.settings.get('break_sound') or os.path.join(default_folder, "break.mp3")
        self.settings['task_complete_sound'] = self.settings.get('task_complete_sound') or os.path.join(default_folder, "complete.mp3")

    def create_default_settings(self):
        # Set default settings for the timer
        self.settings = {
            'focus_time': 25,
            'break_time': 5,
            'long_break_time': 10,
            'coins': 0,
            'cat_items': [],
            'focus_sound': None,
            'break_sound': None,
            'task_complete_sound': None
        }

    def save_settings(self):
        # Save current settings to JSON file
        with open('pomodoro_settings.json', 'w') as f:
            json.dump(self.settings, f)

    def setup_ui(self):
        # Build the main UI layout and widgets
        # Create main frames
        self.top_frame = tk.Frame(self.root, bg='#f5f5f5')
        self.top_frame.pack(pady=20)

        self.middle_frame = tk.Frame(self.root, bg='#f5f5f5')
        self.middle_frame.pack(pady=20)

        self.bottom_frame = tk.Frame(self.root, bg='#f5f5f5')
        self.bottom_frame.pack(pady=20)

        # Clock display
        mins, secs = divmod(self._remaining_time, 60)
        self.clock_label = tk.Label(
        self.top_frame,
        text=f"{mins:02d}:{secs:02d}",
        font=('Arial', 48),
        bg='#f5f5f5'
        )
        self.clock_label.pack()

        # Mode label
        self.mode_label = tk.Label(self.top_frame, text="Focus Time", font=('Arial', 18), bg='#f5f5f5', fg='#d63031')
        self.mode_label.pack()
        self.cycle_label = tk.Label(self.top_frame, text="Focus Session 1/4", font=('Arial', 12), bg='#f5f5f5', fg='#666')
        self.cycle_label.pack()

        # Task list section (replace previous task_canvas code)
        task_frame = tk.Frame(self.middle_frame, bg='#f5f5f5')
        task_frame.pack(side=tk.RIGHT, padx=20)

        tk.Label(task_frame, text="Tasks:", font=('Arial', 12, 'bold'), bg='#f5f5f5').pack()

        # NOTE: exportselection=False keeps selection even after focus changes (so Delete button works)
        self.task_listbox = tk.Listbox(task_frame, width=25, height=8, font=('Arial', 12),
                               exportselection=False, selectmode=tk.SINGLE)
        self.task_listbox.pack(pady=5)

        # Buttons for tasks
        task_btn_frame = tk.Frame(task_frame, bg='#f5f5f5')
        task_btn_frame.pack()

        ttk.Button(task_btn_frame, text="Add Task", command=self.add_task).grid(row=0, column=0, padx=5)
        ttk.Button(task_btn_frame, text="Delete Task", command=self.delete_task).grid(row=0, column=1, padx=5)
        ttk.Button(task_btn_frame, text="Clear Tasks", command=self.clear_tasks).grid(row=0, column=2, padx=5)
        ToolTip(self.task_listbox, "💡 Select a task from the list before pressing Delete")

        # Mark Complete button (only visible during long breaks)
        self.mark_complete_button = ttk.Button(task_btn_frame, text="Mark Complete", command=self.mark_task_complete)
        self.mark_complete_button.grid(row=1, column=0, columnspan=3, pady=5)
        self.mark_complete_button.grid_remove() 
        
        # Display cat image
        self.cat_canvas = tk.Canvas(self.middle_frame, width=200, height=200, bg='#f5f5f5', highlightthickness=0)
        self.cat_canvas.pack(side=tk.LEFT, padx=20)

        # Load cat images
        self.cat_normal = ImageTk.PhotoImage(Image.open("Pomodoro_cat/EyesOpen.png").resize((200, 200)))
        self.cat_sleeping = ImageTk.PhotoImage(Image.open("Pomodoro_cat/Sleep.png").resize((200, 200)))
        self.cat_happy = ImageTk.PhotoImage(Image.open("Pomodoro_cat/EyesOpenHeart.png").resize((200, 200)))

        # initial cat image
        self.cat_image_id = self.cat_canvas.create_image(100, 100, image=self.cat_normal)

        # Timer controls
        self.start_button = ttk.Button(self.bottom_frame, text="Start", command=self.start_timer)
        self.start_button.grid(row=0, column=0, padx=10)

        self.pause_button = ttk.Button(self.bottom_frame, text="Pause", command=self.pause_timer, state=tk.DISABLED)
        self.pause_button.grid(row=0, column=1, padx=10)

        self.skip_button = ttk.Button(self.bottom_frame, text="Skip", command=self.skip_timer)
        self.skip_button.grid(row=0, column=2, padx=10)

        self.reset_button = ttk.Button(self.bottom_frame, text="Reset timer", command=self.reset_timer)
        self.reset_button.grid(row=0, column=3, padx=10)

       # Coin, Cat Shop, and Sound Settings area
        coin_frame = tk.Frame(self.root, bg='#f5f5f5')
        coin_frame.pack(pady=10, fill=tk.X)

        # Coins label
        self.coin_label = tk.Label(coin_frame, text=f"Coins: {self.coins}", font=('Arial', 14), bg='#f5f5f5')
        self.coin_label.grid(row=0, column=0, padx=10, sticky='w')

        # Cat Shop button
        shop_button = ttk.Button(coin_frame, text="Cat Shop", command=self.open_cat_shop)
        shop_button.grid(row=0, column=1, padx=5, sticky='w')

        # Sound Settings button
        sound_button = ttk.Button(coin_frame, text="Sound Settings", command=self.open_sound_settings)
        sound_button.grid(row=0, column=2, padx=5, sticky='w')

        # Timer Settings button
        timer_button = ttk.Button(coin_frame, text="Timer Settings", command=self.open_timer_settings)
        timer_button.grid(row=0, column=3, padx=5, sticky='w')

        # Make columns expand nicely if window resized
        coin_frame.grid_columnconfigure(0, weight=1)
        coin_frame.grid_columnconfigure(1, weight=0)
        coin_frame.grid_columnconfigure(2, weight=0)
        coin_frame.grid_columnconfigure(3, weight=1)
        

    def update_cycle_display(self):
        # Update the label showing the current Pomodoro/break cycle
        if self.is_focus:
            current_focus = (self.focus_sessions_in_cycle % 4) + 1
            self.cycle_label.config(text=f"Focus Session {current_focus}/4")
        else:
            if self.focus_sessions_in_cycle % 4 == 0:
                self.cycle_label.config(text="Long Break Time")
            else:
                self.cycle_label.config(text="Short Break Time")

    def set_cat_state(self, state):
        # Change the cat image based on state (normal, sleeping, happy)
        if state == "normal":
            self.cat_canvas.itemconfig(self.cat_image_id, image=self.cat_normal)
        elif state == "sleeping":
            self.cat_canvas.itemconfig(self.cat_image_id, image=self.cat_sleeping)
        elif state == "happy":
            self.cat_canvas.itemconfig(self.cat_image_id, image=self.cat_happy)
        self.cat_state = state

    def add_task(self):
        # Open a dialog to add a new task to the list
        task_window = tk.Toplevel(self.root)
        task_window.title("Add Task")
        task_window.geometry("400x150")  

        tk.Label(task_window, text="Enter a new task:", font=('Arial', 12)).pack(pady=10)
        task_entry = ttk.Entry(task_window, width=40, font=('Arial', 12))
        task_entry.pack(pady=5)
        task_entry.focus_set()

        def save_task():
            # Save the new task and close the dialog
            task = task_entry.get().strip()
            if task:
                self.tasks.append(task)
                self.task_listbox.insert(tk.END, task)
                last = self.task_listbox.size() - 1
                self.task_listbox.selection_clear(0, tk.END)
                self.task_listbox.selection_set(last)
                self.task_listbox.see(last)
                self.current_task = task
                task_window.destroy()

        ttk.Button(task_window, text="Add Task", command=save_task).pack(pady=10)

        task_window.transient(self.root)  
        task_window.grab_set()            
        self.root.wait_window(task_window)

    def delete_task(self):
        # Delete the selected task from the list
        if not self.tasks:  # Check if task list is empty
            messagebox.showwarning("No Tasks", "There are no tasks to delete!")
            return

        selection = self.task_listbox.curselection()
        
        if not selection:
            messagebox.showwarning("No Task Selected", "Please select a task to delete!")
            return
        
        selection = self.task_listbox.curselection()
        if not selection:
            return
        
        # If multiple are selected (if you ever change selectmode), delete in reverse order
        indices = list(selection)
        for index in reversed(indices):
            # remove from backing list and Listbox
            try:
                del self.tasks[index]
            except IndexError:
                pass
        self.task_listbox.delete(index)

        # If current_task was deleted, clear it
        if self.current_task and self.current_task not in self.tasks:
            self.current_task = ""

    def clear_tasks(self):
        # Remove all tasks from the list after confirmation
        if not self.tasks:  # Check if task list is empty
            messagebox.showwarning("No Tasks", "There are no tasks to clear!")
            return

        if messagebox.askyesno("Clear All Tasks", "Remove ALL tasks?"):
            self.tasks.clear()
            self.task_listbox.delete(0, tk.END)
            self.current_task = ""


    def start_timer(self):
        # Start the Pomodoro timer, checking for valid task selection
        if self.timer_after_id:
            self.root.after_cancel(self.timer_after_id)
            self.timer_after_id = None

        if not self.is_running:
            super().start()  # sets self.is_running = True
            self.start_button.config(state=tk.DISABLED)
            self.pause_button.config(state=tk.NORMAL)

        if self.is_focus:
            # For focus sessions, ensure a task is selected
            selected_indices = self.task_listbox.curselection()
            if not selected_indices:
                messagebox.showwarning("No Task", "Please select or add a task first!")
                return

            selected_task = self.task_listbox.get(selected_indices[0]).strip()

            # Prevent starting on completed task
            if selected_task.startswith("✔"):
                messagebox.showwarning("Task Completed", "Please select or add a new task before starting.")
                return

            # Set current task
            self.current_task = selected_task

            # Play focus sound & set cat state
            if self.settings['focus_sound']:
                Thread(target=self.play_sound, args=(self.settings['focus_sound'],)).start()
            self.set_cat_state("sleeping")

        else:
            # Break mode — no task required
            if self.settings['break_sound']:
                Thread(target=self.play_sound, args=(self.settings['break_sound'],)).start()
                self.set_cat_state("normal")

        # Start ticking
        self.update_timer()

    def pause_timer(self):
        # Pause the timer and update button states
        if self.is_running:
            super().pause()
            self.start_button.config(state=tk.NORMAL)
            self.pause_button.config(state=tk.DISABLED)
            winsound.PlaySound(None, winsound.SND_PURGE)

    def skip_timer(self):
        # Skip the current timer phase, optionally marking task complete
        selected_indices = self.task_listbox.curselection()
        if self.is_focus and not selected_indices:
            messagebox.showwarning("No Task", "Please select or add a task first!")
            return

        selected_task = self.task_listbox.get(selected_indices[0]).strip()
        if selected_task.startswith("✔"):
            messagebox.showwarning("Task Completed", "Please select or add a new task before skipping.")
            return

        self.current_task = selected_task
        self.is_running = False

        # Cancel pending timer update if exists
        if self.timer_after_id:
            self.root.after_cancel(self.timer_after_id)
            self.timer_after_id = None

        # If skipping a focus session, still mark task as complete and award coins
        if self.is_focus:
            self.complete_focus_session()
    
        self.next_phase()

        # Allow user to start again
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)

    def reset_timer(self):
        # Reset the timer to the start of the current phase
        # Cancel any running timer loop
        if self.timer_after_id:
            self.root.after_cancel(self.timer_after_id)
            self.timer_after_id = None

        # Fully stop the timer
        self.is_running = False
        super().reset()

        # Set remaining_time based on current mode
        if self.is_focus:
            self._remaining_time = self.settings['focus_time'] * 60
            self.mode_label.config(text="Focus Time", fg='#d63031')
        else:
            self._remaining_time = self.settings['break_time'] * 60
            self.mode_label.config(text="Break Time", fg='#00b894')

        self.update_display()
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)

    def update_timer(self):
        # Update the timer countdown every second
        if self._remaining_time > 0 and self.is_running:
            self._remaining_time -= 1 
            mins, secs = divmod(self._remaining_time, 60)
            self.clock_label.config(text=f"{mins:02d}:{secs:02d}")
            self.timer_after_id = self.root.after(1000, self.update_timer)
        elif self._remaining_time <= 0:
            self.timer_complete()

    def mark_task_complete(self):
        # Mark the selected task as complete and award coins
        selected_indices = self.task_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("No Task Selected", "Please select a task to mark as complete!")
            return
    
        index = selected_indices[0]
        task_text = self.task_listbox.get(index).lstrip("✔ ").strip()
    
        # Don't mark already completed tasks
        if task_text.startswith("✔"):
            messagebox.showinfo("Already Complete", "This task is already marked as complete!")
            return
    
        # Mark task as complete
        self.task_listbox.delete(index)
        self.task_listbox.insert(index, f"✔ {task_text}")
        self.task_listbox.itemconfig(index, fg="gray")
    
        # Update backing list
        self.tasks[index] = f"✔ {task_text}"
    
        # Award coins for completing task
        coins_earned = random.randint(1, 3)
        self.coins += coins_earned
        self.settings['coins'] = self.coins
        self.save_settings()
        self.coin_label.config(text=f"Coins: {self.coins}")
    
        # Show happy cat briefly
        def show_happy_cat():
            self.set_cat_state("happy")
            self.root.after(2000, show_happy_cat)
    
        messagebox.showinfo("Task Complete!", f"Task marked as complete! You earned {coins_earned} coins!")

    def timer_complete(self):
        # Handle logic when the timer reaches zero
        self.is_running = False

        if self.is_focus:
            # Focus session completed
            self.pomodoro_count += 1
            messagebox.showinfo("Focus Completed", f"Great job! You've completed {self.pomodoro_count} focus sessions!")
    
        # Move to next phase
        self.next_phase()
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)

    def complete_focus_session(self):
        # Complete a focus session, award coins, and select next task
        # Increment total Pomodoro count only
        self.pomodoro_count += 1

        # Award coins
        coins_earned = random.randint(1, 3)
        self.coins += coins_earned
        self.settings['coins'] = self.coins
        self.save_settings()
        self.coin_label.config(text=f"Coins: {self.coins}")

        # Auto-select the next unfinished task
        next_task = None
        for i in range(self.task_listbox.size()):
            task_text = self.task_listbox.get(i)
            if not task_text.startswith("✔"):
                next_task = task_text
                self.task_listbox.selection_clear(0, tk.END)
                self.task_listbox.selection_set(i)
                self.task_listbox.see(i)
                break

        if next_task:
            self.current_task = next_task
        else:
            self.current_task = ""
            messagebox.showinfo("No Tasks Left", "All tasks are complete! Please add a new one.")

    def next_phase(self):
        # Switch between focus, short break, and long break phases
        if self.is_focus:
            # End of focus session → increment cycle counter
            self.focus_sessions_in_cycle += 1

            # Every 4th focus → long break
            if self.focus_sessions_in_cycle % 4 == 0:
                self.is_focus = False
                self.current_duration = self.settings['long_break_time'] * 60
                self.mode_label.config(text="Long Break Time", fg='#0984e3')
                self.mark_complete_button.grid()  # show "Mark Complete" button

                if self.settings.get('task_complete_sound'):
                    Thread(target=self.play_sound, args=(self.settings['task_complete_sound'],)).start()
                    
                messagebox.showinfo("Long Break!",
                f"Time for a {self.settings['long_break_time']}-minute long break!\n\n"
                "One Pomodoro cycle completed!\n"
                "Use the 'Mark Complete' button to mark any tasks you've finished.")
            else:
                # Otherwise → short break
                self.is_focus = False
                self.current_duration = self.settings['break_time'] * 60
                self.mode_label.config(text="Break Time", fg='#00b894')
                self.mark_complete_button.grid_remove()

            self.set_cat_state("normal")

        else:
            # Break finished → go back to focus
            self.is_focus = True
            self.current_duration = self.settings['focus_time'] * 60
            self.mode_label.config(text="Focus Time", fg='#d63031')
            self.mark_complete_button.grid_remove()
            self.set_cat_state("sleeping")

        # Reset timer for the new phase
        self._remaining_time = self.current_duration
        self.update_display()
        self.update_cycle_display()

    def update_display(self):
        # Update the timer display label
        mins, secs = divmod(self._remaining_time, 60)
        self.clock_label.config(text=f"{mins:02d}:{secs:02d}")

    def save_timer_settings(self):
        # Save timer settings from the settings dialog
        try:
            # Read values from entry boxes
            focus = int(self.focus_entry.get())
            brk = int(self.break_entry.get())
            long_brk = int(self.long_break_entry.get())

            # Update settings (store minutes, not seconds)
            self.settings['focus_time'] = focus
            self.settings['break_time'] = brk
            self.settings['long_break_time'] = long_brk

            # Update current timer duration (in seconds)
            if self.is_focus:
                self.duration = focus * 60
            else:
                self.duration = brk * 60

            self._remaining_time = self.duration  # reset countdown
            self.update_display()
            self.save_settings()  # write to JSON 
        
            messagebox.showinfo("Success", "Timer settings saved successfully!")

        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter numbers only.")

    def set_sound(self, sound_type):
        # Set a custom sound for focus, break, or completion
        file_path = filedialog.askopenfilename(title=f"Select {sound_type.replace('_', ' ')}",
                                               filetypes=(("Mp3 files", "*.mp3"), ("All files", "*.*")))
        if file_path:
            try:
                # Ensure 'Pomodoro_sounds' folder exists in your app directory
                os.makedirs("Pomodoro_sounds", exist_ok=True)

                # Copy the selected file into the 'Pomodoro_sounds' folder
                filename = os.path.basename(file_path)
                destination = os.path.join("Pomodoro_sounds", filename)

                shutil.copy(file_path, destination)

                # Save the relative path in settings
                self.settings[sound_type] = destination
                self.save_settings()
                messagebox.showinfo("Sound Saved", f"{sound_type.replace('_', ' ').title()} saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save sound: {e}")

    def play_sound(self, sound_file):
        # Play a sound file using pygame
        try:
            if sound_file:  
                pygame.mixer.init()
                pygame.mixer.music.load(sound_file)
                pygame.mixer.music.play()
        except Exception as e:
            print(f"Error playing sound: {e}")

    def open_music_app(self):
        # Open YouTube Music in the browser
        choice = messagebox.askyesno("Music Apps",
                                     "Would you like to open Youtube music?\nRequires internet connection.")
        if choice:
            webbrowser.open("https://music.youtube.com/")

    def open_cat_shop(self):
        # Open the cat shop window to buy items with coins
        shop_window = tk.Toplevel(self.root)
        shop_window.title("Cat Shop")
        shop_window.geometry("400x400")

        items = [
            {"name": "Fish", "price": 5, "icon": "🐟"},
            {"name": "Ball", "price": 8, "icon": "⚾"},
            {"name": "Scratching Post", "price": 15, "icon": "🌲"},
            {"name": "Luxury Bed", "price": 25, "icon": "🛏️"}
        ]

        tk.Label(shop_window, text=f"Your coins: {self.coins}", font=('Arial', 14)).pack(pady=10)
        tk.Label(shop_window, text="Select an item to buy for your cat:", font=('Arial', 12)).pack()

        item_frame = tk.Frame(shop_window)
        item_frame.pack(pady=10)

        def make_buy_command(item):
            def buy():
                self.buy_item(item)
            return buy

        for item in items:
            item_row = tk.Frame(item_frame)
            item_row.pack(fill=tk.X, pady=5)
            tk.Label(item_row, text=f"{item['icon']} {item['name']}: {item['price']} coins",
                     width=25, anchor=tk.W).pack(side=tk.LEFT)

            state = tk.NORMAL if self.coins >= item['price'] else tk.DISABLED
            ttk.Button(item_row, text="Buy", command=make_buy_command(item), state=state).pack(side=tk.RIGHT)

        ttk.Button(shop_window, text="Close", command=shop_window.destroy).pack(pady=10)

    def buy_item(self, item):
        # Buy an item for the cat if enough coins
        if self.coins >= item['price']:
            self.coins -= item['price']
            self.settings['coins'] = self.coins
            self.settings['cat_items'].append(item['name'])
            self.save_settings()

            self.coin_label.config(text=f"Coins: {self.coins}")
            messagebox.showinfo("Purchase Complete",
                                f"You bought {item['name']} for your cat! Remaining coins: {self.coins}")

            # Show happy cat for 3s then go back
            self.set_cat_state("happy")
            def reset_cat_state():
                self.set_cat_state("normal" if not self.is_focus else "sleeping")
            self.root.after(3000, reset_cat_state)
        else:
            messagebox.showerror("Not Enough Coins", "You don't have enough coins to buy this item!")

    def open_sound_settings(self):
        # Open the sound settings dialog
        sound_window = tk.Toplevel(self.root)
        sound_window.title("Sound Settings")
        sound_window.geometry("400x200")
        sound_window.configure(bg='#f5f5f5')

        tk.Label(sound_window, text="Sound Settings", font=('Arial', 16, 'bold'), bg='#f5f5f5').pack(pady=10)

        # Define button commands as inner functions to access self
        def set_focus_sound():
            self.set_sound('focus_sound')
        def set_break_sound():
            self.set_sound('break_sound')
        def set_completion_sound():
            self.set_sound('task_complete_sound')

        # Focus sound
        ttk.Button(sound_window, text="Set Focus Sound",
                   command=set_focus_sound).pack(pady=5)

        # Break sound
        ttk.Button(sound_window, text="Set Break Sound",
                   command=set_break_sound).pack(pady=5)

        # Completion/long break sound
        ttk.Button(sound_window, text="Set Completion Sound ",
                   command=set_completion_sound).pack(pady=5)

        # Connect to Music App
        ttk.Button(sound_window, text="Connect to Music App", command=self.open_music_app).pack(pady=10)

    def open_timer_settings(self):
    # Timer settings window
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Timer Settings")
        settings_window.geometry("400x250")
        settings_window.configure(bg='#f5f5f5')

        tk.Label(settings_window, text="Timer Settings", font=('Arial', 16, 'bold'), bg='#f5f5f5').pack(pady=10)

        form_frame = tk.Frame(settings_window, bg='#f5f5f5')
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Focus Time (minutes):", bg='#f5f5f5').grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.focus_entry = ttk.Entry(form_frame)  
        self.focus_entry.insert(0, str(self.settings['focus_time']))
        self.focus_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Break Time (minutes):", bg='#f5f5f5').grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.break_entry = ttk.Entry(form_frame)  
        self.break_entry.insert(0, str(self.settings['break_time']))
        self.break_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Long Break Time (minutes):", bg='#f5f5f5').grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.long_break_entry = ttk.Entry(form_frame)  
        self.long_break_entry.insert(0, str(self.settings['long_break_time']))
        self.long_break_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Button(settings_window, text="Save Settings", command=self.save_timer_settings).pack(pady=10)

    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")


if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroTimer(root)
    root.mainloop()