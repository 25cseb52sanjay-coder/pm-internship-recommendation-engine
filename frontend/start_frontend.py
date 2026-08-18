import os
import sys
import subprocess

frontend_dir = os.path.dirname(os.path.abspath(__file__))
NODE_BIN_DIR = r"C:\Users\91733\.gemini\antigravity\scratch\node_bin\node-v20.18.0-win-x64"
NODE_EXE = os.path.join(NODE_BIN_DIR, "node.exe")
NEXT_BIN = os.path.join(frontend_dir, "node_modules", "next", "dist", "bin", "next")

os.environ["PATH"] = NODE_BIN_DIR + ";" + os.environ.get("PATH", "")

print("Starting Next.js Frontend Server on http://localhost:3000 ...")
cmd = [NODE_EXE, NEXT_BIN, "dev", "-p", "3000"]
subprocess.run(cmd, cwd=frontend_dir, env=os.environ)
