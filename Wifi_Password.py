import subprocess

def get_current_wifi_password():
    # Get currently connected SSID
    output = subprocess.check_output("netsh wlan show interfaces", shell=True).decode()
    ssid_line = [line for line in output.split("\n") if "SSID" in line and "BSSID" not in line]
    if not ssid_line:
        print("Not connected to any Wi-Fi.")
        return
    ssid = ssid_line[0].split(":")[1].strip()

    # Get password for the connected SSID
    profile_info = subprocess.check_output(f'netsh wlan show profile name="{ssid}" key=clear', shell=True).decode()
    for line in profile_info.split("\n"):
        if "Key Content" in line:
            password = line.split(":")[1].strip()
            print(f"Connected SSID: {ssid}")
            print(f"Password: {password}")
            return
    print(f"Password for {ssid} not found or not saved.")

if __name__ == "__main__":
    get_current_wifi_password()
