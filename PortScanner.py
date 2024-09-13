import socket
import threading
from queue import Queue
from tqdm import tqdm
import argparse

# Global variables
print_lock = threading.Lock()
queue = Queue()
open_ports = []

# Function to scan a single port
def portscan(port, target):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)  # Timeout of 2 seconds for each port
        result = sock.connect_ex((target, port))  # Use connect_ex to avoid crashing
        if result == 0:
            with print_lock:
                open_ports.append(port)
        sock.close()
    except Exception as e:
        pass  # We ignore all exceptions, but they can be logged for debugging

# Thread function
def threader(target):
    while True:
        worker = queue.get()
        portscan(worker, target)
        queue.task_done()

# Main function to initialize the scanner
def main():
    parser = argparse.ArgumentParser(description="Simple port scanner using multithreading")
    parser.add_argument("target", help="Target IP address or domain to scan (e.g., 'example.com' or '127.0.0.1')")
    parser.add_argument("--specific-ports", nargs='*', type=int, help="List of specific ports to scan (e.g., 80 8080 443)")
    args = parser.parse_args()

    target = socket.gethostbyname(args.target)  # Resolve the domain to an IP address

    # Create thread pool
    for x in range(100):
        t = threading.Thread(target=threader, args=(target,))
        t.daemon = True
        t.start()

    if args.specific_ports:
        # Scan specific ports first if provided
        print(f"Scanning specific ports: {args.specific_ports}")
        for port in args.specific_ports:
            queue.put(port)

    # Define the range of ports to scan (1 to 65535) if no specific ports were provided
    else:
        print("Scanning all ports (1-65535)...")
        for worker in tqdm(range(1, 65535), desc="Scanning Ports", ncols=80, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}'):
            queue.put(worker)

    queue.join()

    # Display open ports
    if open_ports:
        print("\nOpen ports:")
        for port in open_ports:
            print(f"Port {port} is open")
    else:
        print("\nNo open ports found.")

if __name__ == "__main__":
    main()
