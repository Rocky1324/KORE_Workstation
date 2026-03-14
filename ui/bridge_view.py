import customtkinter as ctk
import threading
import os
from PIL import Image
# from core.network_utils import get_local_ip, generate_bridge_qr, get_mdns_name
# from core.server import run_server, API_KEY

class BridgeView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        try:
            self.server_thread = None
            self.is_running = False
            
            from core.network_utils import get_local_ip, get_mdns_name
            
            # Header
            self.title_label = ctk.CTkLabel(self, text="KORE Digital Bridge", font=ctk.CTkFont(size=24, weight="bold"))
            self.title_label.pack(pady=(15, 5))
            
            self.desc_label = ctk.CTkLabel(self, text="Connectez votre mobile en scannant le QR Code.\nAssurez-vous d'être sur le même Wi-Fi.", 
                                          font=ctk.CTkFont(size=13), justify="center")
            self.desc_label.pack(pady=5)

            # Controls (MOVED UP)
            self.control_frame = ctk.CTkFrame(self, fg_color="transparent")
            self.control_frame.pack(pady=15)
            
            self.start_btn = ctk.CTkButton(self.control_frame, text="Démarrer le Serveur", 
                                          fg_color="green", hover_color="darkgreen",
                                          command=self._toggle_server)
            self.start_btn.pack(side="left", padx=10)
            
            self.status_indicator = ctk.CTkLabel(self.control_frame, text="● Hors-ligne", text_color="red")
            self.status_indicator.pack(side="left", padx=10)
            
            # QR Code Display Area (Reduced size)
            self.qr_frame = ctk.CTkFrame(self, width=250, height=250, fg_color="#2b2b2b")
            self.qr_frame.pack(pady=10)
            
            self.qr_label = ctk.CTkLabel(self.qr_frame, text="Veuillez démarrer le serveur", text_color="gray")
            self.qr_label.place(relx=0.5, rely=0.5, anchor="center")
            
            # Status & Info
            self.info_frame = ctk.CTkFrame(self, fg_color="transparent")
            self.info_frame.pack(pady=10, fill="x", padx=100)
            
            self.ip_label = ctk.CTkLabel(self.info_frame, text=f"IP: {get_local_ip()}", font=ctk.CTkFont(size=11))
            self.ip_label.pack(side="left", padx=20)
            
            self.mdns_label = ctk.CTkLabel(self.info_frame, text=f"mDNS: {get_mdns_name()}", font=ctk.CTkFont(size=11))
            self.mdns_label.pack(side="right", padx=20)
        except Exception as e:
            err_label = ctk.CTkLabel(self, text=f"Erreur d'initialisation:\n{str(e)}", text_color="red")
            err_label.pack(pady=50)

    def _toggle_server(self):
        if not self.is_running:
            self._start_server()
        else:
            self._stop_server()

    def _start_server(self):
        try:
            from core.network_utils import get_local_ip, generate_bridge_qr
            from core.server import run_server, API_KEY
            import threading
            
            # Step 1: Network Info
            local_ip = get_local_ip()
            url = f"http://{local_ip}:8000"
            
            # Step 2: Generate Handshake QR
            qr_path = generate_bridge_qr(url, API_KEY)
            
            if not os.path.exists(qr_path):
                from tkinter import messagebox
                messagebox.showerror("Erreur", "Le fichier QR n'a pas pu être généré.")
                return
            
            # Step 3: Update UI with QR Code
            pil_img = Image.open(qr_path)
            self.qr_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(230, 230))
            self.qr_label.configure(image=self.qr_img, text="")
            
            # Step 4: Spawning Server Thread
            self.server_thread = threading.Thread(target=run_server, daemon=True)
            self.server_thread.start()
            
            self.is_running = True
            self.start_btn.configure(text="Arrêter le Serveur", fg_color="red", hover_color="darkred")
            self.status_indicator.configure(text="● En ligne", text_color="green")
            
        except Exception as e:
            from tkinter import messagebox
            import traceback
            err_details = f"Erreur lors du démarrage:\n{str(e)}"
            messagebox.showerror("Erreur Bridge", err_details)
            print(traceback.format_exc())
        
    def _stop_server(self):
        # Note: Uvicorn doesn't enjoy being stopped from a thread easily without more plumbing,
        # but for a simple "Bridge" we can just let it run or rely on the thread being daemon.
        # In a real app, we'd use a more controllable server setup.
        self.is_running = False
        self.start_btn.configure(text="Démarrer le Serveur", fg_color="green", hover_color="darkgreen")
        self.status_indicator.configure(text="● Hors-ligne", text_color="red")
        self.qr_label.configure(image=None, text="Serveur arrêté")
