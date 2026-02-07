"""
Custom Node Manager for ComfyUI Module
Handles installation and management of custom nodes.
"""
import subprocess
import shutil
from pathlib import Path
from typing import Optional, Callable, Dict, List

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import COMFYUI_DIR, GIT_PATH
from core.venv_manager import VenvManager


class CustomNodeManager:
    """Manages ComfyUI custom nodes."""

    def __init__(
        self,
        comfyui_dir: Optional[Path] = None,
        venv_manager: Optional[VenvManager] = None
    ):
        self.comfyui_dir = comfyui_dir or COMFYUI_DIR
        self.venv_manager = venv_manager or VenvManager()

    @property
    def custom_nodes_dir(self) -> Path:
        """Get custom_nodes directory path."""
        return self.comfyui_dir / "custom_nodes"

    def install_node(
        self,
        node_info: Dict,
        progress_callback: Optional[Callable] = None
    ) -> bool:
        """
        Install a custom node from git repository.

        node_info should contain:
            - repo: Git repository URL
            - name: Display name
            - (optional) branch: Specific branch to clone
        """
        repo_url = node_info.get("repo", "")
        name = node_info.get("name", repo_url.split("/")[-1].replace(".git", ""))
        branch = node_info.get("branch", None)

        # Determine target directory name from repo URL
        repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
        target_dir = self.custom_nodes_dir / repo_name

        if target_dir.exists():
            if progress_callback:
                progress_callback(100, 100, f"{name} already installed")
            return True

        try:
            if progress_callback:
                progress_callback(0, 100, f"Cloning {name}...")

            # Ensure custom_nodes directory exists
            self.custom_nodes_dir.mkdir(parents=True, exist_ok=True)

            # Build git clone command
            cmd = [GIT_PATH, "clone", "--depth", "1"]
            if branch:
                cmd.extend(["-b", branch])
            cmd.extend([repo_url, str(target_dir)])

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                if progress_callback:
                    progress_callback(0, 100, f"Error cloning {name}: {result.stderr}")
                return False

            if progress_callback:
                progress_callback(50, 100, f"Installing {name} requirements...")

            # Install node requirements if they exist
            self._install_node_requirements(target_dir, progress_callback)

            if progress_callback:
                progress_callback(100, 100, f"{name} installed successfully")
            return True

        except FileNotFoundError:
            if progress_callback:
                progress_callback(0, 100, "Error: git not found")
            return False
        except Exception as e:
            if progress_callback:
                progress_callback(0, 100, f"Error: {str(e)}")
            return False

    def _install_node_requirements(
        self,
        node_dir: Path,
        progress_callback: Optional[Callable] = None
    ) -> bool:
        """Install requirements for a custom node."""
        requirements_file = node_dir / "requirements.txt"

        if not requirements_file.exists():
            return True  # No requirements to install

        if not self.venv_manager.is_created:
            if progress_callback:
                progress_callback(0, 100, "Warning: venv not created, skipping requirements")
            return True

        return self.venv_manager.install_requirements(requirements_file, progress_callback)

    def remove_node(
        self,
        node_name: str,
        progress_callback: Optional[Callable] = None
    ) -> bool:
        """Remove a custom node."""
        # Find the node directory
        node_dir = None
        for d in self.custom_nodes_dir.iterdir():
            if d.is_dir() and (d.name == node_name or d.name.lower() == node_name.lower()):
                node_dir = d
                break

        if not node_dir or not node_dir.exists():
            if progress_callback:
                progress_callback(0, 100, f"Node {node_name} not found")
            return False

        try:
            if progress_callback:
                progress_callback(0, 100, f"Removing {node_name}...")

            shutil.rmtree(node_dir)

            if progress_callback:
                progress_callback(100, 100, f"{node_name} removed")
            return True

        except Exception as e:
            if progress_callback:
                progress_callback(0, 100, f"Error: {str(e)}")
            return False

    def list_installed_nodes(self) -> List[Dict]:
        """List all installed custom nodes."""
        if not self.custom_nodes_dir.exists():
            return []

        nodes = []
        for item in self.custom_nodes_dir.iterdir():
            if item.is_dir() and not item.name.startswith(".") and item.name != "__pycache__":
                # Try to get more info about the node
                info = {
                    "name": item.name,
                    "path": str(item),
                    "has_requirements": (item / "requirements.txt").exists(),
                    "has_init": (item / "__init__.py").exists(),
                }

                # Try to get git remote URL
                try:
                    result = subprocess.run(
                        [GIT_PATH, "remote", "get-url", "origin"],
                        capture_output=True,
                        text=True,
                        cwd=item
                    )
                    if result.returncode == 0:
                        info["repo"] = result.stdout.strip()
                except Exception:
                    pass

                nodes.append(info)

        return nodes

    def update_node(
        self,
        node_name: str,
        progress_callback: Optional[Callable] = None
    ) -> bool:
        """Update a custom node by pulling latest changes."""
        # Find the node directory
        node_dir = None
        for d in self.custom_nodes_dir.iterdir():
            if d.is_dir() and (d.name == node_name or d.name.lower() == node_name.lower()):
                node_dir = d
                break

        if not node_dir or not node_dir.exists():
            if progress_callback:
                progress_callback(0, 100, f"Node {node_name} not found")
            return False

        try:
            if progress_callback:
                progress_callback(0, 100, f"Updating {node_name}...")

            result = subprocess.run(
                [GIT_PATH, "pull"],
                capture_output=True,
                text=True,
                cwd=node_dir
            )

            if result.returncode != 0:
                if progress_callback:
                    progress_callback(0, 100, f"Error updating: {result.stderr}")
                return False

            # Reinstall requirements in case they changed
            if progress_callback:
                progress_callback(50, 100, "Checking requirements...")
            self._install_node_requirements(node_dir, progress_callback)

            if progress_callback:
                progress_callback(100, 100, f"{node_name} updated")
            return True

        except Exception as e:
            if progress_callback:
                progress_callback(0, 100, f"Error: {str(e)}")
            return False

    def update_all_nodes(
        self,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, bool]:
        """Update all installed custom nodes."""
        installed = self.list_installed_nodes()
        results = {}

        for i, node in enumerate(installed):
            if progress_callback:
                overall = int(i / len(installed) * 100)
                progress_callback(overall, 100, f"Updating {node['name']}...")

            results[node["name"]] = self.update_node(node["name"])

        if progress_callback:
            progress_callback(100, 100, "All nodes updated")

        return results

    def install_multiple(
        self,
        nodes: List[Dict],
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, bool]:
        """Install multiple custom nodes."""
        results = {}
        total = len(nodes)

        for i, node_info in enumerate(nodes):
            name = node_info.get("name", "Unknown")

            def node_callback(current, total_steps, message):
                if progress_callback:
                    overall = int((i + current / 100) / total * 100)
                    progress_callback(overall, 100, message)

            success = self.install_node(node_info, node_callback)
            results[name] = success

        if progress_callback:
            progress_callback(100, 100, "Installation complete")

        return results

    def check_node_installed(self, node_info: Dict) -> bool:
        """Check if a specific node is installed."""
        repo_url = node_info.get("repo", "")
        repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")

        # Check by directory name
        target_dir = self.custom_nodes_dir / repo_name
        if target_dir.exists():
            return True

        # Also check installed nodes' repo URLs
        for node in self.list_installed_nodes():
            if node.get("repo", "").rstrip("/") == repo_url.rstrip("/"):
                return True

        return False

    def get_node_status(self, node_info: Dict) -> str:
        """Get status of a node: 'installed' or 'not_installed'."""
        if self.check_node_installed(node_info):
            return "installed"
        return "not_installed"
