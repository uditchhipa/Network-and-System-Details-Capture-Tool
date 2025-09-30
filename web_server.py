#!/usr/bin/env python3
"""
server.py (SANITIZED)

- No hard-coded ngrok/public URLs.
- Use environment variables to configure ngrok or public URL.
- Do NOT use this against devices without explicit authorization.
"""

from flask import Flask, request, jsonify
from datetime import datetime
import threading
import webbrowser
import socket
import os
import logging

# Optional pyngrok use: only enabled if user sets USE_NGROK=1 and pyngrok available.
USE_NGROK = os.environ.get("USE_NGROK", "0") == "1"
NGROK_AUTH_TOKEN = os.environ.get("NGROK_AUTH_TOKEN", None)  # do not commit tokens
NGROK_PUBLIC_URL = os.environ.get("PUBLIC_URL", "")  # user-provided public URL (optional)

app = Flask(__name__)

# In-memory stores (small demo). For production use a database.
vm_data_store = []
latest_data = None

# set up basic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def get_local_ip():
    """Best-effort local IP address (not public IP)."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"

def get_latest_data_html():
    """Return HTML snippet of latest_data or placeholder."""
    global latest_data
    if not latest_data:
        return '''
        <div class="data-card warning">
            <h3>🕐 Waiting for VM Data...</h3>
            <p>Run the capture tool on an authorized test VM to push data here.</p>
        </div>
        '''
    ipv4_list = latest_data.get('ipv4_addresses', [])
    ipv6_list = latest_data.get('ipv6_addresses', [])
    mac_list = latest_data.get('mac_addresses', [])
    ipv4_display = ', '.join(ipv4_list) if ipv4_list else 'None'
    ipv6_display = ', '.join(ipv6_list) if ipv6_list else 'None'
    mac_display = ', '.join(mac_list) if mac_list else 'None'

    html = f'''
    <div class="data-card success">
        <h3>✅ New VM Data Received</h3>
        <p><strong>VM Name:</strong> {latest_data.get('vm_name', 'Unknown')}</p>
        <p><strong>IPv4:</strong> {ipv4_display}</p>
        <p><strong>IPv6:</strong> {ipv6_display}</p>
        <p><strong>MAC:</strong> {mac_display}</p>
        <p><strong>OS:</strong> {latest_data.get('os', 'Unknown')}</p>
        <p><strong>User:</strong> {latest_data.get('username', 'Unknown')}</p>
        <p><strong>Captured:</strong> {latest_data.get('timestamp', 'Unknown')}</p>
        <p><strong>Received From:</strong> {latest_data.get('server_ip', 'Unknown')}</p>
    </div>
    '''
    return html

def get_all_data_html():
    """Return HTML for the last few captures."""
    if not vm_data_store:
        return '''
        <div class="data-card warning">
            <p>No VM data received yet. The dashboard will update when data arrives.</p>
        </div>
        '''
    html = ''
    for i, data in enumerate(reversed(vm_data_store[-5:])):
        ipv4 = data.get('ipv4_addresses', ['None'])[0]
        ipv6 = data.get('ipv6_addresses', ['None'])[0]
        mac = data.get('mac_addresses', ['None'])[0]
        html += f'''
        <div class="data-card">
            <h4>VM #{len(vm_data_store) - i}: {data.get('vm_name', 'Unknown')}</h4>
            <p><strong>Primary IPv4:</strong> {ipv4}</p>
            <p><strong>Primary IPv6:</strong> {ipv6}</p>
            <p><strong>MAC:</strong> {mac}</p>
            <p><strong>OS:</strong> {data.get('os', 'Unknown')}</p>
            <p><strong>Time:</strong> {data.get('timestamp', 'Unknown')}</p>
        </div>
        '''
    return html

@app.route('/')
def index():
    """Simple dashboard page. Public URL displayed only if configured by user."""
    local_ip = get_local_ip()
    total_vms = str(len(vm_data_store))
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    public_url_display = NGROK_PUBLIC_URL or "Not configured"

    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>VM Capture Dashboard (SANITIZED)</title>
        <meta http-equiv="refresh" content="10">
        <style>
            body {{ font-family: Arial, sans-serif; background:#f0f2f5; margin:0; padding:20px; }}
            .container {{ max-width:1100px; margin:0 auto; background:white; padding:24px; border-radius:10px; }}
            .header {{ padding:20px 10px; text-align:center; }}
            .data-card {{ background:#fafafa; margin:14px 0; padding:18px; border-radius:8px; border-left:5px solid #007bff; }}
            .success {{ border-left-color: #28a745; }}
            .warning {{ border-left-color: #ffc107; }}
            .stats {{ display:flex; gap:10px; justify-content:space-around; margin-bottom:16px; }}
            .stat-box {{ padding:12px; border-radius:6px; background:#f7f9fc; text-align:center; flex:1; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>VM Capture Dashboard (SANITIZED)</h1>
                <p><em>Use only in authorized environments. Do not collect data from devices without consent.</em></p>
                <div class="stats">
                    <div class="stat-box"><h3>Total VMs</h3><h2>{total_vms}</h2></div>
                    <div class="stat-box"><h3>Public URL</h3><h2>{public_url_display}</h2></div>
                    <div class="stat-box"><h3>Last Update</h3><h2>{current_time}</h2></div>
                </div>
            </div>
            <h2>Latest Capture</h2>
            {get_latest_data_html()}
            <h2>Recent Captures</h2>
            {get_all_data_html()}
        </div>
    </body>
    </html>
    '''
    return html

@app.route('/api/vm_data', methods=['POST'])
def receive_vm_data():
    """Receive JSON payload from authorized capture tools."""
    global latest_data
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status':'error','message':'No data received'}), 400
        # Tag with server metadata
        data['received_at'] = datetime.now().isoformat()
        data['server_ip'] = request.remote_addr
        vm_data_store.append(data)
        latest_data = data
        logging.info(f"Data received from {data.get('vm_name','Unknown')} | IP: {request.remote_addr}")
        return jsonify({'status':'success','message':'Data received successfully'}), 200
    except Exception as e:
        logging.exception("Error processing VM data")
        return jsonify({'status':'error','message': str(e)}), 400

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify({'status':'running', 'vms_captured': len(vm_data_store), 'timestamp': datetime.now().isoformat()})

def open_local_browser():
    """Open a local browser to the dashboard (only useful in local dev)."""
    try:
        webbrowser.open('http://127.0.0.1:5000')
    except Exception:
        pass

if __name__ == "__main__":
    logging.info("Starting VM Capture Web Server (SANITIZED)")
    logging.info("=" * 60)

    # Configure public URL only from environment; do not hardcode tokens/URLs in repo.
    # If you want to enable automatic ngrok, set USE_NGROK=1 and NGROK_AUTH_TOKEN in env, and ensure pyngrok installed.
    public_url = ""
    if USE_NGROK:
        try:
            from pyngrok import ngrok, conf
            if NGROK_AUTH_TOKEN:
                conf.get_default().auth_token = NGROK_AUTH_TOKEN
            # Create a tunnel only if user explicitly enabled it via env var.
            ngrok_tunnel = ngrok.connect(5000, bind_tls=True)
            public_url = str(ngrok_tunnel.public_url)
            logging.info(f"Ngrok tunnel started at: {public_url}")
        except Exception as e:
            logging.exception("Failed to start ngrok tunnel automatically. Set PUBLIC_URL env if needed.")
    else:
        public_url = os.environ.get("PUBLIC_URL", "")
        if public_url:
            logging.info(f"Using configured PUBLIC_URL: {public_url}")

    # Optionally open browser in local dev only if OPEN_BROWSER=1
    if os.environ.get("OPEN_BROWSER", "0") == "1":
        threading.Timer(1, open_local_browser).start()

    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        logging.info("Server stopped by user")
