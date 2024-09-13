import requests
import threading
from queue import Queue
from tqdm import tqdm
import argparse

# Global variables
print_lock = threading.Lock()
queue = Queue()
valid_endpoints = []

# Function to check the HTTP response on a given port
def portscan(port, target):
    try:
        url = f"http://{target}:{port}"
        response = requests.get(url, timeout=2)  # Timeout of 2 seconds for each request
        if response.status_code == 200:
            with print_lock:
                valid_endpoints.append(url)
    except Exception:
        pass  # Ignore any errors (e.g., connection refused, timeout)

# Thread function
def threader(target):
    while True:
        worker = queue.get()
        portscan(worker, target)
        queue.task_done()

# Main function to initialize the scanner
def main():
    parser = argparse.ArgumentParser(description="HTTP-based port scanner")
    parser.add_argument("target", help="Target IP address or domain to scan (e.g., 'example.com' or '127.0.0.1')")
    args = parser.parse_args()

    target = args.target

    # Create thread pool
    for x in range(100):
        t = threading.Thread(target=threader, args=(target,))
        t.daemon = True
        t.start()

    print(f"Scanning all HTTP ports (1-65535) on {target}...")
    for worker in tqdm(range(1, 65535), desc="Scanning Ports", ncols=80, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}'):
        queue.put(worker)

    queue.join()

    # Display valid HTTP endpoints
    if valid_endpoints:
        print("\nValid HTTP Endpoints (200 OK):")
        for endpoint in valid_endpoints:
            print(f"[200 OK] {endpoint}")
    else:
        print("\nNo valid HTTP endpoints found.")

if __name__ == "__main__":
    main()
