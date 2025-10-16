import customtkinter as ctk
from ui.ui import AppUI


def main():

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("assets/theme.json")

    app = AppUI()
    app.mainloop()


if __name__ == "__main__":
    main()