import os
import shutil
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, scrolledtext


APP_NAME = "TransVideo"


def app_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[1]


ROOT = app_root()
UV = ROOT / "bin" / "uv.exe"
VENV = ROOT / ".venv"
INSTALL_MARKER = ROOT / ".transvideo-installing"
CREATE_NO_WINDOW = 0x08000000 if sys.platform == "win32" else 0


class Launcher(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("760x500")
        self.resizable(False, False)
        self.configure(bg="#17202A")
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.current_proc = None
        self.installing = False

        tk.Label(
            self,
            text="TransVideo",
            font=("Segoe UI", 22, "bold"),
            fg="#FFFFFF",
            bg="#17202A",
        ).pack(anchor="w", padx=24, pady=(22, 4))

        tk.Label(
            self,
            text="Lần đầu mở app sẽ tải runtime GPU/CPU và thư viện cần thiết. Quá trình này chỉ cần làm một lần và không cần mở CMD.",
            font=("Segoe UI", 10),
            fg="#B8C7D4",
            bg="#17202A",
            wraplength=700,
            justify="left",
        ).pack(anchor="w", padx=24)

        self.log = scrolledtext.ScrolledText(
            self,
            height=14,
            bg="#0F151B",
            fg="#D8E2EA",
            insertbackground="#D8E2EA",
            relief="flat",
            font=("Consolas", 9),
        )
        self.log.pack(fill="both", expand=True, padx=24, pady=18)

        row = tk.Frame(self, bg="#17202A")
        row.pack(fill="x", padx=24, pady=(0, 18))
        self.install_btn = tk.Button(row, text="Tải runtime và mở app", command=self.install_and_run, width=24)
        self.install_btn.pack(side="left")
        self.run_btn = tk.Button(row, text="Mở app", command=self.run_app, width=12)
        self.run_btn.pack(side="left", padx=10)
        self.clean_btn = tk.Button(row, text="Dọn cài lỗi", command=self.clean_partial_install, width=12)
        self.clean_btn.pack(side="left")
        tk.Button(row, text="Thoát", command=self.on_close, width=10).pack(side="right")

        self.after(300, self.auto_start)

    def write(self, text: str):
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.update_idletasks()

    def write_async(self, text: str):
        self.after(0, lambda value=text: self.write(value))

    def auto_start(self):
        if INSTALL_MARKER.exists() and VENV.exists():
            self.write("Phát hiện lần tải runtime trước bị dừng giữa chừng.")
            self.write("Bấm 'Dọn cài lỗi' để xóa phần cài dang dở, sau đó tải lại.")
            return
        if VENV.exists():
            self.run_app()
            return
        self.write("Chưa có runtime. Bấm 'Tải runtime và mở app' để cài lần đầu.")
        self.write("Nếu mạng bị ngắt hoặc máy bị tắt giữa chừng, app sẽ dọn phần cài dang dở trước khi tải lại.")

    def run_cmd(self, args):
        env = os.environ.copy()
        env["PYTHONUTF8"] = "1"
        self.current_proc = subprocess.Popen(
            args,
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
            creationflags=CREATE_NO_WINDOW,
        )
        assert self.current_proc.stdout is not None
        for line in self.current_proc.stdout:
            self.write_async(line.rstrip())
        code = self.current_proc.wait()
        self.current_proc = None
        if code != 0:
            raise RuntimeError(f"Command failed with exit code {code}: {' '.join(map(str, args))}")

    def install_and_run(self):
        if not UV.exists():
            messagebox.showerror(APP_NAME, f"Không tìm thấy uv.exe tại {UV}")
            return
        if self.installing:
            return
        if not messagebox.askyesno(
            APP_NAME,
            "TransVideo sẽ tải Python runtime, PyTorch GPU/CPU, FFmpeg helpers và thư viện AI. Tiếp tục?",
        ):
            return
        self.installing = True
        self.install_btn.configure(state="disabled")
        self.run_btn.configure(state="disabled")
        self.clean_btn.configure(state="disabled")
        thread = threading.Thread(target=self._install_worker, daemon=True)
        thread.start()

    def _install_worker(self):
        try:
            self.after(0, lambda: self.write("Đang tải/cài runtime..."))
            INSTALL_MARKER.write_text("installing", encoding="utf-8")
            self.run_cmd([str(UV), "sync", "--locked"])
            if INSTALL_MARKER.exists():
                INSTALL_MARKER.unlink()
            self.after(0, lambda: self.write("Cài runtime xong. Đang mở app..."))
            self.after(0, self.run_app)
        except Exception as e:
            self.after(0, lambda err=e: self._install_failed(err))

    def _install_failed(self, err: Exception):
        self.write("Cài runtime thất bại. Đang dọn phần cài dang dở...")
        self.clean_partial_install(show_done=False)
        messagebox.showerror(APP_NAME, f"Cài runtime thất bại:\n{err}")
        self.installing = False
        self.install_btn.configure(state="normal")
        self.run_btn.configure(state="normal")
        self.clean_btn.configure(state="normal")

    def clean_partial_install(self, show_done: bool = True):
        if self.current_proc and self.current_proc.poll() is None:
            try:
                self.current_proc.terminate()
                self.current_proc.wait(timeout=10)
            except Exception:
                try:
                    self.current_proc.kill()
                except Exception:
                    pass
        self.current_proc = None
        for path in [VENV, INSTALL_MARKER, ROOT / ".uv-sync.lock"]:
            try:
                if path.is_dir():
                    shutil.rmtree(path, ignore_errors=True)
                elif path.exists():
                    path.unlink()
            except OSError:
                pass
        if show_done:
            self.write("Đã dọn phần cài runtime dang dở.")
            messagebox.showinfo(APP_NAME, "Đã dọn phần cài runtime dang dở.")

    def run_app(self):
        if not UV.exists():
            messagebox.showerror(APP_NAME, f"Không tìm thấy uv.exe tại {UV}")
            return
        if INSTALL_MARKER.exists() and not VENV.exists():
            messagebox.showwarning(APP_NAME, "Runtime cũ cài chưa xong. Hãy bấm 'Dọn cài lỗi' rồi tải lại.")
            return
        if not VENV.exists():
            messagebox.showinfo(APP_NAME, "Chưa có runtime. Hãy bấm 'Tải runtime và mở app' để cài lần đầu.")
            return
        try:
            subprocess.Popen([str(UV), "run", "sp.py"], cwd=ROOT, creationflags=CREATE_NO_WINDOW)
            self.destroy()
        except Exception as e:
            messagebox.showerror(APP_NAME, str(e))

    def on_close(self):
        if self.installing:
            if not messagebox.askyesno(APP_NAME, "Runtime đang được tải. Dừng và dọn phần cài dang dở?"):
                return
            self.clean_partial_install(show_done=False)
        self.destroy()


if __name__ == "__main__":
    Launcher().mainloop()
