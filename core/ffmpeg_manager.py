"""
Portable FFmpeg Manager for ComfyUI Module

Downloads and configures portable FFmpeg for Windows, eliminating the need
for system-installed FFmpeg. Used by video custom nodes (Video Helper Suite, etc).
"""
import os
import subprocess
import zipfile
import shutil
from pathlib import Path
from typing import Optional, Callable

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import BASE_DIR


# Constants
# gyan.dev essentials build: ffmpeg + ffprobe + ffplay with common codecs (~85MB)
FFMPEG_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
FFMPEG_DIR_NAME = "ffmpeg_portable"


class FfmpegManager:
    """Manages portable FFmpeg download and configuration."""

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or BASE_DIR
        self.ffmpeg_dir = self.base_dir / FFMPEG_DIR_NAME
        self.ffmpeg_exe = self.ffmpeg_dir / "bin" / "ffmpeg.exe"
        self.ffprobe_exe = self.ffmpeg_dir / "bin" / "ffprobe.exe"

    @property
    def is_installed(self) -> bool:
        """Check if portable FFmpeg exists."""
        return self.ffmpeg_exe.exists()

    def get_ffmpeg_executable(self) -> str:
        """Return path to ffmpeg executable.

        Uses portable FFmpeg if available, falls back to system ffmpeg.
        """
        if self.is_installed:
            return str(self.ffmpeg_exe)
        return "ffmpeg"

    def get_ffprobe_executable(self) -> str:
        """Return path to ffprobe executable."""
        if self.ffprobe_exe.exists():
            return str(self.ffprobe_exe)
        return "ffprobe"

    def ensure_ffmpeg_in_path(self):
        """Add portable FFmpeg to PATH if available.

        This ensures subprocess calls to 'ffmpeg' (including from custom nodes
        like Video Helper Suite) find our portable FFmpeg.
        """
        if self.is_installed:
            ffmpeg_bin_dir = str(self.ffmpeg_dir / "bin")
            current_path = os.environ.get("PATH", "")
            if ffmpeg_bin_dir not in current_path:
                os.environ["PATH"] = ffmpeg_bin_dir + os.pathsep + current_path

    def download_and_setup(
        self,
        progress_callback: Optional[Callable] = None
    ) -> bool:
        """Download and extract portable FFmpeg.

        The gyan.dev essentials zip has a versioned top-level directory
        (e.g., ffmpeg-7.1-essentials_build/). We flatten it so the
        binaries end up at ffmpeg_portable/bin/ffmpeg.exe.

        Args:
            progress_callback: Optional callback(current, total, message)

        Returns:
            True if setup completed successfully.
        """
        if self.is_installed:
            if progress_callback:
                progress_callback(100, 100, "Portable FFmpeg already installed")
            return True

        try:
            if progress_callback:
                progress_callback(0, 100, "Downloading FFmpeg...")

            zip_path = self.base_dir / "ffmpeg_portable.zip"
            self._download_file(FFMPEG_URL, zip_path, progress_callback)

            if progress_callback:
                progress_callback(75, 100, "Extracting FFmpeg...")

            # Extract to temp directory first (zip has versioned top-level dir)
            temp_dir = self.base_dir / "_ffmpeg_temp"
            temp_dir.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(temp_dir)

            # Find the inner versioned directory (e.g., ffmpeg-7.1-essentials_build/)
            inner_dirs = [d for d in temp_dir.iterdir() if d.is_dir()]
            if not inner_dirs:
                raise RuntimeError("FFmpeg zip has unexpected structure (no inner directory)")

            inner_dir = inner_dirs[0]

            # Move the bin/ directory to our target location
            self.ffmpeg_dir.mkdir(parents=True, exist_ok=True)
            bin_src = inner_dir / "bin"
            bin_dest = self.ffmpeg_dir / "bin"

            if bin_src.exists():
                if bin_dest.exists():
                    shutil.rmtree(bin_dest)
                shutil.move(str(bin_src), str(bin_dest))
            else:
                raise RuntimeError("FFmpeg zip missing bin/ directory")

            # Clean up temp and zip
            shutil.rmtree(temp_dir, ignore_errors=True)
            zip_path.unlink(missing_ok=True)

            # Add to PATH for this session
            self.ensure_ffmpeg_in_path()

            if progress_callback:
                progress_callback(100, 100, "Portable FFmpeg ready")
            return True

        except Exception as e:
            # Clean up on failure
            temp_dir = self.base_dir / "_ffmpeg_temp"
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)
            zip_path = self.base_dir / "ffmpeg_portable.zip"
            zip_path.unlink(missing_ok=True)

            if progress_callback:
                progress_callback(0, 100, f"FFmpeg download failed: {e}")
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
                        pct = int(downloaded / total_size * 70) + 5  # 5-75% range
                        mb = downloaded // (1024 * 1024)
                        total_mb = total_size // (1024 * 1024)
                        progress_callback(pct, 100, f"Downloading FFmpeg... {mb}/{total_mb} MB")

    def get_ffmpeg_version(self) -> Optional[str]:
        """Get the version string of the available ffmpeg."""
        try:
            exe = self.get_ffmpeg_executable()
            result = subprocess.run(
                [exe, "-version"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                # First line is like "ffmpeg version 7.1-essentials_build-..."
                first_line = result.stdout.split("\n")[0]
                return first_line.strip()
            return None
        except Exception:
            return None
