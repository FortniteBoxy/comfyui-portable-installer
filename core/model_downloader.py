"""
Model Downloader for ComfyUI Module
Handles downloading models from HuggingFace and direct URLs.
"""
import os
import shutil
from pathlib import Path
from typing import Optional, Callable, Dict, List, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import MODELS_DIR, MODEL_CATEGORIES

try:
    from huggingface_hub import hf_hub_download, HfApi, list_repo_files
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class ModelDownloader:
    """Downloads and manages AI models."""

    def __init__(self, models_dir: Optional[Path] = None):
        self.models_dir = models_dir or MODELS_DIR
        self.hf_api = HfApi() if HF_AVAILABLE else None
        self._download_cache_dir = self.models_dir / ".hf_cache"

    def _flatten_filename(self, filename: str) -> str:
        """Get the actual filename from a potentially nested path.

        HuggingFace repos may use paths like 'split_files/vae/model.safetensors'.
        After download and cleanup, the file is flattened to just 'model.safetensors'.
        """
        return Path(filename).name

    def check_model_exists(self, model_info: Dict) -> bool:
        """Check if a model file already exists."""
        folder = model_info.get("folder", "checkpoints")
        filename = model_info.get("filename", "")
        # Check both the nested path and the flattened name
        model_path = self.models_dir / folder / filename
        flat_path = self.models_dir / folder / self._flatten_filename(filename)
        return model_path.exists() or flat_path.exists()

    def get_model_path(self, model_info: Dict) -> Path:
        """Get the full path for a model (uses flattened filename)."""
        folder = model_info.get("folder", "checkpoints")
        filename = model_info.get("filename", "")
        flat_path = self.models_dir / folder / self._flatten_filename(filename)
        nested_path = self.models_dir / folder / filename
        # Return whichever exists, preferring the flat path
        if flat_path.exists():
            return flat_path
        if nested_path.exists():
            return nested_path
        return flat_path  # Default to flat

    def download_model(
        self,
        model_info: Dict,
        progress_callback: Optional[Callable] = None
    ) -> bool:
        """
        Download a model from HuggingFace or direct URL.

        model_info should contain:
            - repo: HuggingFace repo ID (e.g., "stabilityai/sdxl-vae")
            - filename: The filename to download
            - folder: Target folder (e.g., "vae", "checkpoints")
            - url: (optional) Direct download URL instead of HF
        """
        if self.check_model_exists(model_info):
            if progress_callback:
                progress_callback(100, 100, f"{model_info.get('name', 'Model')} already exists")
            return True

        # Determine download method
        if "url" in model_info:
            return self._download_direct(model_info, progress_callback)
        elif "repo" in model_info and HF_AVAILABLE:
            return self._download_huggingface(model_info, progress_callback)
        else:
            if progress_callback:
                progress_callback(0, 100, "Error: No download source specified or HF not available")
            return False

    def _download_huggingface(
        self,
        model_info: Dict,
        progress_callback: Optional[Callable] = None
    ) -> bool:
        """Download from HuggingFace Hub."""
        try:
            repo_id = model_info["repo"]
            filename = model_info["filename"]
            folder = model_info.get("folder", "checkpoints")
            subfolder = model_info.get("subfolder", None)

            target_dir = self.models_dir / folder
            target_dir.mkdir(parents=True, exist_ok=True)
            flat_name = self._flatten_filename(filename)
            final_path = target_dir / flat_name

            if progress_callback:
                progress_callback(0, 100, f"Downloading {flat_name} from {repo_id}...")

            # Set up cache directory
            os.environ["HF_HOME"] = str(self._download_cache_dir)
            os.environ["HF_HUB_CACHE"] = str(self._download_cache_dir)

            # Download file
            downloaded_path = hf_hub_download(
                repo_id=repo_id,
                filename=filename,
                subfolder=subfolder,
                local_dir=target_dir,
            )

            # Clean up any nested directories created by HF (flatten split_files etc.)
            self._cleanup_hf_structure(target_dir)

            # If the file didn't end up at the final location, move it
            downloaded_path = Path(downloaded_path)
            if not final_path.exists() and downloaded_path.exists():
                shutil.move(str(downloaded_path), str(final_path))

            if progress_callback:
                progress_callback(100, 100, f"Downloaded {flat_name}")

            return final_path.exists()

        except Exception as e:
            if progress_callback:
                progress_callback(0, 100, f"Error: {str(e)}")
            return False

    def _download_direct(
        self,
        model_info: Dict,
        progress_callback: Optional[Callable] = None
    ) -> bool:
        """Download from direct URL."""
        if not REQUESTS_AVAILABLE:
            if progress_callback:
                progress_callback(0, 100, "Error: requests library not available")
            return False

        try:
            url = model_info["url"]
            filename = model_info["filename"]
            folder = model_info.get("folder", "checkpoints")

            target_dir = self.models_dir / folder
            target_dir.mkdir(parents=True, exist_ok=True)
            target_path = target_dir / filename

            if progress_callback:
                progress_callback(0, 100, f"Downloading {filename}...")

            response = requests.get(url, stream=True)
            response.raise_for_status()

            total_size = int(response.headers.get("content-length", 0))
            downloaded = 0

            last_reported = -1
            with open(target_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=65536):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback and total_size > 0:
                            pct = int(downloaded / total_size * 100)
                            if pct != last_reported:
                                last_reported = pct
                                mb = downloaded // (1024 * 1024)
                                total_mb = total_size // (1024 * 1024)
                                progress_callback(pct, 100, f"Downloading {filename}... {mb}/{total_mb} MB")

            if progress_callback:
                progress_callback(100, 100, f"Downloaded {filename}")

            return target_path.exists()

        except Exception as e:
            if progress_callback:
                progress_callback(0, 100, f"Error: {str(e)}")
            return False

    def _cleanup_hf_structure(self, target_dir: Path):
        """Clean up nested directory structure from HuggingFace downloads.

        HF downloads with paths like 'split_files/vae/model.safetensors' create
        nested directories. This flattens everything to the target_dir level.
        """
        model_extensions = (".safetensors", ".ckpt", ".bin", ".pt", ".pth")

        for ext in model_extensions:
            for item in target_dir.rglob(f"*{ext}"):
                if item.parent != target_dir:
                    dest = target_dir / item.name
                    if not dest.exists():
                        shutil.move(str(item), str(dest))

        # Remove empty subdirectories (recursively, deepest first)
        for subdir in sorted(target_dir.rglob("*"), reverse=True):
            if subdir.is_dir():
                try:
                    subdir.rmdir()  # Only succeeds if empty
                except OSError:
                    pass

    def download_multiple(
        self,
        models: List[Dict],
        progress_callback: Optional[Callable] = None,
        max_workers: int = 3
    ) -> Dict[str, bool]:
        """Download multiple models with parallel downloads."""
        results = {}
        total = len(models)

        def download_with_tracking(model_info, index):
            def model_callback(current, total_steps, message):
                if progress_callback:
                    overall = int((index + current / 100) / total * 100)
                    progress_callback(overall, 100, message)

            success = self.download_model(model_info, model_callback)
            return model_info.get("name", model_info.get("filename")), success

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(download_with_tracking, model, i): model
                for i, model in enumerate(models)
            }

            for future in as_completed(futures):
                name, success = future.result()
                results[name] = success

        return results

    def search_huggingface(
        self,
        query: str,
        model_type: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict]:
        """Search HuggingFace for models."""
        if not HF_AVAILABLE or not self.hf_api:
            return []

        try:
            # Search for models
            models = self.hf_api.list_models(
                search=query,
                limit=limit,
                sort="downloads",
                direction=-1
            )

            results = []
            for model in models:
                # Try to find safetensors or ckpt files
                try:
                    files = list_repo_files(model.id)
                    model_files = [
                        f for f in files
                        if f.endswith((".safetensors", ".ckpt", ".bin"))
                        and not f.startswith(".")
                    ]

                    if model_files:
                        # Pick the most likely main model file
                        main_file = self._guess_main_file(model_files)
                        results.append({
                            "name": model.id.split("/")[-1],
                            "repo": model.id,
                            "filename": main_file,
                            "folder": self._guess_folder(model.id, main_file),
                            "downloads": model.downloads,
                            "files": model_files[:5],  # Include first 5 files
                        })
                except Exception:
                    continue

            return results

        except Exception as e:
            print(f"Search error: {e}")
            return []

    def _guess_main_file(self, files: List[str]) -> str:
        """Guess the main model file from a list of files."""
        # Prefer safetensors
        safetensors = [f for f in files if f.endswith(".safetensors")]
        if safetensors:
            # Look for common patterns
            for pattern in ["model", "diffusion", "unet", "vae"]:
                for f in safetensors:
                    if pattern in f.lower():
                        return f.split("/")[-1]
            return safetensors[0].split("/")[-1]

        # Fall back to ckpt
        ckpt = [f for f in files if f.endswith(".ckpt")]
        if ckpt:
            return ckpt[0].split("/")[-1]

        return files[0].split("/")[-1] if files else ""

    def _guess_folder(self, repo_id: str, filename: str) -> str:
        """Guess the appropriate model folder."""
        repo_lower = repo_id.lower()
        file_lower = filename.lower()

        if "vae" in repo_lower or "vae" in file_lower:
            return "vae"
        if "lora" in repo_lower or "lora" in file_lower:
            return "loras"
        if "controlnet" in repo_lower or "control" in file_lower:
            return "controlnet"
        if "clip" in repo_lower and "vision" in repo_lower:
            return "clip_vision"
        if "clip" in repo_lower:
            return "clip"
        if "upscale" in repo_lower or "esrgan" in repo_lower:
            return "upscale_models"
        if "embedding" in repo_lower or "textual" in repo_lower:
            return "embeddings"

        return "checkpoints"

    def scan_local_models(self) -> Dict[str, List[Dict]]:
        """Scan local models directory and return found models."""
        results = {}

        for category in MODEL_CATEGORIES:
            category_dir = self.models_dir / category
            if not category_dir.exists():
                results[category] = []
                continue

            models = []
            for file in category_dir.iterdir():
                if file.is_file() and file.suffix in [".safetensors", ".ckpt", ".bin", ".pt"]:
                    models.append({
                        "name": file.stem,
                        "filename": file.name,
                        "folder": category,
                        "path": str(file),
                        "size_gb": file.stat().st_size / (1024 ** 3),
                    })

            results[category] = models

        return results

    def list_available_models(self, category: str) -> List[Dict]:
        """Get models from registry for a category."""
        from data.models_registry import MODELS

        return [
            {**info, "id": model_id}
            for model_id, info in MODELS.items()
            if info.get("folder") == category
        ]

    def get_model_status(self, model_info: Dict) -> str:
        """Get status of a model: 'installed', 'missing', or 'downloading'."""
        if self.check_model_exists(model_info):
            return "installed"
        return "missing"
