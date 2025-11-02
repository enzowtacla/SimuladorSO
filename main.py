import tkinter as tk
from Simulador import Interface

# mains apenas roda a interface
if __name__ == "__main__":
    root = tk.Tk()
    app = Interface(root)
    root.mainloop()