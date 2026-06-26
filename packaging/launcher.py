import os
import subprocess
import sys
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


class Launcher(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("720x430")
        self.resizable(False, False)
        self.configure(bg="#17202A")
        self.protocol("WM_DELETE_WINDOW", self.destroy)

        tk.Label(
            self,
            text="TransVideo",
            font=("Segoe UI", 22, "bold"),
            fg="#FFFFFF",
            bg="#17202A",
        ).pack(anchor="w", padx=24, pady=(22, 4))

        tk.Label(
            self,
            text="Lan dau chay se tai runtime GPU/CPU va cac thu vien can thiet. Viec nay co the rat lau, nhung chi can lam mot lan.",
            font=("Segoe UI", 10),
            fg="#B8C7D4",
            bg="#17202A",
            wraplength=660,
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
        self.install_btn = tk.Button(row, text="Tai runtime va mo app", command=self.install_and_run, width=22)
        self.install_btn.pack(side="left")
        tk.Button(row, text="Mo app", command=self.run_app, width=12).pack(side="left", padx=10)
        tk.Button(row, text="Thoat", command=self.destroy, width=10).pack(side="right")

        self.after(300, self.auto_start)

    def write(self, text: str):
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.update_idletasks()

    def auto_start(self):
        if VENV.exists():
            self.run_app()
            return
        self.write("Chua co runtime. Bam 'Tai runtime va mo app' de cai lan dau.")

    def run_cmd(self, args):
        env = os.environ.copy()
        env["PYTHONUTF8"] = "1"
        proc = subprocess.Popen(
            args,
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )
        assert proc.stdout is not None
        for line in proc.stdout:
            self.write(line.rstrip())
        code = proc.wait()
        if code != 0:
            raise RuntimeError(f"Command failed with exit code {code}: {' '.join(map(str, args))}")

    def install_and_run(self):
        if not UV.exists():
            messagebox.showerror(APP_NAME, f"Khong tim thay uv.exe tai {UV}")
            return
        if not messagebox.askyesno(
            APP_NAME,
            "TransVideo se tai Python runtime, PyTorch GPU/CPU, FFmpeg helpers va thu vien AI. Tiep tuc?",
        ):
            return
        self.install_btn.configure(state="disabled")
        try:
            self.write("Dang tai/cai runtime...")
            self.run_cmd([str(UV), "sync", "--locked"])
            self.write("Cai runtime xong.")
            self.run_app()
        except Exception as e:
            messagebox.showerror(APP_NAME, str(e))
            self.install_btn.configure(state="normal")

    def run_app(self):
        if not UV.exists():
            messagebox.showerror(APP_NAME, f"Khong tim thay uv.exe tai {UV}")
            return
        try:
            subprocess.Popen([str(UV), "run", "sp.py"], cwd=ROOT)
            self.destroy()
        except Exception as e:
            messagebox.showerror(APP_NAME, str(e))


if __name__ == "__main__":
    Launcher().mainloop()
