"""
    Main method, starts the welcome window.
"""
from main_window import MainWindow
from welcome_window import WelcomeWindow
import tkinter as tk


if __name__ == '__main__':
    """Create the Tkinter root, attach the MainWindow to it and then start the application loop."""
    root = tk.Tk()
    main_window = MainWindow(root)
    root.mainloop()

