import threading
import time
from server import server
from gui import LoginApp
import tkinter as tk

server_thread = threading.Thread(target=server)
server_thread.daemon = True
server_thread.start()

time.sleep(1)

root = tk.Tk()
app = LoginApp(root)
root.mainloop()