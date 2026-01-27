import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
from tkinter import simpledialog
import threading
import websocket
import sys

class WebSocketTester:
    def __init__(self, root):
        self.root = root
        self.root.title("WebSocket Tester")
        self.ws = None
        self.token = simpledialog.askstring("Token", "Enter your authentication token:")
        tk.Label(root, text="WebSocket URL").pack()
        self.url_entry = tk.Entry(root, width=50)
        self.url_entry.pack()
        self.url_entry.insert(0, "ws://localhost:8000/ws/?token=" + self.token)
        self.connect()

        self.connect_btn = tk.Button(root, text="Connect", command=self.connect)
        self.connect_btn.pack(pady=5)

        self.log = scrolledtext.ScrolledText(root, width=60, height=15)
        self.log.pack()

        self.msg_entry = tk.Entry(root, width=50)
        self.msg_entry.pack(pady=5)

        self.send_btn = tk.Button(root, text="Send", command=self.send)
        self.send_btn.pack()

    def log_msg(self, msg):
        self.log.insert(tk.END, msg + "\n")
        self.log.see(tk.END)

    def connect(self):
        def run():
            self.ws = websocket.WebSocketApp(
                self.url_entry.get(),
                on_message=lambda ws, msg: self.log_msg(f"⬅ {msg}"),
                on_error=lambda ws, err: self.log_msg(f"❌ {err}"),
                on_close=lambda ws: self.log_msg("🔌 Connection closed"),
                on_open=lambda ws: self.log_msg("✅ Connected")
            )
            self.ws.on_open = lambda ws: self.log_msg("✅ Connected")
            self.ws.run_forever()

        threading.Thread(target=run, daemon=True).start()

    def send(self):
        if self.ws:
            msg = self.msg_entry.get()
            self.ws.send(msg)
            self.log_msg(f"➡ {msg}")
            self.msg_entry.delete(0, tk.END)

class Endpointester:
    def __init__(self, root):
        self.root = root
        self.root.title("Endpoint Tester")

        tk.Label(root, text="Endpoint URL").pack()
        self.url_entry = tk.Entry(root, width=50)
        self.url_entry.pack()
        self.token_entry = tk.Entry(root, width=50)
        self.token_entry.pack()
        self.url_entry.insert(0, "http://localhost:8000/")

        self.test_btn = tk.Button(root, text="Test Endpoint", command=self.test_endpoint)
        self.test_btn.pack(pady=5)

        self.log = scrolledtext.ScrolledText(root, width=60, height=15)
        self.log.pack()

    def log_msg(self, msg):
        self.log.insert(tk.END, msg + "\n")
        self.log.see(tk.END)

    def test_endpoint(self):
        import requests
        url = self.url_entry.get()
        token = self.token_entry.get()
        headers = {"Authorization": f"Token {token}"}
        try:
            response = requests.get(url, headers=headers)
            self.log_msg(f"Response Code: {response.status_code}")
            self.log_msg(f"Response Body: {response.text}")
        except Exception as e:
            self.log_msg(f"Error: {e}")
if sys.argv[1] == "ws":
    root = tk.Tk()
    app = WebSocketTester(root)
    root.mainloop()
else:
    root = tk.Tk()
    app = Endpointester(root)
    root.mainloop()

