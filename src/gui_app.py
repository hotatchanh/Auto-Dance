import os
import threading
import tkinter as tk
from tkinter import filedialog

from .app_conf import AppConf
from .audition_ctrl import AuditionCtrl
from .io_control import IoControl


class AuditionGui:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Auto Dance Controller")
        self.controller = None
        self.controller_thread = None

        self.config_path = tk.StringVar(value="app.conf")
        self.pid_value = tk.StringVar(value="")
        self.status_value = tk.StringVar(value="Ready")
        self.speed_value = tk.StringVar(value="-")

        self._build_ui()
        self._load_config()

    def _build_ui(self):
        config_frame = tk.LabelFrame(self.root, text="Configuration")
        config_frame.pack(fill="x", padx=10, pady=8)

        tk.Label(config_frame, text="Config file:").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        tk.Entry(config_frame, textvariable=self.config_path, width=40).grid(
            row=0, column=1, sticky="ew", padx=6, pady=4
        )
        tk.Button(config_frame, text="Browse", command=self._browse_config).grid(
            row=0, column=2, padx=6, pady=4
        )
        tk.Button(config_frame, text="Load", command=self._load_config).grid(
            row=0, column=3, padx=6, pady=4
        )

        tk.Label(config_frame, text="Audition PID:").grid(row=1, column=0, sticky="w", padx=6, pady=4)
        tk.Entry(config_frame, textvariable=self.pid_value, width=20).grid(
            row=1, column=1, sticky="w", padx=6, pady=4
        )
        tk.Button(config_frame, text="Auto Detect", command=self._auto_detect_pid).grid(
            row=1, column=2, padx=6, pady=4
        )
        tk.Button(config_frame, text="Save Config", command=self._save_config).grid(
            row=1, column=3, padx=6, pady=4
        )

        config_frame.columnconfigure(1, weight=1)

        control_frame = tk.LabelFrame(self.root, text="Control")
        control_frame.pack(fill="x", padx=10, pady=8)

        tk.Button(control_frame, text="Start", width=12, command=self._start).pack(
            side="left", padx=6, pady=6
        )
        tk.Button(control_frame, text="Stop", width=12, command=self._stop).pack(
            side="left", padx=6, pady=6
        )
        tk.Button(control_frame, text="Measure Speed", width=14, command=self._measure_speed).pack(
            side="left", padx=6, pady=6
        )
        tk.Button(control_frame, text="Speed +", width=10, command=self._increase_speed).pack(
            side="left", padx=6, pady=6
        )
        tk.Button(control_frame, text="Speed -", width=10, command=self._decrease_speed).pack(
            side="left", padx=6, pady=6
        )

        speed_frame = tk.Frame(self.root)
        speed_frame.pack(fill="x", padx=10, pady=4)
        tk.Label(speed_frame, text="Current speed:").pack(side="left")
        tk.Label(speed_frame, textvariable=self.speed_value).pack(side="left", padx=6)

        status_frame = tk.Frame(self.root)
        status_frame.pack(fill="x", padx=10, pady=6)
        tk.Label(status_frame, textvariable=self.status_value, anchor="w").pack(fill="x")

    def _browse_config(self):
        path = filedialog.askopenfilename(
            title="Select config file",
            filetypes=[("Config files", "*.conf"), ("All files", "*.*")],
        )
        if path:
            self.config_path.set(path)
            self._load_config()

    def _ensure_config_exists(self, path):
        if os.path.exists(path):
            return
        example_path = "example-app.conf"
        if os.path.exists(example_path):
            with open(example_path, "r", encoding="utf-8") as src:
                with open(path, "w", encoding="utf-8") as dest:
                    dest.write(src.read())
            self.status_value.set(f"Created {path} from example-app.conf")
            return
        raise FileNotFoundError(f"Missing config file: {path}")

    def _load_config(self):
        path = self.config_path.get().strip()
        if not path:
            self.status_value.set("Please select a config file.")
            return
        try:
            self._ensure_config_exists(path)
            conf = AppConf(path)
            conf.read()
            pid = conf.get("AuAu", "pid")
            if pid is not None:
                self.pid_value.set(str(pid))
            self.status_value.set("Config loaded.")
        except Exception as exc:
            self.status_value.set(f"Failed to load config: {exc}")

    def _save_config(self):
        path = self.config_path.get().strip()
        pid = self.pid_value.get().strip()
        if not path:
            self.status_value.set("Please select a config file.")
            return
        if not pid:
            self.status_value.set("PID is required.")
            return
        try:
            self._ensure_config_exists(path)
            conf = AppConf(path)
            conf.read()
            conf.set("AuAu", "pid", pid)
            self.status_value.set("Config saved.")
        except Exception as exc:
            self.status_value.set(f"Failed to save config: {exc}")

    def _auto_detect_pid(self):
        pid = IoControl.find_audition_pid()
        if pid:
            self.pid_value.set(str(pid))
            self.status_value.set(f"Detected Audition PID: {pid}")
        else:
            self.status_value.set("Could not detect Audition window.")

    def _start(self):
        if self.controller_thread and self.controller_thread.is_alive():
            self.status_value.set("Controller is already running.")
            return
        path = self.config_path.get().strip()
        pid_text = self.pid_value.get().strip()
        if not pid_text:
            self.status_value.set("PID is required.")
            return
        self._save_config()
        pid = int(pid_text)
        try:
            self.controller = AuditionCtrl(conf_file=path, pid_override=pid)
        except Exception as exc:
            self.status_value.set(f"Failed to start: {exc}")
            return

        self.controller_thread = threading.Thread(target=self.controller.run, daemon=True)
        self.controller_thread.start()
        self.status_value.set("Controller started.")
        self.speed_value.set(str(self.controller.speed))

    def _stop(self):
        if self.controller:
            self.controller.stop()
            self.status_value.set("Controller stopped.")
        else:
            self.status_value.set("Controller is not running.")

    def _measure_speed(self):
        if not self.controller:
            self.status_value.set("Controller is not running.")
            return
        self.controller.measure_speed()
        self.speed_value.set(str(self.controller.speed))
        self.status_value.set("Speed measured.")

    def _increase_speed(self):
        if not self.controller:
            self.status_value.set("Controller is not running.")
            return
        self.controller.increase_speed()
        self.speed_value.set(str(self.controller.speed))
        self.status_value.set("Speed increased.")

    def _decrease_speed(self):
        if not self.controller:
            self.status_value.set("Controller is not running.")
            return
        self.controller.decrease_speed()
        self.speed_value.set(str(self.controller.speed))
        self.status_value.set("Speed decreased.")

    def run(self):
        self.root.mainloop()
