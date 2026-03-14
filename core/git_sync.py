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
        """Performs a Pull -> Add -> Commit -> Push cycle with improved robustness."""
        # 0. Check current branch
        branch_res = self._run_git(["rev-parse", "--abbrev-ref", "HEAD"])
        branch = branch_res["stdout"].strip() if branch_res["success"] else "main"

        # 0.5 Check if remote origin exists
        check_origin = self._run_git(["remote", "get-url", "origin"])
        if not check_origin["success"]:
            return {"success": False, "stderr": "Le dépôt distant 'origin' n'est pas configuré. Utilisez '/github [URL]' d'abord.", "code": -1}

        # 1. Pull changes
        pull_res = self._run_git(["pull", "origin", branch, "--rebase"])
        if not pull_res["success"]:
            err = pull_res["stderr"].lower()
            if "conflict" in err:
                return {"success": False, "stderr": "Conflit détecté ! La version distante de la base de données diffère. Vous devez probablement forcer un push ou faire un backup manuel.", "code": -2}
            elif "could not resolve host" in err:
                return {"success": False, "stderr": "Pas de connexion internet ou serveur inaccessible.", "code": -3}
            # If pull fails for other reasons, we might still want to try pushing if we are ahead
        
        # 2. Add database
        if not os.path.exists(self.db_path):
            return {"success": False, "stderr": f"Fichier {os.path.basename(self.db_path)} introuvable.", "code": -4}
            
        add_res = self._run_git(["add", "kore.db"])
        if not add_res["success"]: return add_res
        
        # 3. Commit
        commit_res = self._run_git(["commit", "-m", message])
        # If nothing to commit, git returns returncode 1. We check the output.
        if not commit_res["success"]:
            if "nothing to commit" in commit_res["stdout"] or "rien à valider" in commit_res["stdout"]:
                # This is actually a success state (already up to date locally)
                pass
            else:
                return commit_res
        
        # 4. Push
        push_res = self._run_git(["push", "origin", branch])
        if not push_res["success"]:
            err = push_res["stderr"]
            if "rejected" in err or "non-fast-forward" in err:
                return {"success": False, "stderr": "Push rejeté : La version distante est plus récente. Tentez de synchroniser à nouveau.", "code": -5}
            elif "403" in err or "permission denied" in err:
                return {"success": False, "stderr": "Erreur d'authentification GitHub. Vérifiez vos identifiants ou votre token.", "code": -6}
            return {"success": False, "stderr": f"Erreur Push: {err}", "stdout": push_res["stdout"]}
            
        return {"success": True, "message": "Synchronisation réussie !"}

    def get_status(self):
        """Checks if there are uncommitted changes in the DB."""
        res = self._run_git(["status", "--short", "kore.db"])
        if res["success"]:
            return "Modifié" if res["stdout"].strip() else "Synchronisé"
        return "Inconnu"
