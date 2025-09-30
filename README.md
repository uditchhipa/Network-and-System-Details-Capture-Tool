# Smart Network Capture Tool

A simple Python project that captures basic system and network information from a machine and displays it on a real-time web dashboard using Flask and Ngrok.

⚠️ **Disclaimer:** This project is for **educational and research purposes only**. Do not use it on systems without permission.

---

## ✨ Features

* Collects details like:

  * OS version
  * Username
  * IPv4 / IPv6 addresses
  * MAC addresses
* Sends captured data to a Flask web server
* Real-time web dashboard with:

  * Latest system capture
  * History of last 5 captures
* Automatic Ngrok integration for external access

---

## 📂 Project Structure

```
smart-network-capture/
│── capture.py       # Run on target machine to collect info
│── web_server.py    # Run on your machine to receive + view data
│── requirements.txt # Python dependencies
│── README.md        # Project documentation
```

---

## ⚙️ Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/smart-network-capture.git
   cd smart-network-capture
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

---

## 🚀 Usage

### Start the Web Server

Run on your own machine to receive and view data:

```bash
python web_server.py
```

* This starts a Flask server on `http://127.0.0.1:5000/`
* An Ngrok URL will also be generated (so remote devices can connect).
* A dashboard will open in your browser.

### Run the Capture Tool

Run on the other machine to send data to the server:

```bash
python capture.py
```

* The tool will auto-detect the server URL.
* If it cannot connect, you can manually enter the Ngrok URL shown in the server logs.
* Captured details will appear instantly on the web dashboard.

---

## 📸 Example Dashboard

*(You can add a screenshot here after running it once.)*

---

## 🛠 Requirements

* Python 3.7+
* Dependencies:

  * Flask
  * Requests
  * Psutil
  * Pyngrok

Install with:

```bash
pip install -r requirements.txt
```

---

## 📜 License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.
