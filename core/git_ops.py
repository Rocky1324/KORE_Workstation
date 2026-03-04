import subprocess
import os

class GitOps:
    def __init__(self, repo_path="."):
        self.repo_path = repo_path

    def is_git_repo(self):
        """Checks if the path is a git repository."""
        return os.path.exists(os.path.join(self.repo_path, ".git"))

    def get_last_commit(self):
        """Returns the hash and message of the last commit."""
        try:
            if not self.is_git_repo():
                return {"success": False, "error": "Pas un dépôt Git."}

            # Get hash and message
            cmd = ["git", "log", "-1", "--format=%h - %s"]
            result = subprocess.check_output(cmd, cwd=self.repo_path, stderr=subprocess.STDOUT, text=True)
            return {"success": True, "commit": result.strip()}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_status(self):
        """Returns a brief status (branch and changes)."""
        try:
            if not self.is_git_repo():
                return {"success": False, "error": "Pas un dépôt Git."}
            
            branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=self.repo_path, text=True).strip()
            changes = subprocess.check_output(["git", "status", "--short"], cwd=self.repo_path, text=True).strip()
            
            status_desc = f"Branch: {branch}"
            if changes:
                status_desc += " (+ modifs)"
            else:
                status_desc += " (Clean)"
                
            return {"success": True, "status": status_desc}
        except Exception as e:
            return {"success": False, "error": str(e)}
