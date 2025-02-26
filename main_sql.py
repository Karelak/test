import tkinter as tk
from theater_system_sql import TheaterTicketSystem

if __name__ == "__main__":
    root = tk.Tk()
    app = TheaterTicketSystem(root)
    root.mainloop()
