import tkinter as tk

from ui.design import apply_design
from views.auth_view import create_auth_view


window = tk.Tk()
window.title("Personal Finance Manager")
window.geometry("480x560")
window.resizable(False, False)

apply_design(window)
create_auth_view(window)

window.mainloop()
