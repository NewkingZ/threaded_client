# Root program that holds the main process

import sys
import os.path
import tkinter as tk
import modules.mainapp as mainapp

VERSION = "1.0"

# Start GUI & set icon
root = tk.Tk()
mainapp.ThreadedClient(root, "Sample Threaded Client V" + VERSION, VERSION)

# Hold the main loop
root.mainloop()
