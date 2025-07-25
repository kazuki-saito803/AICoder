# agent/tools.py の修正

from langchain.agents import tool
import os
import json # jsonモジュールは他のツールで使う可能性があるので残しておくか、不要なら削除
import git

@tool
# 修正前: def write_file(input: str) -> str:
# 修正後: pathとcontentを直接引数として受け取る
def write_file(path: str, content: str) -> str:
    """Create a file. Expects 'path' (string) and 'content' (string)."""
    try:
        # 以前のjson.loadsの行は不要になる
        # data = json.loads(input)
        # path = data.get("path")
        # content = data.get("content")

        if not path or not content:
            # pathやcontentが空の場合のチェックは残しておく
            return "Error: 'path' and 'content' are required."
        
        # 親ディレクトリが存在しない場合に作成するロジックを追加（堅牢性向上のため、推奨）
        parent_dir = os.path.dirname(path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)

        with open(path, "w") as f:
            f.write(content)
        return f"Wrote file at {path}"
    except Exception as e:
        return f"Error: {e}"

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
        repo.git.add(A=True) # A=True は all=True に変更を推奨 (gitpythonの新しいバージョン)
        repo.index.commit(commit_msg)
        remote_url = repo_url.replace("https://", f"https://{token}@")
        origin = repo.create_remote("origin", url=remote_url)
        origin.push(refspec="master:master") # 'master' を可変にするか、'main' に変更を推奨
        return "Pushed to GitHub"
    except Exception as e:
        return f"Error: {e}"