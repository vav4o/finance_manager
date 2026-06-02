import tkinter as tk

from services.auth_service import logout_user
from ui.design import apply_design
from views.auth_view import create_auth_view
from views.dashboard_view import create_dashboard_view


window = tk.Tk()
window.title("Personal Finance Manager")
window.geometry("500x650")
window.resizable(False, False)

apply_design(window)


def show_login():
    window.geometry("500x650")
    create_auth_view(window, show_dashboard)


def show_dashboard(user):
    create_dashboard_view(window, user, logout)


def logout():
    logout_user()
    show_login()


show_login()

window.mainloop()
