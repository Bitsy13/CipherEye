import os
import re
import tempfile
import subprocess
from flask import Flask, render_template, request

app = Flask(__name__)

SECRET_PATTERNS = {
    "AWS Access Key ID": r"AKIA[0-9A-Z]{16}",
    "GitHub Personal Access Token": r"ghp_[a-zA-Z0-9]{36}",
    "Hardcoded Password Assignment": r"password\s*=\s*['\"].+?['\"]",
    "Private Key Header": r"-----BEGIN PRIVATE KEY-----",
    "GitHub Repository Link": r"https?://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+"
}

def scan_file(file_path, display_name):
    file_leaks = []
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for line_num, line in enumerate(f, 1):
                for secret_name, pattern in SECRET_PATTERNS.items():
                    if re.search(pattern, line):
                        file_leaks.append({
                            "secret_type": secret_name,
                            "file": display_name,
                            "line_number": line_num,
                            "content": line.strip()
                        })
    except Exception as e:
        pass
    return file_leaks

def scan_directory(target_dir):
    all_leaks = []
    files_scanned = 0
    for root, dirs, files in os.walk(target_dir):
        if '.git' in root or 'node_modules' in root or '__pycache__' in root:
            continue
        for file in files:
            if file.endswith(('.py', '.js', '.json', '.txt', '.env', '.yml', '.yaml')):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, target_dir)
                files_scanned += 1
                all_leaks.extend(scan_file(full_path, rel_path))
    return files_scanned, all_leaks

@app.route("/", methods=["GET", "POST"])
def index():
    results = None
    scanned_target = None
    
    if request.method == "POST":
        github_url = request.form.get("github_url").strip()
        uploaded_files = request.files.getlist("files")
        
        # Option A: User submitted a GitHub URL
        if github_url:
            scanned_target = github_url
            temp_dir = tempfile.mkdtemp()
            try:
                subprocess.run(["git", "clone", github_url, temp_dir], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                files_count, leaks = scan_directory(temp_dir)
                results = {"files_scanned": files_count, "leaks": leaks}
            except Exception as e:
                results = {"error": "Failed to clone repository. Check the URL or ensure Git is installed."}
                
        # Option B: User uploaded files directly
        elif uploaded_files and uploaded_files[0].filename != '':
            scanned_target = "Uploaded Files"
            temp_dir = tempfile.mkdtemp()
            files_count = 0
            all_leaks = []
            
            for uploaded_file in uploaded_files:
                file_path = os.path.join(temp_dir, uploaded_file.filename)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                uploaded_file.save(file_path)
                files_count += 1
                all_leaks.extend(scan_file(file_path, uploaded_file.filename))
                
            results = {"files_scanned": files_count, "leaks": all_leaks}
            
    return render_template("index.html", results=results, target=scanned_target)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    