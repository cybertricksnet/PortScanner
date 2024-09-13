import requests
import threading
import socket
from queue import Queue
from tqdm import tqdm
import argparse
from colorama import Fore, Style, init

init(autoreset=True)

# Global variables
print_lock = threading.Lock()
queue = Queue()
valid_endpoints = []
all_ports_status = []

# Function to check the HTTP response on a given port
def portscan(port, target):
    try:
        url = f"http://{target}:{port}"
        response = requests.get(url, timeout=1)  # Shorten timeout to 1 second for faster feedback
        
        if response.status_code == 200:
            with print_lock:
                valid_endpoints.append((port, url))
                print(f"{Fore.GREEN}[200 OK] Found: {url}")
        else:
            with print_lock:
                all_ports_status.append((port, f"{Fore.YELLOW}[{response.status_code}] {url}"))
    except requests.ConnectionError:
        with print_lock:
            all_ports_status.append((port, f"{Fore.RED}Port {port} not open: {url}"))
    except Exception as e:
        with print_lock:
            all_ports_status.append((port, f"{Fore.RED}Error accessing port {port}: {url}, {e}"))

# Thread function
def threader(target, progress_bar):
    while True:
        worker = queue.get()
        portscan(worker, target)
        queue.task_done()
        # Update the progress bar with the current port being scanned
        progress_bar.update(1)
        progress_bar.set_description(f"Scanning Port {worker}")

# Main function to initialize the scanner
def main():
    parser = argparse.ArgumentParser(description="HTTP-based port scanner with logging")
    parser.add_argument("target", help="Target IP address or domain to scan (e.g., 'example.com' or '127.0.0.1')")
    parser.add_argument("--start-port", type=int, default=1, help="Start port number (default is 1)")
    parser.add_argument("--end-port", type=int, default=65535, help="End port number (default is 65535)")
    args = parser.parse_args()

    target = args.target

    # Test if the domain can be resolved
    try:
        socket.gethostbyname(target)
    except socket.gaierror:
        print(f"{Fore.RED}Could not resolve domain: {target}")
        return

    # Progress bar setup
    total_ports = args.end_port - args.start_port + 1
    progress_bar = tqdm(total=total_ports, ncols=80, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} ({rate_fmt})')

    # Create thread pool (increase threads for faster scan)
    for x in range(500):
        t = threading.Thread(target=threader, args=(target, progress_bar))
        t.daemon = True
        t.start()

    print(f"Scanning all HTTP ports ({args.start_port}-{args.end_port}) on {target}...")
    for worker in range(args.start_port, args.end_port + 1):
        queue.put(worker)

    queue.join()
    progress_bar.close()

    # Sort ports by their number to ensure correct order
    all_ports_status.sort(key=lambda x: x[0])

    # Display valid HTTP endpoints
    if valid_endpoints:
        print("\nValid HTTP Endpoints (200 OK):")
        for port, endpoint in valid_endpoints:
            print(f"[200 OK] {endpoint}")
    else:
        print("\nNo valid HTTP endpoints found.")
    
    # Display all scanned port statuses
    print("\nPort Scan Results:")
    for port, status in all_ports_status:
        print(status)

if __name__ == "__main__":
    main()
