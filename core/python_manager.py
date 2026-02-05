"""
Embedded Python Manager for ComfyUI Module

Downloads and configures Python embedded distribution for Windows.
Eliminates the need for system-installed Python.
"""
import os
import subprocess
import zipfile
from pathlib import Path
from typing import Optional, Callable

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import BASE_DIR


# Constants
PYTHON_VERSION = "3.12.8"
PYTHON_URL = f"https://www.python.org/ftp/python/{PYTHON_VERSION}/python-{PYTHON_VERSION}-embed-amd64.zip"
PYTHON_DIR_NAME = "python_embedded"


class PythonManager:
    """Manages embedded Python download, extraction, and configuration."""

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or BASE_DIR
        self.python_dir = self.base_dir / PYTHON_DIR_NAME
        self.python_exe = self.python_dir / "python.exe"
        self.site_packages = self.python_dir / "Lib" / "site-packages"

    @property
    def is_installed(self) -> bool:
        """Check if embedded Python exists and is configured."""
        return self.python_exe.exists() and self.site_packages.exists()

    @property
    def has_pip(self) -> bool:
        """Check if pip is available."""
        if not self.python_exe.exists():
            return False
        result = subprocess.run(
            [str(self.python_exe), "-m", "pip", "--version"],
            capture_output=True, text=True
        )
        return result.returncode == 0

    @property
    def pth_file(self) -> Optional[Path]:
        """Find the python3xx._pth file."""
        for f in self.python_dir.glob("python*._pth"):
            return f
        return None

    def download_and_setup(
        self,
        progress_callback: Optional[Callable] = None
    ) -> bool:
        """Download, extract, and configure embedded Python.

        Steps:
            1. Download embeddable ZIP from python.org
            2. Extract to python_embedded/
            3. Configure ._pth file for site-packages
            4. Bootstrap pip via ensurepip

        Args:
            progress_callback: Optional callback(current, total, message)

        Returns:
            True if setup completed successfully.
        """
        if self.is_installed and self.has_pip:
            if progress_callback:
                progress_callback(100, 100, "Embedded Python already installed")
            return True

        try:
            # Step 1: Download
            if not self.python_exe.exists():
                if progress_callback:
                    progress_callback(0, 100, f"Downloading Python {PYTHON_VERSION}...")

                zip_path = self.base_dir / "python_embedded.zip"
                self._download_file(PYTHON_URL, zip_path, progress_callback)

                # Step 2: Extract
                if progress_callback:
                    progress_callback(50, 100, "Extracting Python...")

                self.python_dir.mkdir(parents=True, exist_ok=True)
                with zipfile.ZipFile(zip_path, 'r') as zf:
                    zf.extractall(self.python_dir)

                zip_path.unlink(missing_ok=True)

            # Step 3: Configure ._pth
            if progress_callback:
                progress_callback(65, 100, "Configuring Python paths...")

            self._configure_pth()

            # Step 4: Create site-packages
            self.site_packages.mkdir(parents=True, exist_ok=True)

            # Step 5: Bootstrap pip
            if not self.has_pip:
                if progress_callback:
                    progress_callback(75, 100, "Bootstrapping pip...")

                self._bootstrap_pip(progress_callback)

            if progress_callback:
                progress_callback(100, 100, "Embedded Python ready")
            return True

        except Exception as e:
            if progress_callback:
                progress_callback(0, 100, f"Error setting up Python: {e}")
            return False

    def _download_file(
        self,
        url: str,
        dest: Path,
        progress_callback: Optional[Callable] = None
    ):
        """Download a file with progress reporting using urllib (no dependencies)."""
        import urllib.request
        import ssl

        ctx = ssl.create_default_context()
        req = urllib.request.Request(url, headers={
            "User-Agent": "ComfyUI-Module-Installer/1.0"
        })

        with urllib.request.urlopen(req, context=ctx) as response:
            total_size = int(response.headers.get("Content-Length", 0))
            downloaded = 0
            block_size = 65536  # 64KB chunks

            with open(dest, "wb") as f:
                while True:
                    chunk = response.read(block_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_callback and total_size > 0:
                        pct = int(downloaded / total_size * 45) + 5  # 5-50% range
                        mb = downloaded // (1024 * 1024)
                        total_mb = total_size // (1024 * 1024)
                        progress_callback(pct, 100, f"Downloading Python... {mb}/{total_mb} MB")

    def _configure_pth(self):
        """Configure the ._pth file to enable site-packages and import site."""
        pth = self.pth_file
        if pth is None:
            raise FileNotFoundError("Could not find python*._pth file in embedded Python")

        # Find the stdlib zip name (e.g., python312.zip)
        zip_name = None
        for f in self.python_dir.glob("python*.zip"):
            zip_name = f.name
            break

        if zip_name is None:
            zip_name = "python312.zip"

        lines = [
            zip_name,
            ".",
            "Lib",
            "Lib\\site-packages",
            "",
            "import site",
        ]
        pth.write_text("\n".join(lines), encoding="ascii")

    def _bootstrap_pip(self, progress_callback: Optional[Callable] = None):
        """Bootstrap pip by downloading get-pip.py.

        The embedded Python distribution does not include ensurepip,
        so we download get-pip.py from bootstrap.pypa.io.
        """
        import urllib.request
        import ssl

        get_pip_path = self.python_dir / "get-pip.py"

        if progress_callback:
            progress_callback(78, 100, "Downloading get-pip.py...")

        ctx = ssl.create_default_context()
        req = urllib.request.Request(
            "https://bootstrap.pypa.io/get-pip.py",
            headers={"User-Agent": "ComfyUI-Module-Installer/1.0"}
        )
        with urllib.request.urlopen(req, context=ctx) as response:
            get_pip_path.write_bytes(response.read())

        if progress_callback:
            progress_callback(82, 100, "Installing pip...")

        result = subprocess.run(
            [str(self.python_exe), str(get_pip_path)],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            raise RuntimeError(f"get-pip.py failed: {result.stderr}")

        # Clean up get-pip.py
        get_pip_path.unlink(missing_ok=True)

        if progress_callback:
            progress_callback(88, 100, "Upgrading pip...")

        # Upgrade pip to latest
        subprocess.run(
            [str(self.python_exe), "-m", "pip", "install", "--upgrade", "pip"],
            capture_output=True, text=True
        )

    def install_package(
        self,
        package: str,
        progress_callback: Optional[Callable] = None,
        extra_args: Optional[list] = None
    ) -> bool:
        """Install a package into the embedded Python.

        Args:
            package: Package spec (e.g., "requests>=2.31.0")
            progress_callback: Optional callback(current, total, message)
            extra_args: Extra pip arguments (e.g., ["--index-url", "..."])

        Returns:
            True if installation succeeded.
        """
        if not self.is_installed:
            if progress_callback:
                progress_callback(0, 100, "Error: Embedded Python not found")
            return False

        try:
            if progress_callback:
                progress_callback(0, 100, f"Installing {package}...")

            cmd = [str(self.python_exe), "-m", "pip", "install", package]
            if extra_args:
                cmd.extend(extra_args)

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                if progress_callback:
                    progress_callback(0, 100, f"Error installing {package}: {result.stderr}")
                return False

            if progress_callback:
                progress_callback(100, 100, f"Installed {package}")
            return True

        except Exception as e:
            if progress_callback:
                progress_callback(0, 100, f"Error: {e}")
            return False

    def install_requirements(
        self,
        requirements_file: Path,
        progress_callback: Optional[Callable] = None
    ) -> bool:
        """Install packages from a requirements.txt file.

        Args:
            requirements_file: Path to requirements.txt
            progress_callback: Optional callback(current, total, message)

        Returns:
            True if installation succeeded.
        """
        if not self.is_installed:
            if progress_callback:
                progress_callback(0, 100, "Error: Embedded Python not found")
            return False

        if not requirements_file.exists():
            if progress_callback:
                progress_callback(0, 100, f"Error: {requirements_file} not found")
            return False

        try:
            if progress_callback:
                progress_callback(0, 100, f"Installing from {requirements_file.name}...")

            cmd = [str(self.python_exe), "-m", "pip", "install",
                   "-r", str(requirements_file)]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                if progress_callback:
                    progress_callback(0, 100, f"Error: {result.stderr}")
                return False

            if progress_callback:
                progress_callback(100, 100, "Requirements installed")
            return True

        except Exception as e:
            if progress_callback:
                progress_callback(0, 100, f"Error: {e}")
            return False

    def setup_tkinter(
        self,
        progress_callback: Optional[Callable] = None
    ) -> bool:
        """Download and install tkinter for embedded Python.

        The embeddable Python distribution does not include tkinter.
        We download the matching Python NuGet package and extract just
        the tkinter files (_tkinter.pyd, tcl/tk DLLs, Lib/tkinter/, tcl/).

        Args:
            progress_callback: Optional callback(current, total, message)

        Returns:
            True if tkinter is available after setup.
        """
        # Check if tkinter already works
        try:
            result = subprocess.run(
                [str(self.python_exe), "-c", "import _tkinter; print('ok')"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                if progress_callback:
                    progress_callback(100, 100, "tkinter already available")
                return True
        except Exception:
            pass

        if progress_callback:
            progress_callback(0, 100, "Downloading tkinter components...")

        try:
            import shutil
            nuget_url = f"https://www.nuget.org/api/v2/package/python/{PYTHON_VERSION}"
            zip_path = self.base_dir / "_python_nuget.zip"

            self._download_nuget(nuget_url, zip_path, progress_callback)

            if progress_callback:
                progress_callback(70, 100, "Extracting tkinter files...")

            # Files we need from the NuGet package (inside tools/ prefix)
            needed_dlls = {"_tkinter.pyd", "tcl86t.dll", "tk86t.dll"}

            with zipfile.ZipFile(zip_path, 'r') as zf:
                for member in zf.namelist():
                    # _tkinter.pyd, tcl86t.dll, tk86t.dll → python_embedded/
                    if member.startswith("tools/DLLs/"):
                        fname = Path(member).name
                        if fname in needed_dlls:
                            target = self.python_dir / fname
                            with zf.open(member) as src:
                                target.write_bytes(src.read())

                    # Lib/tkinter/ → python_embedded/Lib/tkinter/
                    elif member.startswith("tools/Lib/tkinter/"):
                        rel = member[len("tools/"):]
                        target = self.python_dir / rel
                        if member.endswith("/"):
                            target.mkdir(parents=True, exist_ok=True)
                        else:
                            target.parent.mkdir(parents=True, exist_ok=True)
                            with zf.open(member) as src:
                                target.write_bytes(src.read())

                    # tcl/ directory → python_embedded/tcl/
                    elif member.startswith("tools/tcl/"):
                        rel = member[len("tools/"):]
                        target = self.python_dir / rel
                        if member.endswith("/"):
                            target.mkdir(parents=True, exist_ok=True)
                        else:
                            target.parent.mkdir(parents=True, exist_ok=True)
                            with zf.open(member) as src:
                                target.write_bytes(src.read())

            # Clean up
            zip_path.unlink(missing_ok=True)

            if progress_callback:
                progress_callback(90, 100, "Verifying tkinter...")

            # Verify
            result = subprocess.run(
                [str(self.python_exe), "-c", "import tkinter; print('tkinter ok')"],
                capture_output=True, text=True
            )

            if result.returncode == 0:
                if progress_callback:
                    progress_callback(100, 100, "tkinter ready")
                return True
            else:
                if progress_callback:
                    progress_callback(0, 100, f"tkinter verification failed: {result.stderr}")
                return False

        except Exception as e:
            # Clean up on failure
            zip_path = self.base_dir / "_python_nuget.zip"
            zip_path.unlink(missing_ok=True)
            if progress_callback:
                progress_callback(0, 100, f"tkinter setup failed: {e}")
            return False

    def _download_nuget(
        self,
        url: str,
        dest: Path,
        progress_callback: Optional[Callable] = None
    ):
        """Download the Python NuGet package (follows redirects)."""
        import urllib.request
        import ssl

        ctx = ssl.create_default_context()
        req = urllib.request.Request(url, headers={
            "User-Agent": "ComfyUI-Module-Installer/1.0"
        })

        with urllib.request.urlopen(req, context=ctx) as response:
            total_size = int(response.headers.get("Content-Length", 0))
            downloaded = 0
            block_size = 65536

            with open(dest, "wb") as f:
                while True:
                    chunk = response.read(block_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_callback and total_size > 0:
                        pct = int(downloaded / total_size * 65) + 5  # 5-70% range
                        mb = downloaded // (1024 * 1024)
                        total_mb = total_size // (1024 * 1024)
                        progress_callback(pct, 100, f"Downloading tkinter... {mb}/{total_mb} MB")

    def get_python_version(self) -> Optional[str]:
        """Get the version string of the embedded Python."""
        if not self.python_exe.exists():
            return None
        try:
            result = subprocess.run(
                [str(self.python_exe), "--version"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except Exception:
            return None
