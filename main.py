import threading
import time

from server import server
from client import  client

server_thread = threading.Thread(target=server)
server_thread.daemon = True
server_thread.start()

time.sleep(1)

client()