# main.py
import tkinter as tk
from logic import QuizManager
from gui import QuizApp

if __name__ == "__main__":
    root = tk.Tk()
    manager = QuizManager()
    app = QuizApp(root, manager)
    root.mainloop()