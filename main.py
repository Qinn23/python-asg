import tkinter as tk
from homework_planner import open_homework_planner_window
from pomodoro_timer import PomodoroTimer  # Import the PomodoroTimer class
from calandar_timetable import CalendarApp

# Colors and fonts
BG_COLOR = "#f5f6fa"
BTN_COLOR = "#40739e"
BTN_HOVER = "#273c75"
TEXT_COLOR = "#2d3436"
FONT_TITLE = ("Segoe UI", 22, "bold")
FONT_BTN = ("Segoe UI", 12, "bold")

def on_enter(e):
    e.widget['background'] = BTN_HOVER

def on_leave(e):
    e.widget['background'] = BTN_COLOR

def open_homework_planner():
    open_homework_planner_window()

def open_calendar_app():
    calendar_window = tk.Toplevel(root)
    calendar_window.title("Calendar App")
    calendar_window.geometry("1050x700")
    CalendarApp(calendar_window)  # attach the calendar to this window
    
def open_pomodoro_timer():
    pomo_window = tk.Toplevel(root)
    pomo_window.title("Pomodoro Timer")
    PomodoroTimer(pomo_window)

root = tk.Tk()
root.title("TAR UMT Student Assistant App")
root.configure(bg=BG_COLOR)
root.geometry("420x400")
root.resizable(True, True)

# Center the window
root.update_idletasks()
w = root.winfo_screenwidth()
h = root.winfo_screenheight()
size = tuple(int(_) for _ in root.geometry().split('+')[0].split('x'))
x = w//2 - size[0]//2
y = h//2 - size[1]//2
root.geometry(f"{size[0]}x{size[1]}+{x}+{y}")

main_frame = tk.Frame(root, bg=BG_COLOR)
main_frame.pack(fill="both", expand=True, padx=20, pady=20)

tk.Label(main_frame, text="Main Menu", font=FONT_TITLE, bg=BG_COLOR, fg="black").pack(pady=(10, 20), fill="x")

btn_hw = tk.Button(main_frame, text="Homework Planner", width=22, height=2, bg=BTN_COLOR, fg="white", font=FONT_BTN, bd=0, activebackground=BTN_HOVER, activeforeground="white", command=open_homework_planner, cursor="hand2")
btn_hw.pack(pady=10)
btn_hw.bind("<Enter>", on_enter)
btn_hw.bind("<Leave>", on_leave)

btn_cal = tk.Button(main_frame, text="Calendar App", width=22, height=2, bg=BTN_COLOR, fg="white", font=FONT_BTN, bd=0, activebackground=BTN_HOVER, activeforeground="white", command=open_calendar_app, cursor="hand2")
btn_cal.pack(pady=10)
btn_cal.bind("<Enter>", on_enter)
btn_cal.bind("<Leave>", on_leave)

btn_pomo = tk.Button(main_frame, text="Pomodoro Timer", width=22, height=2, bg=BTN_COLOR, fg="white", font=FONT_BTN, bd=0, activebackground=BTN_HOVER, activeforeground="white", command=open_pomodoro_timer, cursor="hand2")
btn_pomo.pack(pady=10)
btn_pomo.bind("<Enter>", on_enter)
btn_pomo.bind("<Leave>", on_leave)

tk.Label(main_frame, text="© 2025 TAR UMT Student Assistant", font=("Segoe UI", 9), bg=BG_COLOR, fg="#636e72").pack(side="bottom", pady=10, fill="x")

root.mainloop() 