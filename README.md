# RDP Brute Force Tool
==========================

A Python script designed to perform a brute-force attack on Remote Desktop Protocol (RDP) connections.

## Overview
------------

This script uses a combination of IP addresses, usernames, and passwords to attempt to connect to RDP servers. It employs multithreading to process multiple combinations concurrently, making it a efficient tool for brute-force attacks.

## Features
------------

* **Input files**: Reads input data from three files: `ip.txt`, `users.txt`, and `passwords.txt`
* **Combination generator**: Generates combinations of IP addresses, usernames, and passwords in the following order:
	+ For each password
	+ For each username
	+ For each IP address
* **RDP connection attempts**: Attempts to connect to each RDP server using the `xfreerdp` command (on Linux) or `wfreerdp.exe` (on Windows) with the `+auth-only` flag
* **Timeout and threading**: Uses a timeout of 15 seconds for each connection attempt and employs multithreading to process multiple combinations concurrently (max 30 threads)
* **Output**: Writes successful combinations to a file named `good.txt` in the format "ip:port /d:<server> | username | password"
* **Error handling**: Handles errors and exceptions, including file reading errors, connection timeouts, and authentication failures

## Usage
-----

### Prerequisites

1. Install `xfreerdp` on Linux or download `wfreerdp.exe` on Windows.
2. Create the input files (`ip.txt`, `users.txt`, and `passwords.txt`) with the required data.

### Running the Script

1. Run the script using Python: `python script_name.py`

## Notes
-----

* This script is designed for brute-force attacks and should be used responsibly and in compliance with applicable laws and regulations.
* Use at your own risk.
* This script is for educational purposes only.

## Input Files
--------------

* `ip.txt`: contains a list of IP addresses, either in the format "IP" or "IP:port"
* `users.txt`: contains a list of usernames
* `passwords.txt`: contains a list of passwords

## Output File
--------------

* `good.txt`: contains successful combinations in the format "ip:port /d:<server> | username | password"
