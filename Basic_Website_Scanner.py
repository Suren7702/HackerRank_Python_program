import socket
from datetime import datetime

def scan_ports(target, start_port=1, end_port=1024):
    print(f"Starting scan on {target}")
    print(f"Scanning ports {start_port} to {end_port}...\n")
    start_time = datetime.now()

    try:
        for port in range(start_port, end_port + 1):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)  # Fast scanning
            result = s.connect_ex((target, port))  # 0 = open
            if result == 0:
                print(f"[+] Port {port} is OPEN")
            s.close()
    except KeyboardInterrupt:
        print("\n[!] Scan aborted by user.")
    except socket.gaierror:
        print("[!] Hostname could not be resolved.")
    except socket.error:
        print("[!] Could not connect to server.")
    
    end_time = datetime.now()
    total_time = end_time - start_time
    print(f"\nScan completed in: {total_time}")

if __name__ == "__main__":
    target = input("Enter IP or hostname to scan: ")
    scan_ports(target)
