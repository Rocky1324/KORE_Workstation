import os
import sys
import socket
import qrcode
import threading
import subprocess
import tkinter as tk
from PIL import Image, ImageTk

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def show_qr_window(url):
    root = tk.Tk()
    root.title("Scannez pour Flet Mobile")
    root.geometry("400x450")
    
    label_info = tk.Label(root, text=f"Lien de développement :\n{url}", font=("Arial", 10))
    label_info.pack(pady=10)
    
    # Generate QR
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to Tkinter format
    tk_img = ImageTk.PhotoImage(img)
    label_qr = tk.Label(root, image=tk_img)
    label_qr.image = tk_img # Keep reference
    label_qr.pack(pady=10)
    
    btn_close = tk.Button(root, text="Fermer", command=root.destroy)
    btn_close.pack(pady=10)
    
    root.mainloop()

def run_flet_server(port):
    print(f"Lancement du serveur Flet sur le port {port}...")
    # Use the venv flet if possible
    flet_exe = os.path.join(os.getcwd(), "venv", "Scripts", "flet.exe")
    if not os.path.exists(flet_exe):
        flet_exe = "flet"
        
    cmd = [flet_exe, "run", "--web", "--host", "0.0.0.0", "--port", str(port), "mobile/main.py"]
    subprocess.run(cmd)

if __name__ == "__main__":
    port = 8551
    ip = get_local_ip()
    flet_url = f"http://{ip}:{port}"
    
    print("="*40)
    print(f"ADRESSE : {flet_url}")
    print("="*40)
    
    # Start server in thread
    server_thread = threading.Thread(target=run_flet_server, args=(port,), daemon=True)
    server_thread.start()
    
    # Show QR Window in main thread
    show_qr_window(flet_url)
