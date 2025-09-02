import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import time
import winsound
import random
from threading import Thread
import json
import os
import webbrowser
from PIL import Image, ImageTk

class Timer:
    def __init__(self, duration=0):
        self.duration = duration  # in seconds
        self.remaining_time = duration
        self.is_running = False

    def start(self):
        self.is_running = True

    def pause(self):
        self.is_running = False

    def reset(self):
        self.remaining_time = self.duration

    def tick(self):
        if self.is_running and self.remaining_time > 0:
            self.remaining_time -= 1
        return self.remaining_time
    
class PomodoroTimer(Timer):
    def __init__(self, root):
        self.root = root
        self.root.title("Purr-odoro Timer")
        self.root.geometry("800x600")
        self.root.configure(bg='#f5f5f5')

        # Load settings or create default
        self.load_settings()

        # Initialize variables
        self.is_running = False
        self.is_focus = True
        self.remaining_time = self.settings['focus_time'] * 60
        self.pomodoro_count = 0
        self.coins = 10  # Starting coins
        self.current_task = ""
        self.cat_state = "normal"  # normal, sleeping, happy

        # Setup UI
        self.setup_ui()

    def load_settings(self):
        try:
            if os.path.exists('pomodoro_settings.json'):
                with open('pomodoro_settings.json', 'r') as f:
                    self.settings = json.load(f)
            else:
                self.create_default_settings()
        except:
            self.create_default_settings()

    def create_default_settings(self):
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
        with open('pomodoro_settings.json', 'w') as f:
            json.dump(self.settings, f)

    def setup_ui(self):
        # Create main frames
        self.top_frame = tk.Frame(self.root, bg='#f5f5f5')
        self.top_frame.pack(pady=20)

        self.middle_frame = tk.Frame(self.root, bg='#f5f5f5')
        self.middle_frame.pack(pady=20)

        self.bottom_frame = tk.Frame(self.root, bg='#f5f5f5')
        self.bottom_frame.pack(pady=20)

        # Clock display
        self.clock_label = tk.Label(self.top_frame, text="25:00", font=('Arial', 48), bg='#f5f5f5')
        self.clock_label.pack()

        # Mode label
        self.mode_label = tk.Label(self.top_frame, text="Focus Time", font=('Arial', 18), bg='#f5f5f5', fg='#d63031')
        self.mode_label.pack()

        # Task note paper
        self.task_canvas = tk.Canvas(self.middle_frame, width=200, height=150, bg='#fffbdf', highlightthickness=0)
        self.task_canvas.pack(side=tk.RIGHT, padx=20)

        self.task_canvas.create_rectangle(0, 0, 200, 150, fill='#fffbdf', outline='#d4b483')
        self.task_canvas.create_text(100, 30, text="Current Task:", font=('Arial', 12, 'bold'))
        self.task_text = self.task_canvas.create_text(100, 70, text="No task set", font=('Arial', 12), width=180)

        # Cat display (image instead of drawing)
        self.cat_canvas = tk.Canvas(self.middle_frame, width=200, height=200, bg='#f5f5f5', highlightthickness=0)
        self.cat_canvas.pack(side=tk.LEFT, padx=20)

        # Load cat images
        self.cat_normal = ImageTk.PhotoImage(Image.open("Pomodoro_cat/EyesOpen.png").resize((200, 200)))
        self.cat_sleeping = ImageTk.PhotoImage(Image.open("Pomodoro_cat/Sleep.png").resize((200, 200)))
        self.cat_happy = ImageTk.PhotoImage(Image.open("Pomodoro_cat/EyesOpenHeart.png").resize((200, 200)))

        # Put initial cat image on canvas
        self.cat_image_id = self.cat_canvas.create_image(100, 100, image=self.cat_normal)

        # Timer controls
        self.start_button = ttk.Button(self.bottom_frame, text="Start", command=self.start_timer)
        self.start_button.grid(row=0, column=0, padx=10)

        self.pause_button = ttk.Button(self.bottom_frame, text="Pause", command=self.pause_timer, state=tk.DISABLED)
        self.pause_button.grid(row=0, column=1, padx=10)

        self.skip_button = ttk.Button(self.bottom_frame, text="Skip", command=self.skip_timer)
        self.skip_button.grid(row=0, column=2, padx=10)

        self.reset_button = ttk.Button(self.bottom_frame, text="Reset", command=self.reset_timer)
        self.reset_button.grid(row=0, column=3, padx=10)

        # Settings area
        settings_frame = tk.Frame(self.root, bg='#f5f5f5')
        settings_frame.pack(pady=20)

        tk.Label(settings_frame, text="Focus Time (min):", bg='#f5f5f5').grid(row=0, column=0, padx=5, pady=5)
        self.focus_entry = ttk.Entry(settings_frame, width=5)
        self.focus_entry.insert(0, str(self.settings['focus_time']))
        self.focus_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(settings_frame, text="Break Time (min):", bg='#f5f5f5').grid(row=1, column=0, padx=5, pady=5)
        self.break_entry = ttk.Entry(settings_frame, width=5)
        self.break_entry.insert(0, str(self.settings['break_time']))
        self.break_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(settings_frame, text="Long Break (min):", bg='#f5f5f5').grid(row=2, column=0, padx=5, pady=5)
        self.long_break_entry = ttk.Entry(settings_frame, width=5)
        self.long_break_entry.insert(0, str(self.settings['long_break_time']))
        self.long_break_entry.grid(row=2, column=1, padx=5, pady=5)

        save_button = ttk.Button(settings_frame, text="Save Settings", command=self.save_timer_settings)
        save_button.grid(row=3, columnspan=2, pady=5)

        # Coin display
        coin_frame = tk.Frame(self.root, bg='#f5f5f5')
        coin_frame.pack(pady=10)

        self.coin_label = tk.Label(coin_frame, text=f"Coins: {self.coins}", font=('Arial', 14), bg='#f5f5f5')
        self.coin_label.pack(side=tk.LEFT, padx=10)

        shop_button = ttk.Button(coin_frame, text="Cat Shop", command=self.open_cat_shop)
        shop_button.pack(side=tk.LEFT)

        # Sound buttons
        sound_frame = tk.Frame(self.root, bg='#f5f5f5')
        sound_frame.pack(pady=10)

        ttk.Button(sound_frame, text="Set Focus Sound", command=lambda: self.set_sound('focus_sound')).grid(row=0, column=0, padx=5)
        ttk.Button(sound_frame, text="Set Break Sound", command=lambda: self.set_sound('break_sound')).grid(row=0, column=1, padx=5)
        ttk.Button(sound_frame, text="Set Completion Sound", command=lambda: self.set_sound('task_complete_sound')).grid(row=0, column=2, padx=5)
        ttk.Button(sound_frame, text="Connect to Music App", command=self.connect_music_app).grid(row=0, column=3, padx=5)

        # Start with task input
        self.set_task()

    def set_cat_state(self, state):
        if state == "normal":
            self.cat_canvas.itemconfig(self.cat_image_id, image=self.cat_normal)
        elif state == "sleeping":
            self.cat_canvas.itemconfig(self.cat_image_id, image=self.cat_sleeping)
        elif state == "happy":
            self.cat_canvas.itemconfig(self.cat_image_id, image=self.cat_happy)
        self.cat_state = state

    def set_task(self):
        task = simpledialog.askstring("Set Task", "What would you like to focus on this session?")
        if task:
            self.current_task = task
            self.task_canvas.itemconfigure(self.task_text, text=task)

    def start_timer(self):
        if not self.current_task:
            messagebox.showwarning("No Task", "Please set a task first!")
            return

        if not self.is_running:
            super().start()  # Start base Timer
            self.start_button.config(state=tk.DISABLED)
            self.pause_button.config(state=tk.NORMAL)

        if self.is_focus:
            if self.settings['focus_sound']:
                Thread(target=self.play_sound, args=(self.settings['focus_sound'],)).start()
            self.set_cat_state("sleeping")
        else:
            if self.settings['break_sound']:
                Thread(target=self.play_sound, args=(self.settings['break_sound'],)).start()
            self.set_cat_state("normal")

        self.update_timer()

    def pause_timer(self):
        if self.is_running:
            self.is_running = False
            self.start_button.config(state=tk.NORMAL)
            self.pause_button.config(state=tk.DISABLED)
            winsound.PlaySound(None, winsound.SND_PURGE)

    def skip_timer(self):
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)
        self.next_phase()

    def reset_timer(self):
        super().reset()
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)

        if self.is_focus:
            self.remaining_time = self.settings['focus_time'] * 60
        else:
            self.remaining_time = self.settings['break_time'] * 60
        self.update_display()

    def update_timer(self):
        if self.is_running:
            mins, secs = divmod(self.tick(), 60)
            self.clock_label.config(text=f"{mins:02d}:{secs:02d}")

        if self.remaining_time > 0:
            self.root.after(1000, self.update_timer)
        else:
            self.timer_complete()

    def timer_complete(self):
        self.is_running = False
        if self.settings['task_complete_sound']:
            Thread(target=self.play_sound, args=(self.settings['task_complete_sound'],)).start()

        if self.is_focus:
            self.pomodoro_count += 1
            messagebox.showinfo("Focus Completed", f"Great job! You've completed {self.pomodoro_count} Pomodoros!")

            coins_earned = random.randint(1, 3)
            self.coins += coins_earned
            self.settings['coins'] = self.coins
            self.save_settings()
            self.coin_label.config(text=f"Coins: {self.coins}")

            if self.pomodoro_count % 4 == 0:
                self.is_focus = False
                self.remaining_time = self.settings['long_break_time'] * 60
                self.mode_label.config(text="Long Break Time", fg='#0984e3')
                messagebox.showinfo("Long Break", f"Take a long break of {self.settings['long_break_time']} minutes.")
            else:
                self.is_focus = False
                self.remaining_time = self.settings['break_time'] * 60
                self.mode_label.config(text="Break Time", fg='#00b894')

            self.task_canvas.itemconfigure(self.task_text, fill='gray')
            self.task_canvas.create_line(20, 70, 180, 70, fill='red', width=2)
        else:
            self.is_focus = True
            self.remaining_time = self.settings['focus_time'] * 60
            self.mode_label.config(text="Focus Time", fg='#d63031')
            self.set_task()

        self.update_display()
        self.start_button.config(state=tk.NORMAL)

    def next_phase(self):
        if self.is_focus:
            self.is_focus = False
            self.remaining_time = self.settings['break_time'] * 60
            self.mode_label.config(text="Break Time", fg='#00b894')
            self.set_cat_state("normal")
        else:
            self.is_focus = True
            self.remaining_time = self.settings['focus_time'] * 60
            self.mode_label.config(text="Focus Time", fg='#d63031')
            self.set_cat_state("sleeping")
        self.update_display()

    def update_display(self):
        mins, secs = divmod(self.remaining_time, 60)
        self.clock_label.config(text=f"{mins:02d}:{secs:02d}")

    def save_timer_settings(self):
        try:
            focus_time = int(self.focus_entry.get())
            break_time = int(self.break_entry.get())
            long_break = int(self.long_break_entry.get())

            if focus_time < 1 or break_time < 1 or long_break < 1:
                raise ValueError("Times must be at least 1 minute")

            self.settings['focus_time'] = focus_time
            self.settings['break_time'] = break_time
            self.settings['long_break_time'] = long_break

            self.save_settings()
            messagebox.showinfo("Settings Saved", "Settings have been saved successfully!")
            self.reset_timer()
        except Exception as e:
            messagebox.showerror("Invalid Input", str(e))

    def set_sound(self, sound_type):
        file_path = filedialog.askopenfilename(title=f"Select {sound_type.replace('_', ' ')}",
                                               filetypes=(("WAV files", "*.wav"), ("All files", "*.*")))
        if file_path:
            self.settings[sound_type] = file_path
            self.save_settings()

    def play_sound(self, sound_file):
        try:
            winsound.PlaySound(sound_file, winsound.SND_FILENAME | winsound.SND_ASYNC)
        except:
            pass

    def connect_music_app(self):
        choice = messagebox.askyesno("Music Apps",
                                     "Would you like to open Youtube music?\nRequires internet connection.")
        if choice:
            webbrowser.open("https://music.youtube.com/")

    def open_cat_shop(self):
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

        for item in items:
            row = tk.Frame(item_frame)
            row.pack(fill=tk.X, pady=5)
            tk.Label(row, text=f"{item['icon']} {item['name']}: {item['price']} coins",
                     width=25, anchor=tk.W).pack(side=tk.LEFT)

            state = tk.NORMAL if self.coins >= item['price'] else tk.DISABLED
            ttk.Button(row, text="Buy", command=lambda i=item: self.buy_item(i), state=state).pack(side=tk.RIGHT)

        ttk.Button(shop_window, text="Close", command=shop_window.destroy).pack(pady=10)

    def buy_item(self, item):
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
            self.root.after(3000, lambda: self.set_cat_state("normal" if not self.is_focus else "sleeping"))
        else:
            messagebox.showerror("Not Enough Coins", "You don't have enough coins to buy this item!")


if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroTimer(root)
    root.mainloop()