from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
import os
import uvicorn
from database.db_manager import DBManager
from core.network_utils import get_local_ip

app = FastAPI(title="KORE Digital Bridge Server")
db = DBManager()

# Security: Persistent API Key
def get_persistent_api_key():
    key = db.get_setting("api_key")
    if not key:
        key = "KORE_" + os.urandom(8).hex()
        db.set_setting("api_key", key)
    return key

API_KEY = get_persistent_api_key()

async def verify_token(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return x_api_key

class JournalNote(BaseModel):
    title: str
    content: str

@app.get("/")
async def root():
    import os
    db_abs = os.path.abspath(db.db_path)
    db_exists = os.path.exists(db_abs)
    db_size = os.path.getsize(db_abs) if db_exists else 0
    
    return HTMLResponse(content=f"""
        <html>
            <body style='background: #0a0a0a; color: #e0e0e0; font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif; text-align: center; padding: 50px;'>
                <h1 style='color: #FFA500; font-size: 3em;'>KORE Digital Bridge</h1>
                <div style='background: #1a1a1a; padding: 30px; border-radius: 20px; border: 1px solid #333; display: inline-block; text-align: left; box-shadow: 0 10px 30px rgba(0,0,0,0.5);'>
                    <h2 style='border-bottom: 2px solid #FFA500; padding-bottom: 10px;'>Diagnostic Serveur</h2>
                    <p><b>Statut :</b> <span style='color: #39FF14;'>OPERATIONNEL</span></p>
                    <p><b>Base de Données :</b> <code style='background: #000; padding: 3px 8px; border-radius: 4px;'>{db_abs}</code></p>
                    <p><b>Taille DB :</b> {db_size / 1024:.2f} KB</p>
                    <p><b>Fichier présent :</b> {"✅ OUI" if db_exists else "❌ NON (Vérifiez le dossier !)"}</p>
                    <hr style='border: 0; border-top: 1px solid #333; margin: 20px 0;'>
                    <p><b>Code de Couplage :</b></p>
                    <div style='background: #000; padding: 15px; border-radius: 10px; font-family: monospace; font-size: 1.2em; color: #00F3FF; border: 1px dashed #555;'>
                        http://{get_local_ip()}:8000|{API_KEY}
                    </div>
                    <p style='font-size: 0.8em; color: #888; margin-top: 15px;'><i>Utilisez ce code dans l'application mobile pour synchroniser.</i></p>
                </div>
            </body>
        </html>
    """)

@app.get("/status", dependencies=[Depends(verify_token)])
async def status():
    return {"status": "online", "version": "1.1", "name": "KORE-Workstation", "db": db.db_path}

@app.get("/debug", dependencies=[Depends(verify_token)])
async def debug_info():
    import os
    return {
        "cwd": os.getcwd(),
        "db_path": db.db_path,
        "db_exists": os.path.exists(db.db_path),
        "db_size": os.path.getsize(db.db_path) if os.path.exists(db.db_path) else 0
    }

@app.get("/tasks", dependencies=[Depends(verify_token)])
async def get_tasks():
    tasks = db.get_pending_tasks(limit=50)
    return [{"id": t[0], "text": t[1], "priority": t[2], "deadline": t[3]} for t in tasks]

@app.post("/tasks/{task_id}/done", dependencies=[Depends(verify_token)])
async def mark_task_done(task_id: int):
    db.update_task_status(task_id, status='Fait')
    return {"message": "Tâche terminée"}

@app.post("/journal", dependencies=[Depends(verify_token)])
async def add_journal(note: JournalNote):
    db.add_journal_entry(note.title, note.content, "Mobile Capture")
    return {"message": "Note enregistrée"}

@app.get("/library", dependencies=[Depends(verify_token)])
async def list_library():
    lib_path = os.path.join(os.getcwd(), "kore_library")
    if not os.path.exists(lib_path):
        return []
    files = [f for f in os.listdir(lib_path) if os.path.isfile(os.path.join(lib_path, f))]
    return files

@app.get("/library/{filename}", dependencies=[Depends(verify_token)])
async def get_file(filename: str):
    lib_path = os.path.join(os.getcwd(), "kore_library")
    file_path = os.path.join(lib_path, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    # [Optimization] Streaming with FileResponse for efficiency
    return FileResponse(path=file_path, filename=filename, media_type='application/pdf')

# mDNS / ZeroConf logic
def start_mdns():
    try:
        from zeroconf import IPVersion, ServiceInfo, Zeroconf
        import socket

        desc = {'version': '1.0', 'api_key': API_KEY}
        local_ip = get_local_ip()
        
        info = ServiceInfo(
            "_kore._tcp.local.",
            "KORE-Workstation._kore._tcp.local.",
            addresses=[socket.inet_aton(local_ip)],
            port=8000,
            properties=desc,
            server="kore-workstation.local.",
        )

        zeroconf = Zeroconf(ip_version=IPVersion.V4Only)
        zeroconf.register_service(info)
        return zeroconf, info
    except Exception as e:
        print(f"mDNS failed: {e}")
        return None, None

def run_server():
    # To be called from a thread in app.py
    zc, info = start_mdns()
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    finally:
        if zc:
            zc.unregister_service(info)
            zc.close()
