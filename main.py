import tkinter as tk
from homework_planner import open_homework_planner_window

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
    cal_window = tk.Toplevel(root)
    cal_window.title("Calendar App")
    cal_window.configure(bg=BG_COLOR)
    tk.Label(cal_window, text="Calendar App (Coming Soon!)", font=FONT_BTN, bg=BG_COLOR, fg=TEXT_COLOR).pack(padx=30, pady=30, fill="both", expand=True)

root = tk.Tk()
root.title("TAR UMT Student Assistant App")
root.configure(bg=BG_COLOR)
root.geometry("420x320")
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

tk.Label(main_frame, text="© 2025 TAR UMT Student Assistant", font=("Segoe UI", 9), bg=BG_COLOR, fg="#636e72").pack(side="bottom", pady=10, fill="x")

root.mainloop() 