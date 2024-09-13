import requests
import threading
import socket
from queue import Queue
from tqdm import tqdm
import argparse
from colorama import Fore, Style, init
import signal
import sys

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
def threader(target):
    while True:
        worker = queue.get()
        portscan(worker, target)
        queue.task_done()

# Function to show the summary of the scan
def show_summary():
    if valid_endpoints:
        print("\nValid HTTP Endpoints (200 OK):")
        for port, endpoint in valid_endpoints:
            print(f"[200 OK] {endpoint}")
    else:
        print("\nNo valid HTTP endpoints found.")

    print("\nPort Scan Results:")
    for port, status in all_ports_status:
        print(status)

# Signal handler to display the summary when Ctrl+C is pressed
def signal_handler(sig, frame):
    print("\n\n[!] Scan interrupted by user.")
    show_summary()
    sys.exit(0)

# Main function to initialize the scanner
def main():
    signal.signal(signal.SIGINT, signal_handler)  # Handle Ctrl+C to show summary
    
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

    # Create thread pool
    for x in range(500):
        t = threading.Thread(target=threader, args=(target,))
        t.daemon = True
        t.start()

    print(f"Scanning HTTP ports ({args.start_port}-{args.end_port}) on {target}...")

    # Customize progress bar to show the current port being checked along with the range
    total_ports = args.end_port - args.start_port + 1
    for worker in tqdm(range(args.start_port, args.end_port + 1), 
                       desc=f"Scanning ports {args.start_port}-{args.end_port}", 
                       ncols=80, 
                       bar_format=f'Scanning Port {{n_fmt}}/({args.start_port}-{args.end_port}) | {{percentage:3.0f}}%'):
        queue.put(worker)

    queue.join()

    # Show summary when scan is done
    show_summary()

if __name__ == "__main__":
    main()
