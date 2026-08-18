import os
import sys
import subprocess

frontend_dir = os.path.dirname(os.path.abspath(__file__))
NODE_BIN_DIR = r"C:\Users\91733\.gemini\antigravity\scratch\node_bin\node-v20.18.0-win-x64"
NPM_CMD = os.path.join(NODE_BIN_DIR, "npm.cmd")
NODE_MODULES_BIN = os.path.join(frontend_dir, "node_modules", ".bin")

os.environ["PATH"] = NODE_BIN_DIR + ";" + NODE_MODULES_BIN + ";" + os.environ.get("PATH", "")

args = sys.argv[1:] if len(sys.argv) > 1 else ["install"]

print(f"Executing: {NPM_CMD} {' '.join(args)} ...")
res = subprocess.run([NPM_CMD] + args, cwd=frontend_dir, env=os.environ, shell=True)
sys.exit(res.returncode)
