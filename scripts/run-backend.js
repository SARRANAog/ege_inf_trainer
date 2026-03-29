const { spawn } = require("child_process");
const fs = require("fs");
const path = require("path");

const projectRoot = path.resolve(__dirname, "..");
const backendDir = path.join(projectRoot, "backend");

const candidatePythons = [
  path.join(backendDir, ".venv", "Scripts", "python.exe"),
  path.join(backendDir, ".venv", "bin", "python"),
  "python",
];

const pythonPath = candidatePythons.find((candidate) => candidate === "python" || fs.existsSync(candidate));

if (!pythonPath) {
  console.error("Python interpreter not found. Create backend/.venv or install python in PATH.");
  process.exit(1);
}

const args = ["-m", "uvicorn", "server:app", "--host", "127.0.0.1", "--port", "8001"];

const child = spawn(pythonPath, args, {
  cwd: backendDir,
  stdio: "inherit",
  shell: false,
});

const stopChild = () => {
  if (!child.killed) child.kill("SIGTERM");
};

process.on("SIGINT", stopChild);
process.on("SIGTERM", stopChild);

child.on("exit", (code, signal) => {
  if (signal) process.exit(0);
  process.exit(code ?? 0);
});

child.on("error", (error) => {
  console.error("Failed to start backend:", error.message);
  process.exit(1);
});
