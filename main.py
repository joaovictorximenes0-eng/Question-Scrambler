# main.py
import tkinter as tk
from src.logic import QuizManager
from src.gui import QuizApp

if __name__ == "__main__":
    root = tk.Tk()
    manager = QuizManager()
    app = QuizApp(root, manager)
    root.mainloop()