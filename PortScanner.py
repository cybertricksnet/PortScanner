import socket
import threading
from queue import Queue

print_lock = threading.Lock()
target = "127.0.0.1"
queue = Queue()
open_ports = []

def portscan(port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((target, port))
        with print_lock:
            print(f"Port {port} is open")
            open_ports.append(port)
        sock.close()
    except:
        pass

def threader():
    while True:
        worker = queue.get()
        portscan(worker)
        queue.task_done()

for x in range(100):
    t = threading.Thread(target=threader)
    t.daemon = True
    t.start()

for worker in range(1, 65535):
    queue.put(worker)

queue.join()

print("Open ports:", open_ports)
