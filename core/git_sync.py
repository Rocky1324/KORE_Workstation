import subprocess
import os

class GitSyncManager:
    """Handles Git synchronization for the database (kore.db)."""
    
    def __init__(self, db_path="kore.db"):
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.db_path = os.path.join(self.project_root, db_path)
        
    def _run_git(self, args):
        """Helper to run git commands in the project root."""
        try:
            # CREATE_NO_WINDOW = 0x08000000. Prevents console flash on Windows.
            creation_flags = 0x08000000 if os.name == 'nt' else 0
            result = subprocess.run(
                ["git"] + args,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=False,
                creationflags=creation_flags
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "code": result.returncode
            }
        except FileNotFoundError:
            return {"success": False, "stderr": "Git n'est pas installé sur ce système.", "code": -1}

    def initialize_repo(self, remote_url=None):
        """Initializes a git repo in the project root if it doesn't exist."""
        if not os.path.exists(os.path.join(self.project_root, ".git")):
            res = self._run_git(["init"])
            if not res["success"]: return res
            
            # Create a .gitignore if it doesn't exist
            gitignore_path = os.path.join(self.project_root, ".gitignore")
            if not os.path.exists(gitignore_path):
                with open(gitignore_path, "w") as f:
                    f.write("__pycache__/\n*.pyc\nbackups/\nexports/\ndocs/\n.venv/\n.env\n")
        
        if remote_url:
            # Check if 'origin' exists
            check_origin = self._run_git(["remote", "get-url", "origin"])
            if check_origin["success"]:
                # Update existing
                self._run_git(["remote", "set-url", "origin", remote_url])
            else:
                # Add new
                self._run_git(["remote", "add", "origin", remote_url])
        
        return {"success": True, "message": "Repo Git initialisé."}

    def sync(self, message="Update database sync"):
        """Performs a Pull -> Add -> Commit -> Push cycle."""
        # 1. Pull changes
        pull_res = self._run_git(["pull", "origin", "main", "--rebase"])
        # If pull fails (maybe first time or conflict), we continue carefully
        
        # 2. Add database
        # We might want to use git-lfs for binary files, but for small SQLite it's okay
        add_res = self._run_git(["add", "kore.db"])
        if not add_res["success"]: return add_res
        
        # 3. Commit
        commit_res = self._run_git(["commit", "-m", message])
        # If nothing to commit, commit_res.success will be False, but that's okay
        
        # 4. Push
        push_res = self._run_git(["push", "origin", "main"])
        if not push_res["success"]:
            # If push fails, maybe we need to pull again
            return {"success": False, "stderr": f"Erreur Push: {push_res['stderr']}", "stdout": push_res["stdout"]}
            
        return {"success": True, "message": "Synchronisation réussie !"}

    def get_status(self):
        """Checks if there are uncommitted changes in the DB."""
        res = self._run_git(["status", "--short", "kore.db"])
        if res["success"]:
            return "Modifié" if res["stdout"].strip() else "Synchronisé"
        return "Inconnu"
