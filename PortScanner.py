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

print_lock = threading.Lock()
queue = Queue()
valid_endpoints = []

def portscan(port, target):
    try:
        url = f"http://{target}:{port}"
        response = requests.get(url, timeout=1)
        
        if response.status_code == 200:
            with print_lock:
                valid_endpoints.append((port, url))
                print(f"{Fore.CYAN}[200 OK] Found: {url}")
        else:
            with print_lock:
                print(f"{Fore.RED}Port {port} not open: {url}")
    except requests.ConnectionError:
        with print_lock:
            print(f"{Fore.RED}Port {port} not open: {url}")
    except Exception:
        with print_lock:
            print(f"{Fore.RED}Port {port} not open: {url}")

def threader(target):
    while True:
        worker = queue.get()
        portscan(worker, target)
        queue.task_done()

def show_summary():
    if valid_endpoints:
        print("\nValid HTTP Endpoints (200 OK):")
        for port, endpoint in valid_endpoints:
            print(f"{Fore.CYAN}[200 OK] {endpoint}")
    else:
        print(f"{Fore.RED}\nNo valid HTTP endpoints found.")

def signal_handler(sig, frame):
    print("\n\n[!] Scan interrupted by user.")
    show_summary()
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)
    
    parser = argparse.ArgumentParser(description="HTTP-based port scanner with logging")
    parser.add_argument("target", help="Target IP address or domain to scan (e.g., 'example.com' or '127.0.0.1')")
    parser.add_argument("--start-port", type=int, default=1, help="Start port number (default is 1)")
    parser.add_argument("--end-port", type=int, default=65535, help="End port number (default is 65535)")
    args = parser.parse_args()

    target = args.target

    try:
        socket.gethostbyname(target)
    except socket.gaierror:
        print(f"{Fore.RED}Could not resolve domain: {target}")
        return

    for x in range(500):
        t = threading.Thread(target=threader, args=(target,))
        t.daemon = True
        t.start()

    print(f"Scanning HTTP ports ({args.start_port}-{args.end_port}) on {target}...")

    for worker in tqdm(range(args.start_port, args.end_port + 1), desc=f"Scanning ports {args.start_port}-{args.end_port}", ncols=80):
        queue.put(worker)

    queue.join()

    show_summary()

if __name__ == "__main__":
    main()
