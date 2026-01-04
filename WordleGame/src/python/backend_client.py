import subprocess
import threading
import queue
import time
from pathlib import Path


class GameBackend:
    def __init__(self, exe_path: str):
        self.exe_path = exe_path
        self.proc = None
        self._stdout_q = queue.Queue()
        self._stderr_q = queue.Queue()
        self._reader_threads = []

    def start_process(self):
        self.stop()
        workdir = str(Path(self.exe_path).parent)
        try:
            self.proc = subprocess.Popen(
                [self.exe_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                cwd=workdir
            )
        except Exception as e:
            print("Failed to start process:", e)
            return False

        def _reader(f, q):
            try:
                for line in f:
                    q.put(line.rstrip("\r\n"))
            except Exception:
                pass

        t_out = threading.Thread(target=_reader, args=(self.proc.stdout, self._stdout_q), daemon=True)
        t_err = threading.Thread(target=_reader, args=(self.proc.stderr, self._stderr_q), daemon=True)
        t_out.start(); t_err.start()
        self._reader_threads = [t_out, t_err]
        return True

    def _send_command(self, cmd: str, timeout: float = 2.0) -> str:
        if not self.proc or self.proc.poll() is not None:
            return "NO C++ Process"
        # sanitize command: strip, remove stray CR, and uppercase guess word
        cmd = cmd.strip().replace("\r", "")
        if cmd.upper().startswith("GUESS "):
            parts = cmd.split(" ", 1)
            guess = parts[1].strip().upper()
            cmd = f"GUESS {guess}"
        try:
            self.proc.stdin.write(cmd + "\n")
            self.proc.stdin.flush()
        except Exception as e:
            return f"FAILED WRITE: {e}"

        out_lines = []
        start = time.time()
        while time.time() - start < timeout:
            try:
                line = self._stdout_q.get_nowait()
                out_lines.append(line)
                if line.startswith(("READY", "FEEDBACK", "WIN", "INVALID", "HINT", "ERROR")):
                    # also grab stderr if any
                    while not self._stderr_q.empty():
                        out_lines.append(self._stderr_q.get_nowait())
                    return " | ".join(out_lines)
            except queue.Empty:
                time.sleep(0.01)
        # timeout: include any stderr
        stderr_lines = []
        while not self._stderr_q.empty():
            stderr_lines.append(self._stderr_q.get_nowait())
        return " | ".join(out_lines + stderr_lines) if (out_lines or stderr_lines) else "NO RESPONSE"

    def start_game(self):
        return self._send_command("START", timeout=2.5)

    def set_mode(self, mode: str):
        return self._send_command(f"MODE {mode}", timeout=1.0)

    def send_guess(self, guess: str):
        # спробуємо відправити просте слово (без префікса)
        g = guess.strip().upper()
        resp = self._send_command(g, timeout=3.0)
        if "INVALID" in resp and not g.startswith("GUESS "):
            # fallback: спробувати у форматі "GUESS <word>"
            resp = self._send_command(f"GUESS {g}", timeout=3.0)
        return resp

    def request_hint(self):
        return self._send_command("HINT", timeout=1.0)

    def stop(self):
        if self.proc:
            try:
                self.proc.kill()
            except Exception:
                pass
            self.proc = None
        with self._stdout_q.mutex:
            self._stdout_q.queue.clear()
        with self._stderr_q.mutex:
            self._stderr_q.queue.clear()
