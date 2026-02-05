"""
Portable Git Manager for ComfyUI Module

Downloads and configures MinGit for Windows, eliminating the need
for system-installed Git.
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
GIT_VERSION = "2.47.1"
MINGIT_URL = (
    f"https://github.com/git-for-windows/git/releases/download/"
    f"v{GIT_VERSION}.windows.1/MinGit-{GIT_VERSION}-64-bit.zip"
)
GIT_DIR_NAME = "git_portable"


class GitManager:
    """Manages portable Git download and configuration."""

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or BASE_DIR
        self.git_dir = self.base_dir / GIT_DIR_NAME
        self.git_exe = self.git_dir / "cmd" / "git.exe"

    @property
    def is_installed(self) -> bool:
        """Check if portable Git exists."""
        return self.git_exe.exists()

    def get_git_executable(self) -> str:
        """Return the path to the git executable.

        Uses portable Git if available, falls back to system git.

        Returns:
            Path string to git executable.
        """
        if self.is_installed:
            return str(self.git_exe)
        return "git"

    def ensure_git_in_path(self):
        """Add portable Git to PATH if available.

        This ensures subprocess calls to 'git' (including from GitPython)
        find our portable Git without requiring system installation.
        """
        if self.is_installed:
            git_cmd_dir = str(self.git_dir / "cmd")
            current_path = os.environ.get("PATH", "")
            if git_cmd_dir not in current_path:
                os.environ["PATH"] = git_cmd_dir + os.pathsep + current_path

    def download_and_setup(
        self,
        progress_callback: Optional[Callable] = None
    ) -> bool:
        """Download and extract portable MinGit.

        Args:
            progress_callback: Optional callback(current, total, message)

        Returns:
            True if setup completed successfully.
        """
        if self.is_installed:
            if progress_callback:
                progress_callback(100, 100, "Portable Git already installed")
            return True

        try:
            if progress_callback:
                progress_callback(0, 100, f"Downloading MinGit {GIT_VERSION}...")

            zip_path = self.base_dir / "git_portable.zip"
            self._download_file(MINGIT_URL, zip_path, progress_callback)

            if progress_callback:
                progress_callback(80, 100, "Extracting Git...")

            self.git_dir.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(self.git_dir)

            zip_path.unlink(missing_ok=True)

            # Add to PATH for this session
            self.ensure_git_in_path()

            if progress_callback:
                progress_callback(100, 100, "Portable Git ready")
            return True

        except Exception as e:
            if progress_callback:
                progress_callback(0, 100, f"Git download failed: {e}")
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
                        pct = int(downloaded / total_size * 75) + 5  # 5-80% range
                        mb = downloaded // (1024 * 1024)
                        total_mb = total_size // (1024 * 1024)
                        progress_callback(pct, 100, f"Downloading Git... {mb}/{total_mb} MB")

    def run_git(
        self,
        args: list,
        cwd: Optional[Path] = None,
        progress_callback: Optional[Callable] = None
    ) -> tuple:
        """Run a git command using portable or system git.

        Args:
            args: Git arguments (e.g., ["clone", "--depth", "1", url, dest])
            cwd: Working directory for the command.
            progress_callback: Optional callback(current, total, message)

        Returns:
            Tuple of (success: bool, output: str)
        """
        try:
            cmd = [self.get_git_executable()] + args
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=cwd
            )

            if result.returncode != 0:
                return False, result.stderr
            return True, result.stdout

        except FileNotFoundError:
            msg = "Git not found. Neither portable nor system Git is available."
            if progress_callback:
                progress_callback(0, 100, msg)
            return False, msg
        except Exception as e:
            return False, str(e)

    def get_git_version(self) -> Optional[str]:
        """Get the version string of the available git."""
        try:
            result = subprocess.run(
                [self.get_git_executable(), "--version"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except Exception:
            return None
