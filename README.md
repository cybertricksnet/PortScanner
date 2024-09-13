
# PortScanner

**PortScanner** is a Python tool that scans HTTP ports on a target domain or IP address. It uses multiple threads to quickly check which ports are open and which are closed. This is helpful for testing web services or checking security on a server.

## Requirements
- Python 3.7 or higher

## Installation

- **Clone this repository**:
   ```bash
   git clone https://github.com/cybertricksnet/PortScanner.git
   ```

- **Change to the directory**:
   ```bash
   cd PortScanner
   ```

- **Install necessary libraries**:
   Install any missing Python libraries by running:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### **Basic scan of all ports (1-65535)**:
```bash
python3 PortScanner.py example.com
```
This will scan all ports from 1 to 65535 on the domain `example.com` and tell you if they are open or closed.

### **Scanning a specific range of ports**:
```bash
python3 PortScanner.py cms1.bac.edu.my --start-port 8000 --end-port 9000
```
This scans ports 8000 to 9000 on the domain `example.com` and shows the results.

## Port Range Explanation

You can use the `--start-port` and `--end-port` options to limit the range of ports being scanned. For example:
   ```bash
   python3 PortScanner.py example.com --start-port 1000 --end-port 2000
   ```

This command will only scan ports between 1000 and 2000, which can save time compared to scanning the entire range.

### Example of Output

The tool will show you if each port is open or not while it's scanning:
```bash
Port 874 not open: http://example.com:874
Port 875 not open: http://example.com:875
[200 OK] Found: http://example.com:80
```

### Interrupting the Scan

If you stop the scan with **Ctrl+C**, the tool will summarize any open ports it has found so far:
```bash
[!] Scan interrupted by user.

Valid HTTP Endpoints (200 OK):
[200 OK] http://example.com:80
```

## Features

- **Multithreaded**: This means it scans multiple ports at once, making it faster.
- **Custom port ranges**: You can scan any range of ports you want.
- **Clear results**: It shows which ports are open or closed as it scans.
- **Graceful stop**: When you stop the scan, it will still show the open ports.

## Notes

- You can adjust the range of ports depending on what you need.
- The tool is simple and useful for checking if certain web ports are open.

## Licensing

[![MIT License](https://img.shields.io/badge/license-MIT_License-blue)](https://opensource.org/licenses/MIT)

<sup>NOTE: Downloading this repository may trigger a false-positive alert from your anti-virus or anti-malware software. You can whitelist the filepath if necessary. This repository is safe to use and can be used free of charge. However, it is not recommended to store these files on critical systems, as they could pose a risk of local file inclusion attacks if improperly handled.</sup>
