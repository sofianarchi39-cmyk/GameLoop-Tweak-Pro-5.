"""GameLoop Tweak Starter

A small, reversible Windows power-plan helper and GameLoop process detector.
No game-file edits, injection, registry patches, or anti-cheat interference.
"""
from __future__ import annotations

import csv
import io
import json
import os
import platform
import re
import subprocess
import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox

WINDOWS = sys.platform == "win32"
HIGH_PERFORMANCE_GUID = "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"
GUID_RE = re.compile(r"\b[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}\b")
STATE_DIR = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "GameLoopTweakStarter"
STATE_FILE = STATE_DIR / "previous_power_plan.json"
POSSIBLE_GAMELOOP_PROCESSES = {
    "appmarket.exe", "androidemulatorex.exe", "androidemulatoren.exe",
    "androidprocess.exe", "aow_exe.exe", "tencentdl.exe",
}


def command(*args: str) -> str:
    """Run a Windows system tool safely, without a shell."""
    if not WINDOWS:
        raise RuntimeError("This application works on Windows only.")
    completed = subprocess.run(
        list(args), capture_output=True, text=True, errors="replace",
        timeout=15,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        check=False,
    )
    if completed.returncode:
        reason = (completed.stderr or completed.stdout).strip()
        raise RuntimeError(reason or f"Command exited with code {completed.returncode}.")
    return completed.stdout


def get_active_scheme() -> str:
    result = GUID_RE.search(command("powercfg", "/getactivescheme"))
    if not result:
        raise RuntimeError("Couldn't read the current Windows power plan.")
    return result.group(0).lower()


def get_available_schemes() -> set[str]:
    return {match.lower() for match in GUID_RE.findall(command("powercfg", "/list"))}


def find_gameloop_processes() -> list[str]:
    output = command("tasklist", "/fo", "csv", "/nh")
    process_names = set()
    for row in csv.reader(io.StringIO(output)):
        if row and row[0].strip().lower() in POSSIBLE_GAMELOOP_PROCESSES:
            process_names.add(row[0].strip())
    return sorted(process_names, key=str.casefold)


def read_saved_scheme() -> str | None:
    if not STATE_FILE.is_file():
        return None
    data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    saved = data.get("previous_guid", "")
    if not isinstance(saved, str) or not GUID_RE.fullmatch(saved):
        raise RuntimeError("Backup file is invalid; no changes were made.")
    return saved.lower()


def save_scheme(scheme: str) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps({"previous_guid": scheme}, indent=2), encoding="utf-8")


def total_memory_gb() -> str:
    if not WINDOWS:
        return "Windows only"
    # No external dependencies; use native Windows memory information.
    import ctypes
    from ctypes import wintypes

    class MEMORYSTATUSEX(ctypes.Structure):
        _fields_ = [
            ("dwLength", wintypes.DWORD), ("dwMemoryLoad", wintypes.DWORD),
            ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
            ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
            ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
            ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
        ]

    info = MEMORYSTATUSEX()
    info.dwLength = ctypes.sizeof(info)
    if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(info)):
        return f"{info.ullTotalPhys / (1024 ** 3):.1f} GB"
    return "Unavailable"


BG = "#101827"
CARD = "#1b293c"
FG = "#e8f0fa"
MUTED = "#a4b4c8"
BLUE = "#3e80ff"
GREEN = "#16a085"


class TweakApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.title("GameLoop Tweak Starter")
        root.geometry("570x490")
        root.minsize(550, 480)
        root.configure(background=BG)

        tk.Label(root, text="GAMELOOP TWEAK STARTER", bg=BG, fg=FG,
                 font=("Segoe UI", 18, "bold")).pack(pady=(22, 5))
        tk.Label(root, text="Windows settings only  •  Safe & reversible",
                 bg=BG, fg=MUTED, font=("Segoe UI", 10)).pack(pady=(0, 16))

        self.status = tk.StringVar(value="Press Scan to check your system")
        self.power = tk.StringVar(value="Power plan: not checked")
        self.system = tk.StringVar(value="System: not checked")
        panel = tk.Frame(root, bg=CARD, padx=18, pady=14)
        panel.pack(fill="x", padx=22)
        for value in (self.status, self.power, self.system):
            tk.Label(panel, textvariable=value, bg=CARD, fg=FG, anchor="w",
                     justify="left", wraplength=490, font=("Segoe UI", 10)).pack(fill="x", pady=5)

        button_options = dict(font=("Segoe UI", 11, "bold"), fg="white",
                              bd=0, activeforeground="white", cursor="hand2",
                              relief="flat", padx=10, pady=10)
        tk.Button(root, text="1   Scan GameLoop & PC", command=self.scan,
                  bg=BLUE, activebackground="#295ec4", **button_options).pack(fill="x", padx=22, pady=(20, 7))
        tk.Button(root, text="2   Enable High Performance", command=self.enable,
                  bg=GREEN, activebackground="#0d806b", **button_options).pack(fill="x", padx=22, pady=7)
        tk.Button(root, text="3   Restore Previous Power Plan", command=self.restore,
                  bg="#42556e", activebackground="#34475d", **button_options).pack(fill="x", padx=22, pady=7)

        tk.Label(root, text="Does not change PUBG files, boost FPS artificially, or bypass anti-cheat.",
                 bg=BG, fg=MUTED, wraplength=500,
                 font=("Segoe UI", 9)).pack(pady=(14, 0))
        self.scan()

    def scan(self) -> None:
        if not WINDOWS:
            self.status.set("GameLoop status: Windows only")
            self.power.set("Power plan: unavailable")
            self.system.set(f"Platform: {platform.system()}")
            return
        try:
            processes = find_gameloop_processes()
            self.status.set("GameLoop-related processes: " + (
                ", ".join(processes) if processes else "None detected (may be closed)"))
        except (RuntimeError, OSError, subprocess.TimeoutExpired) as exc:
            self.status.set(f"Process scan error: {exc}")
        try:
            current = get_active_scheme()
            name = "High Performance" if current == HIGH_PERFORMANCE_GUID else current
            self.power.set(f"Active Windows power plan: {name}")
        except (RuntimeError, OSError, subprocess.TimeoutExpired) as exc:
            self.power.set(f"Power plan scan error: {exc}")
        self.system.set(f"Logical CPU processors: {os.cpu_count() or 'N/A'}    |    RAM: {total_memory_gb()}")

    def enable(self) -> None:
        try:
            current = get_active_scheme()
            if current == HIGH_PERFORMANCE_GUID:
                messagebox.showinfo("Already active", "High Performance is already active.")
                return
            if HIGH_PERFORMANCE_GUID not in get_available_schemes():
                messagebox.showwarning(
                    "Plan not available",
                    "The High Performance plan isn't available on this PC.\n"
                    "Nothing was changed. Use Windows Power Options to inspect available plans.",
                )
                return
            if not messagebox.askyesno(
                "Confirm change", "Enable Windows High Performance power plan?\n\n"
                "This can increase power usage and heat on laptops."
            ):
                return
            # Preserve the original plan from the first successful activation.
            if read_saved_scheme() is None:
                save_scheme(current)
            command("powercfg", "/setactive", HIGH_PERFORMANCE_GUID)
            self.scan()
            messagebox.showinfo("Done", "High Performance is active. Use Restore to undo.")
        except (RuntimeError, OSError, subprocess.TimeoutExpired, ValueError, json.JSONDecodeError) as exc:
            messagebox.showerror("Couldn't apply", f"No further changes were made.\n\n{exc}")

    def restore(self) -> None:
        try:
            saved = read_saved_scheme()
            if saved is None:
                messagebox.showinfo("No backup", "There is no saved previous power plan.")
                return
            if saved not in get_available_schemes():
                messagebox.showwarning("Unavailable", "The original power plan is no longer available.")
                return
            if not messagebox.askyesno("Restore", "Restore the previously saved Windows power plan?"):
                return
            command("powercfg", "/setactive", saved)
            STATE_FILE.unlink(missing_ok=True)
            self.scan()
            messagebox.showinfo("Restored", "Previous power plan has been restored.")
        except (RuntimeError, OSError, subprocess.TimeoutExpired, ValueError, json.JSONDecodeError) as exc:
            messagebox.showerror("Restore failed", str(exc))


if __name__ == "__main__":
    root = tk.Tk()
    TweakApp(root)
    root.mainloop()
