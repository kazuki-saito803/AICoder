import os
import json
import git
from langchain.tools import Tool
from langchain_core.tools import tool


# --- write_file tool 関数本体 ---
@tool
def write_file(path: str, content: str) -> str:
    """Create a file. Expects 'path' (string) and 'content' (string)."""
    try:
        if not path or not content:
            return "Error: 'path' and 'content' are required."
        
        parent_dir = os.path.dirname(path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)

        with open(path, "w") as f:
            f.write(content)
        return f"Wrote file at {path}"
    except Exception as e:
        return f"Error: {e}"

# --- make_directory tool 関数本体 ---
@tool
def make_directory(input: str) -> str:
    """Create a directory. Expects JSON string with 'path'."""
    try:
        data = json.loads(input)
        path = data.get("path")
        os.makedirs(path, exist_ok=True)
        return f"Created directory {path}"
    except Exception as e:
        return f"Error: {e}"

# --- git_init_and_push tool 関数本体 ---
@tool
def git_init_and_push(input: str) -> str:
    """Init Git and push. Expects JSON string with 'repo_url', 'commit_msg', and 'token'."""
    try:
        data = json.loads(input)
        repo_url = data.get("repo_url")
        commit_msg = data.get("commit_msg")
        token = data.get("token")
        if not all([repo_url, commit_msg, token]):
            return "Error: Missing required fields."

        repo = git.Repo.init(".")
        repo.git.add(all=True)
        repo.index.commit(commit_msg)
        remote_url = repo_url.replace("https://", f"https://{token}@")
        origin = repo.create_remote("origin", url=remote_url)
        origin.push(refspec="master:master")
        return "Pushed to GitHub"
    except Exception as e:
        return f"Error: {e}"