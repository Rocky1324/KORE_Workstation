import socket
import os
# from PIL import ImageTk, Image

def get_local_ip():
    """Returns the local IP address of the machine."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def generate_bridge_qr(url, api_key):
    """Generates a QR Code image for the Digital Bridge handshake."""
    import qrcode
    from PIL import Image
    data = f"{url}|{api_key}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save temporary file for UI display
    temp_path = os.path.join(os.getcwd(), "temp", "bridge_qr.png")
    if not os.path.exists(os.path.dirname(temp_path)):
        os.makedirs(os.path.dirname(temp_path))
    
    img.save(temp_path)
    return temp_path

def get_mdns_name():
    """Returns the suggested mDNS name."""
    return "kore-workstation.local"
