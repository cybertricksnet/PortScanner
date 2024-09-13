import socket
import threading
from queue import Queue
import requests
from tqdm import tqdm
import argparse

# Global variables
print_lock = threading.Lock()
queue = Queue()
open_ports = []
valid_endpoints = []

# Function to check if port is open and if it returns a 200 OK for HTTP
def portscan(port, target):
    try:
        # Check if the port is open
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)  # Timeout of 2 seconds for each port
        result = sock.connect_ex((target, port))
        sock.close()
        
        if result == 0:
            # Try to send an HTTP request to the open port
            try:
                url = f"http://{target}:{port}"
                response = requests.get(url, timeout=2)
                if response.status_code == 200:
                    with print_lock:
                        valid_endpoints.append(url)
                open_ports.append(port)
            except Exception as e:
                pass
    except Exception as e:
        pass

# Thread function
def threader(target):
    while True:
        worker = queue.get()
        portscan(worker, target)
        queue.task_done()

# Main function to initialize the scanner
def main():
    parser = argparse.ArgumentParser(description="Port scanner with HTTP status check")
    parser.add_argument("target", help="Target IP address or domain to scan (e.g., 'example.com' or '127.0.0.1')")
    args = parser.parse_args()

    target = socket.gethostbyname(args.target)  # Resolve the domain to an IP address

    # Create thread pool
    for x in range(100):
        t = threading.Thread(target=threader, args=(target,))
        t.daemon = True
        t.start()

    print("Scanning all ports (1-65535)...")
    for worker in tqdm(range(1, 65535), desc="Scanning Ports", ncols=80, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}'):
        queue.put(worker)

    queue.join()

    # Display open ports and valid endpoints
    if open_ports:
        print("\nOpen ports:")
        for port in open_ports:
            print(f"Port {port} is open")
    else:
        print("\nNo open ports found.")
    
    if valid_endpoints:
        print("\nValid HTTP Endpoints (200 OK):")
        for endpoint in valid_endpoints:
            print(f"[200 OK] {endpoint}")
    else:
        print("\nNo valid HTTP endpoints found.")

if __name__ == "__main__":
    main()
