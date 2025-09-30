# system_info_analyzer.py  (SANITIZED)
import socket
import platform
import psutil
import os
import requests
import subprocess
from datetime import datetime

# NOTE: Do NOT commit real ngrok or secret URLs into the repository.
# Configure your server URL via environment variables or by editing config.example.
NGROK_URL = "https://YOUR_NGROK_URL_HERE"  # ← Placeholder (do not commit real secrets)
SERVER_URLS = [
    f"{NGROK_URL}",                        # Primary: user-provided ngrok / remote URL
    "http://localhost:5000/api/vm_data",   # Fallback: local testing
]

def find_working_server():
    """Automatically find which server URL works (tries /status endpoint)."""
    for server_url in SERVER_URLS:
        if not server_url or "YOUR_NGROK_URL_HERE" in server_url:
            continue
        try:
            print(f"🔍 Testing connection to: {server_url}")
            response = requests.get(server_url.replace('/api/vm_data', '/status'), timeout=5)
            if response.status_code == 200:
                print(f"✅ Server found at: {server_url}")
                return server_url
        except requests.exceptions.RequestException as e:
            print(f"❌ Cannot reach: {server_url} - {e}")
            continue

    print("❌ No servers available. Please check your configuration or run the server locally.")
    return None

def get_active_interface():
    """Get the active network interface with internet access (IPv4)."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
    except Exception:
        ip = None

    if not ip:
        return None, None

    for iface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET and addr.address == ip:
                return iface, addrs
    return None, None

def get_os_info():
    """Get detailed Windows OS info when available using systeminfo; fallback to platform."""
    try:
        output = subprocess.check_output(
            'systeminfo | findstr /B /C:"OS Name" /C:"OS Version"',
            shell=True,
            universal_newlines=True
        )
        lines = output.strip().splitlines()
        os_name = ""
        os_version = ""
        for line in lines:
            if line.startswith("OS Name:"):
                os_name = line.split(":", 1)[1].strip()
            elif line.startswith("OS Version:"):
                os_version = line.split(":", 1)[1].strip()
        return f"{os_name} ({os_version})" if os_name else platform.platform()
    except Exception:
        return platform.platform()

def get_network_info():
    """Capture system and active network info. No personal identifiers hard-coded."""
    info = {}

    info["vm_name"] = platform.node()
    info["os"] = get_os_info()
    try:
        info["username"] = os.getlogin()
    except Exception:
        info["username"] = "unknown"
    info["timestamp"] = datetime.now().isoformat()

    iface, addrs = get_active_interface()
    ipv4_list, ipv6_list, mac_list = [], [], []

    if addrs:
        for addr in addrs:
            if addr.family == socket.AF_INET:
                ipv4_list.append(addr.address)
            elif addr.family == socket.AF_INET6:
                clean_ip = addr.address.split("%")[0]
                ipv6_list.append(clean_ip)
            elif getattr(psutil, "AF_LINK", None) and addr.family == psutil.AF_LINK:
                mac_list.append(addr.address)

    info["ipv4_addresses"] = ipv4_list or ["No IPv4 detected"]
    info["ipv6_addresses"] = ipv6_list or ["No IPv6 detected"]
    info["mac_addresses"] = mac_list or ["No MAC detected"]

    return info

def send_to_server(data, server_url):
    """Send captured data to Flask server."""
    try:
        print(f"📤 Sending to: {server_url}")
        response = requests.post(server_url, json=data, timeout=10)
        if response.status_code == 200:
            print("✅ Data successfully sent to server!")
            return True
        else:
            print(f"⚠️ Server responded with status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Failed to send data: {e}")
        return False

def main():
    print("🚀 Starting System Info Analyzer (sanitized)...")
    print("=" * 60)

    # Prefer environment variable if provided (safer than committing URLs)
    manual_env = os.environ.get("SYSTEM_ANALYZER_SERVER")
    if manual_env:
        SERVER_URLS.insert(0, manual_env)

    server_url = find_working_server()
    if not server_url:
        manual_url = input("🌐 Enter server URL manually (or press Enter to exit): ").strip()
        if manual_url:
            server_url = manual_url
        else:
            print("❌ No server specified. Exiting.")
            return

    data = get_network_info()

    print("\n📊 Captured Information (local preview):")
    print(f"🖥️  VM Name: {data['vm_name']}")
    print(f"💻 OS: {data['os']}")
    print(f"👤 User: {data['username']}")
    print(f"🌐 IPv4: {data['ipv4_addresses']}")
    print(f"🔗 IPv6: {data['ipv6_addresses']}")
    print(f"📟 MAC: {data['mac_addresses']}")
    print("=" * 60)

    # source_ip capture (best-effort)
    try:
        data["source_ip"] = socket.gethostbyname(socket.gethostname())
    except Exception:
        data["source_ip"] = "unknown"

    success = send_to_server(data, server_url)

    if success:
        print("\n🎉 Success! Check your web dashboard for the results.")
    else:
        print("\n💡 Troubleshooting tips:")
        print("   • Ensure the server URL is correct and reachable")
        print("   • Ensure both machines have internet access")
        print("   • Run the server locally for testing")

if __name__ == "__main__":
    main()
