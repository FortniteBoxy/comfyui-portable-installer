"""
Installation Tab for ComfyUI Module Installer
"""
import tkinter as tk
from tkinter import ttk
from pathlib import Path
import threading

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import (
    DEFAULT_HOST, DEFAULT_PORT, VRAM_MODES,
    VRAM_DESCRIPTIONS, EXTRA_FLAGS
)

from core.comfy_installer import ComfyInstaller
from core.venv_manager import VenvManager
from core.server_manager import ServerManager
from ui.widgets import (
    ProgressFrame, LogFrame, StatusIndicator,
    ButtonBar, LabeledEntry, LabeledCombobox
)


class InstallTab(ttk.Frame):
    """Installation and server control tab."""

    def __init__(self, parent, main_window):
        super().__init__(parent, padding=10)
        self.main_window = main_window

        # Initialize managers
        self.venv_manager = VenvManager()
        self.installer = ComfyInstaller(venv_manager=self.venv_manager)
        self.server_manager = ServerManager()

        self._setup_ui()
        self._refresh_status()
        self._show_first_launch_hint()

    def _setup_ui(self):
        # Split into left and right panels
        left_panel = ttk.Frame(self)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        right_panel = ttk.Frame(self)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # === LEFT PANEL: Installation ===
        install_frame = ttk.LabelFrame(left_panel, text="Installation", padding=10)
        install_frame.pack(fill=tk.X, pady=(0, 10))

        # Status indicators
        status_frame = ttk.Frame(install_frame)
        status_frame.pack(fill=tk.X, pady=(0, 5))

        self.venv_status = StatusIndicator(status_frame, "Python Environment")
        self.venv_status.pack(anchor=tk.W, pady=2)

        self.comfyui_status = StatusIndicator(status_frame, "ComfyUI")
        self.comfyui_status.pack(anchor=tk.W, pady=2)

        # Install info text
        info_text = (
            "Full Install will: set up the Python environment, install PyTorch "
            "with CUDA support, clone ComfyUI from GitHub, install all "
            "dependencies, and create model directories."
        )
        info_label = ttk.Label(
            install_frame, text=info_text,
            wraplength=350, foreground="#555555",
            font=("Segoe UI", 8)
        )
        info_label.pack(fill=tk.X, pady=(0, 5))

        # Install buttons
        install_buttons = ButtonBar(install_frame)
        install_buttons.pack(fill=tk.X, pady=5)

        install_buttons.add_button(
            "full_install", "Full Install",
            self._full_install, width=15
        )
        install_buttons.add_button(
            "update", "Update ComfyUI",
            self._update_comfyui, width=15
        )
        install_buttons.add_button(
            "sage", "Install SageAttention",
            self._install_sage_attention, width=20
        )
        install_buttons.add_button(
            "purge", "Purge ComfyUI",
            self._purge_comfyui, width=15
        )
        install_buttons.add_button(
            "refresh", "Refresh",
            self._refresh_status, width=10
        )

        # Progress
        self.install_progress = ProgressFrame(install_frame)
        self.install_progress.pack(fill=tk.X, pady=5)

        # === LEFT PANEL: Server Control ===
        server_frame = ttk.LabelFrame(left_panel, text="Server Control", padding=10)
        server_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Server settings
        settings_frame = ttk.Frame(server_frame)
        settings_frame.pack(fill=tk.X, pady=(0, 5))

        # Host and port
        host_port_frame = ttk.Frame(settings_frame)
        host_port_frame.pack(fill=tk.X, pady=2)

        self.host_entry = LabeledEntry(host_port_frame, "Host:", DEFAULT_HOST)
        self.host_entry.pack(side=tk.LEFT, padx=(0, 10))

        self.port_entry = LabeledEntry(host_port_frame, "Port:", str(DEFAULT_PORT))
        self.port_entry.pack(side=tk.LEFT)

        host_port_help = ttk.Label(
            settings_frame,
            text="Default 127.0.0.1:8188 = local only. Use 0.0.0.0 to allow access from other devices on your network.",
            wraplength=350, foreground="#888888",
            font=("Segoe UI", 7)
        )
        host_port_help.pack(fill=tk.X, pady=(0, 2))

        # VRAM mode with description
        vram_section = ttk.Frame(settings_frame)
        vram_section.pack(fill=tk.X, pady=2)

        self.vram_combo = LabeledCombobox(
            vram_section, "VRAM Mode:",
            list(VRAM_MODES.keys()), "normal"
        )
        self.vram_combo.pack(side=tk.LEFT)
        self.vram_combo.combo.bind("<<ComboboxSelected>>", self._on_vram_change)

        self.vram_desc_label = ttk.Label(
            settings_frame,
            text=VRAM_DESCRIPTIONS.get("normal", ""),
            wraplength=350, foreground="#555555",
            font=("Segoe UI", 8)
        )
        self.vram_desc_label.pack(fill=tk.X, pady=(2, 5))

        # Extra startup flags
        flags_frame = ttk.LabelFrame(settings_frame, text="Startup Options", padding=5)
        flags_frame.pack(fill=tk.X, pady=(5, 5))

        self.flag_vars = {}
        self.flag_checkbuttons = {}
        for flag_id, flag_info in EXTRA_FLAGS.items():
            var = tk.BooleanVar(value=False)
            self.flag_vars[flag_id] = var
            cb = ttk.Checkbutton(
                flags_frame, text=flag_info["label"],
                variable=var
            )
            cb.pack(anchor=tk.W, pady=1)
            self.flag_checkbuttons[flag_id] = cb
            # Add tooltip-style description
            desc_label = ttk.Label(
                flags_frame,
                text=flag_info["description"],
                wraplength=330, foreground="#777777",
                font=("Segoe UI", 7)
            )
            desc_label.pack(anchor=tk.W, padx=(20, 0), pady=(0, 3))

        # Server buttons
        self.server_buttons = ButtonBar(server_frame)
        self.server_buttons.pack(fill=tk.X, pady=5)

        self.server_buttons.add_button(
            "start", "Start Server",
            self._start_server, width=15
        )
        self.server_buttons.add_button(
            "stop", "Stop Server",
            self._stop_server, width=15
        )
        self.server_buttons.disable("stop")

        self.server_buttons.add_button(
            "open_ui", "Open in Browser",
            self._open_browser, width=15
        )

        # Server status
        self.server_indicator = StatusIndicator(server_frame, "Server Status")
        self.server_indicator.pack(anchor=tk.W, pady=5)
        self.server_indicator.set_status("pending")

        # === RIGHT PANEL: Log ===
        log_frame = ttk.LabelFrame(right_panel, text="Log", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.log = LogFrame(log_frame, height=20)
        self.log.pack(fill=tk.BOTH, expand=True)

        # Log controls
        log_buttons = ttk.Frame(log_frame)
        log_buttons.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(log_buttons, text="Clear Log", command=self.log.clear).pack(side=tk.RIGHT)

    def _on_vram_change(self, event=None):
        """Update VRAM description when mode changes."""
        mode = self.vram_combo.get()
        desc = VRAM_DESCRIPTIONS.get(mode, "")
        self.vram_desc_label.config(text=desc)

    def _get_extra_args(self):
        """Build extra args list from checked startup flags."""
        args = []
        for flag_id, var in self.flag_vars.items():
            if var.get():
                flag_str = EXTRA_FLAGS[flag_id]["flag"]
                args.extend(flag_str.split())
        return args

    def _refresh_status(self):
        """Refresh installation status indicators."""
        status = self.installer.check_installation()

        self.venv_status.set_status("ok" if status["venv_created"] else "pending")
        self.comfyui_status.set_status("ok" if status["comfyui_installed"] else "pending")

        # Update server status
        if self.server_manager.is_running:
            self.server_indicator.set_status("running")
            self.server_buttons.disable("start")
            self.server_buttons.enable("stop")
            self.main_window.set_server_status(True, self.server_manager.server_url)
        else:
            self.server_indicator.set_status("pending")
            self.server_buttons.enable("start")
            self.server_buttons.disable("stop")
            self.main_window.set_server_status(False)

        # Update SageAttention checkbox label based on install status
        sa_installed = self.venv_manager.is_package_installed("sageattention")
        sa_label = "SageAttention (installed)" if sa_installed else "SageAttention (not installed)"
        self.flag_checkbuttons["sage_attention"].config(text=sa_label)

        self.log.log(f"Status: Python={'ready' if status['venv_created'] else 'not set up'}, "
                    f"ComfyUI={'installed' if status['comfyui_installed'] else 'not installed'}")

    def _full_install(self):
        """Perform full installation."""
        self.log.log("Starting full installation...")
        self.log.log("  Step 1: Set up Python environment")
        self.log.log("  Step 2: Install PyTorch with CUDA")
        self.log.log("  Step 3: Clone ComfyUI from GitHub")
        self.log.log("  Step 4: Install ComfyUI dependencies")
        self.log.log("  Step 5: Create model directories")
        self.main_window.set_status("Installing...")

        def progress_callback(current, total, message):
            if self.winfo_exists():
                self.after(0, lambda: self._update_progress(current, total, message))

        def do_install():
            return self.installer.full_install(progress_callback)

        def on_complete(success):
            if success:
                self.log.log("Installation completed successfully!")
                self.log.log("Next steps: Go to the Models tab to download models,")
                self.log.log("then click 'Start Server' to launch ComfyUI.")
                self.main_window.set_status("Installation complete")
            else:
                self.log.log("Installation failed! Check the log for details.")
                self.main_window.set_status("Installation failed")
            self._refresh_status()

        self.main_window.run_async(do_install, on_complete)

    def _install_sage_attention(self):
        """Install Triton + SageAttention."""
        if not self.venv_manager.is_created:
            self.log.log("Python environment not set up. Run Full Install first.")
            return

        if self.venv_manager.is_package_installed("sageattention"):
            from tkinter import messagebox
            if not messagebox.askyesno(
                "Already Installed",
                "SageAttention is already installed.\n\nReinstall?"
            ):
                return

        self.log.log("Installing Triton + SageAttention...")
        self.log.log("  This enables 2-3x faster attention operations,")
        self.log.log("  especially useful for video generation workflows.")
        self.main_window.set_status("Installing SageAttention...")

        def progress_callback(current, total, message):
            if self.winfo_exists():
                self.after(0, lambda: self._update_progress(current, total, message))

        def do_install():
            return self.venv_manager.install_sage_attention(progress_callback)

        def on_complete(success):
            if success:
                self.log.log("SageAttention installed! Enable the checkbox below to use it.")
                self.main_window.set_status("SageAttention installed")
            else:
                self.log.log("SageAttention installation failed. Check the log for details.")
                self.main_window.set_status("SageAttention install failed")
            self._refresh_status()

        self.main_window.run_async(do_install, on_complete)

    def _update_comfyui(self):
        """Update ComfyUI."""
        if not self.installer.is_installed:
            self.log.log("ComfyUI not installed. Use Full Install first.")
            return

        self.log.log("Updating ComfyUI (pulling latest from GitHub)...")
        self.main_window.set_status("Updating...")

        def progress_callback(current, total, message):
            if self.winfo_exists():
                self.after(0, lambda: self._update_progress(current, total, message))

        def do_update():
            return self.installer.update_comfyui(progress_callback)

        def on_complete(success):
            if success:
                self.log.log("Update completed!")
                self.main_window.set_status("Update complete")
            else:
                self.log.log("Update failed!")
                self.main_window.set_status("Update failed")

        self.main_window.run_async(do_update, on_complete)

    def _purge_comfyui(self):
        """Purge ComfyUI installation (keeps Python env and models)."""
        from tkinter import messagebox

        if not self.installer.is_installed:
            self.log.log("ComfyUI not installed. Nothing to purge.")
            return

        # Stop server first if running
        if self.server_manager.is_running:
            if not messagebox.askyesno(
                "Server Running",
                "ComfyUI server is running. Stop it and purge?"
            ):
                return
            self._stop_server()
            import time
            time.sleep(2)  # Wait for server to stop

        # Confirm purge
        if not messagebox.askyesno(
            "Confirm Purge",
            "This will DELETE the ComfyUI installation.\n\n"
            "KEPT: Python environment\n"
            "BACKED UP: Downloaded models (auto-restored on reinstall)\n"
            "DELETED: ComfyUI repo, Custom nodes\n\n"
            "You can run 'Full Install' again after purging.\n\n"
            "Continue?"
        ):
            return

        self.log.log("Purging ComfyUI installation...")
        self.main_window.set_status("Purging...")

        def progress_callback(current, total, message):
            if self.winfo_exists():
                self.after(0, lambda: self._update_progress(current, total, message))

        def do_purge():
            return self.installer.purge_comfyui(progress_callback)

        def on_complete(success):
            if success:
                self.log.log("Purge completed! Use 'Full Install' for fresh installation.")
                self.main_window.set_status("Purge complete")
            else:
                self.log.log("Purge failed!")
                self.main_window.set_status("Purge failed")
            self._refresh_status()

        self.main_window.run_async(do_purge, on_complete)

    def _update_progress(self, current, total, message):
        """Update progress from main thread."""
        self.install_progress.update_progress(current, total, message)
        self.log.log(message)

    def _start_server(self):
        """Start ComfyUI server."""
        if not self.installer.is_installed:
            self.log.log("ComfyUI not installed! Run Full Install first.")
            return

        host = self.host_entry.get()
        port = int(self.port_entry.get())
        vram_mode = self.vram_combo.get()
        extra_args = self._get_extra_args()

        flag_desc = f", flags: {' '.join(extra_args)}" if extra_args else ""
        self.log.log(f"Starting server on {host}:{port} (VRAM: {vram_mode}{flag_desc})...")
        self.server_indicator.set_status("warning")  # Starting

        def log_callback(line):
            if self.winfo_exists():
                self.after(0, lambda: self.log.log(line))

        def progress_callback(current, total, message):
            if self.winfo_exists():
                self.after(0, lambda: self.log.log(message))

        def do_start():
            return self.server_manager.start_server(
                host=host,
                port=port,
                vram_mode=vram_mode,
                extra_args=extra_args if extra_args else None,
                progress_callback=progress_callback,
                log_callback=log_callback
            )

        def on_complete(success):
            if success:
                self.log.log(f"Server running at {self.server_manager.server_url}")
                self.log.log("Click 'Open in Browser' or visit the URL to use ComfyUI.")
                self.server_indicator.set_status("running")
                self.server_buttons.disable("start")
                self.server_buttons.enable("stop")
                self.main_window.set_server_status(True, self.server_manager.server_url)
                self.main_window.set_status("Server running")
            else:
                self.log.log("Failed to start server! Check the log for errors.")
                self.server_indicator.set_status("error")
                self.main_window.set_status("Server start failed")

        self.main_window.run_async(do_start, on_complete)

    def _stop_server(self):
        """Stop ComfyUI server."""
        self.log.log("Stopping server...")

        def progress_callback(current, total, message):
            if self.winfo_exists():
                self.after(0, lambda: self.log.log(message))

        def do_stop():
            return self.server_manager.stop_server(progress_callback)

        def on_complete(success):
            if success:
                self.log.log("Server stopped")
                self.server_indicator.set_status("pending")
                self.server_buttons.enable("start")
                self.server_buttons.disable("stop")
                self.main_window.set_server_status(False)
                self.main_window.set_status("Server stopped")
            else:
                self.log.log("Failed to stop server!")

        self.main_window.run_async(do_stop, on_complete)

    def _open_browser(self):
        """Open ComfyUI in browser."""
        import webbrowser
        url = self.server_manager.server_url
        self.log.log(f"Opening {url} in browser...")
        webbrowser.open(url)

    def _show_first_launch_hint(self):
        """Show helpful guidance on first launch when nothing is installed."""
        status = self.installer.check_installation()
        if status["comfyui_installed"]:
            return  # Not a first launch

        self.log.log("=" * 50)
        self.log.log("  Welcome to ComfyUI Module!")
        self.log.log("=" * 50)
        self.log.log("")
        if not status["venv_created"]:
            self.log.log("Getting started:")
            self.log.log("  1. Click 'Full Install' to set up everything.")
            self.log.log("     This will download ComfyUI, PyTorch, and")
            self.log.log("     all dependencies (~5-15 min).")
            self.log.log("")
            self.log.log("  2. After install, go to the Models tab to")
            self.log.log("     download AI models (required to generate).")
            self.log.log("")
            self.log.log("  3. Then click 'Start Server' and 'Open in")
            self.log.log("     Browser' to use ComfyUI.")
        else:
            self.log.log("Python environment is ready.")
            self.log.log("Click 'Full Install' to download and set up ComfyUI.")
        self.log.log("")
        self.log.log("Tip: Check Help > Getting Started for a full guide.")
        self.log.log("     Check Help > VRAM Guide to pick the right models")
        self.log.log("     for your GPU.")
