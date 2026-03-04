import os
import sqlite3
import shutil
from datetime import datetime

class BackupManager:
    def __init__(self, db_path="kore.db"):
        from database.db_manager import DBManager
        self.db = DBManager(db_path)
        self.project_root = os.path.dirname(os.path.dirname(__file__))
        self.db_path = os.path.join(self.project_root, db_path)
        
        # Load persistent backup folder or use default
        default_backup = os.path.join(self.project_root, "backups")
        self.backup_folder = self.db.get_setting("backup_folder", default_backup)
        
        if not os.path.exists(self.backup_folder):
            try:
                os.makedirs(self.backup_folder)
            except:
                # If the persistent path is invalid/inaccessible, fallback to default
                self.backup_folder = default_backup
                if not os.path.exists(self.backup_folder):
                    os.makedirs(self.backup_folder)

    def set_backup_folder(self, new_path):
        """Allows setting a cloud-synced folder like Google Drive/Dropbox."""
        if os.path.exists(new_path) and os.path.isdir(new_path):
            self.backup_folder = new_path
            self.db.set_setting("backup_folder", new_path)
            return True
        return False

    def create_backup(self):
        """Creates a timestamped copy of the database."""
        if not os.path.exists(self.db_path):
            return {"status": "error", "message": "Base de données introuvable."}
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"kore_backup_{timestamp}.db"
        
        try:
            # Safer way to backup SQLite is to use the backup mechanism,
            # but simple file copy works if connection is closed or in read-only.
            # We'll use the sqlite3 backup API for safety.
            dest_path = os.path.join(self.backup_folder, backup_filename)
            
            source_conn = sqlite3.connect(self.db_path)
            dest_conn = sqlite3.connect(dest_path)
            
            with source_conn, dest_conn:
                source_conn.backup(dest_conn)
                
            dest_conn.close()
            source_conn.close()
            
            return {"status": "success", "message": f"Backup créé: {dest_path}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def list_backups(self):
        """Returns a list of available backups."""
        backups = []
        if os.path.exists(self.backup_folder):
            for file in os.listdir(self.backup_folder):
                if file.endswith(".db") and "kore_backup" in file:
                    backups.append(os.path.join(self.backup_folder, file))
        return sorted(backups, reverse=True)
