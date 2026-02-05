"""
ComfyUI API Client - Full Control Over All ComfyUI APIs

Comprehensive API client covering all ComfyUI endpoints:
- Queue management (queue prompt, get queue, clear queue, delete items)
- History (get history, clear history, delete history items)
- Models (list model folders, list models, get metadata)
- System (stats, features, free memory)
- Object/Node info (get all nodes, get specific node)
- Execution control (interrupt, cancel)
- File management (view, upload images/masks)
- User data management
- Settings
- WebSocket for real-time updates
"""
import json
import asyncio
import threading
from pathlib import Path
from typing import Optional, Callable, Dict, List, Any, Union
from dataclasses import dataclass
from enum import Enum

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import websocket
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False


class QueuePosition(Enum):
    """Queue position for new prompts."""
    BACK = "back"
    FRONT = "front"


@dataclass
class QueueStatus:
    """Current queue status."""
    queue_running: List[Dict]
    queue_pending: List[Dict]

    @property
    def running_count(self) -> int:
        return len(self.queue_running)

    @property
    def pending_count(self) -> int:
        return len(self.queue_pending)

    @property
    def total_count(self) -> int:
        return self.running_count + self.pending_count

    @property
    def is_empty(self) -> bool:
        return self.total_count == 0


@dataclass
class SystemStats:
    """System statistics."""
    system: Dict
    devices: List[Dict]
    version: str

    @property
    def vram_total(self) -> int:
        """Total VRAM in bytes."""
        if self.devices:
            return self.devices[0].get("vram_total", 0)
        return 0

    @property
    def vram_free(self) -> int:
        """Free VRAM in bytes."""
        if self.devices:
            return self.devices[0].get("vram_free", 0)
        return 0


class ComfyAPI:
    """
    Comprehensive ComfyUI API Client.

    Provides full control over all ComfyUI REST APIs and WebSocket connections.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 8188):
        self.host = host
        self.port = port
        self._ws = None
        self._ws_thread = None
        self._ws_callbacks: Dict[str, List[Callable]] = {}
        self._client_id: Optional[str] = None

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"

    @property
    def ws_url(self) -> str:
        url = f"ws://{self.host}:{self.port}/ws"
        if self._client_id:
            url += f"?clientId={self._client_id}"
        return url

    # =========================================================================
    # UTILITY METHODS
    # =========================================================================

    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make GET request."""
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests library not available")

        try:
            response = requests.get(
                f"{self.base_url}{endpoint}",
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json() if response.content else None
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"API request failed: {e}")

    def _post(
        self,
        endpoint: str,
        data: Optional[Dict] = None,
        files: Optional[Dict] = None,
        json_data: Optional[Dict] = None
    ) -> Optional[Dict]:
        """Make POST request."""
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests library not available")

        try:
            response = requests.post(
                f"{self.base_url}{endpoint}",
                data=data,
                files=files,
                json=json_data,
                timeout=30
            )
            response.raise_for_status()
            return response.json() if response.content else None
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"API request failed: {e}")

    def _delete(self, endpoint: str) -> bool:
        """Make DELETE request."""
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests library not available")

        try:
            response = requests.delete(
                f"{self.base_url}{endpoint}",
                timeout=30
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException:
            return False

    def is_available(self) -> bool:
        """Check if ComfyUI server is available."""
        try:
            self._get("/system_stats")
            return True
        except Exception:
            return False

    # =========================================================================
    # QUEUE MANAGEMENT
    # =========================================================================

    def queue_prompt(
        self,
        prompt: Dict,
        client_id: Optional[str] = None,
        front: bool = False,
        number: Optional[int] = None,
        extra_data: Optional[Dict] = None
    ) -> Dict:
        """
        Queue a workflow/prompt for execution.

        Args:
            prompt: The workflow prompt (node graph)
            client_id: Client ID for WebSocket notifications
            front: If True, add to front of queue
            number: Optional queue number
            extra_data: Extra data to pass (e.g., extra_pnginfo)

        Returns:
            Dict with prompt_id, number, and node_errors
        """
        payload = {"prompt": prompt}

        if client_id or self._client_id:
            payload["client_id"] = client_id or self._client_id
        if front:
            payload["front"] = True
        if number is not None:
            payload["number"] = number
        if extra_data:
            payload["extra_data"] = extra_data

        return self._post("/prompt", json_data=payload)

    def get_queue(self) -> QueueStatus:
        """
        Get current queue status.

        Returns:
            QueueStatus with running and pending queues
        """
        result = self._get("/queue")
        return QueueStatus(
            queue_running=result.get("queue_running", []),
            queue_pending=result.get("queue_pending", [])
        )

    def get_queue_remaining(self) -> Dict:
        """
        Get remaining items in queue.

        Returns:
            Dict with exec_info containing queue_remaining count
        """
        return self._get("/prompt")

    def clear_queue(self) -> None:
        """Clear all items from the queue."""
        self._post("/queue", json_data={"clear": True})

    def delete_queue_items(self, prompt_ids: List[str]) -> None:
        """
        Delete specific items from the queue.

        Args:
            prompt_ids: List of prompt IDs to delete
        """
        self._post("/queue", json_data={"delete": prompt_ids})

    # =========================================================================
    # HISTORY MANAGEMENT
    # =========================================================================

    def get_history(
        self,
        max_items: Optional[int] = None,
        offset: Optional[int] = None
    ) -> Dict:
        """
        Get execution history.

        Args:
            max_items: Maximum number of items to return
            offset: Offset for pagination

        Returns:
            Dict mapping prompt_id to history entry
        """
        params = {}
        if max_items is not None:
            params["max_items"] = max_items
        if offset is not None:
            params["offset"] = offset

        return self._get("/history", params=params if params else None)

    def get_history_item(self, prompt_id: str) -> Optional[Dict]:
        """
        Get history for a specific prompt.

        Args:
            prompt_id: The prompt ID to look up

        Returns:
            History entry or None
        """
        result = self._get(f"/history/{prompt_id}")
        return result.get(prompt_id) if result else None

    def clear_history(self) -> None:
        """Clear all history."""
        self._post("/history", json_data={"clear": True})

    def delete_history_items(self, prompt_ids: List[str]) -> None:
        """
        Delete specific items from history.

        Args:
            prompt_ids: List of prompt IDs to delete
        """
        self._post("/history", json_data={"delete": prompt_ids})

    # =========================================================================
    # JOBS API (Enhanced Queue/History)
    # =========================================================================

    def get_jobs(
        self,
        status: Optional[List[str]] = None,
        workflow_id: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        limit: int = 100,
        offset: int = 0
    ) -> Dict:
        """
        Get jobs with filtering and sorting.

        Args:
            status: Filter by status (pending, in_progress, completed, failed)
            workflow_id: Filter by workflow ID
            sort_by: Sort field (created_at, execution_duration)
            sort_order: Sort order (asc, desc)
            limit: Max items to return
            offset: Pagination offset

        Returns:
            Dict with jobs list and pagination info
        """
        params = {
            "sort_by": sort_by,
            "sort_order": sort_order,
            "limit": limit,
            "offset": offset
        }

        if status:
            params["status"] = ",".join(status)
        if workflow_id:
            params["workflow_id"] = workflow_id

        return self._get("/api/jobs", params=params)

    def get_job(self, job_id: str) -> Optional[Dict]:
        """
        Get specific job details.

        Args:
            job_id: The job ID

        Returns:
            Job details or None
        """
        return self._get(f"/api/jobs/{job_id}")

    # =========================================================================
    # EXECUTION CONTROL
    # =========================================================================

    def interrupt(self, prompt_id: Optional[str] = None) -> None:
        """
        Interrupt execution.

        Args:
            prompt_id: If provided, interrupt specific prompt; otherwise interrupt all
        """
        payload = {}
        if prompt_id:
            payload["prompt_id"] = prompt_id
        self._post("/interrupt", json_data=payload)

    def free_memory(
        self,
        unload_models: bool = True,
        free_memory: bool = True
    ) -> None:
        """
        Free GPU memory.

        Args:
            unload_models: Unload all models from VRAM
            free_memory: Free cached memory
        """
        self._post("/free", json_data={
            "unload_models": unload_models,
            "free_memory": free_memory
        })

    # =========================================================================
    # MODELS
    # =========================================================================

    def get_model_folders(self) -> List[str]:
        """
        Get list of model folder types.

        Returns:
            List of folder names (checkpoints, loras, vae, etc.)
        """
        return self._get("/models")

    def get_models(self, folder: str) -> List[str]:
        """
        Get list of models in a folder.

        Args:
            folder: Folder name (checkpoints, loras, vae, etc.)

        Returns:
            List of model filenames
        """
        return self._get(f"/models/{folder}")

    def get_model_metadata(self, folder: str, filename: str) -> Optional[Dict]:
        """
        Get safetensors metadata for a model.

        Args:
            folder: Model folder
            filename: Model filename

        Returns:
            Metadata dict or None
        """
        return self._get(f"/view_metadata/{folder}", params={"filename": filename})

    def get_embeddings(self) -> List[str]:
        """
        Get list of available embeddings.

        Returns:
            List of embedding names
        """
        return self._get("/embeddings")

    # =========================================================================
    # OBJECT/NODE INFO
    # =========================================================================

    def get_object_info(self) -> Dict:
        """
        Get definitions for all available nodes.

        Returns:
            Dict mapping node class names to their definitions
        """
        return self._get("/object_info")

    def get_node_info(self, node_class: str) -> Optional[Dict]:
        """
        Get definition for a specific node class.

        Args:
            node_class: Node class name (e.g., "KSampler")

        Returns:
            Node definition or None
        """
        result = self._get(f"/object_info/{node_class}")
        return result.get(node_class) if result else None

    # =========================================================================
    # SYSTEM INFO
    # =========================================================================

    def get_system_stats(self) -> SystemStats:
        """
        Get system statistics.

        Returns:
            SystemStats with system info, devices, and version
        """
        result = self._get("/system_stats")
        return SystemStats(
            system=result.get("system", {}),
            devices=result.get("devices", []),
            version=result.get("system", {}).get("comfyui_version", "unknown")
        )

    def get_features(self) -> Dict:
        """
        Get server feature flags.

        Returns:
            Dict of feature flags
        """
        return self._get("/features")

    # =========================================================================
    # FILE MANAGEMENT
    # =========================================================================

    def view_image(
        self,
        filename: str,
        subfolder: str = "",
        folder_type: str = "output",
        preview: Optional[str] = None,
        channel: Optional[str] = None
    ) -> bytes:
        """
        Get image file content.

        Args:
            filename: Image filename
            subfolder: Subfolder within the folder type
            folder_type: Folder type (input, temp, output)
            preview: Preview format (webp, jpeg;90)
            channel: Channel filter (rgba, rgb, a)

        Returns:
            Image bytes
        """
        params = {
            "filename": filename,
            "type": folder_type
        }
        if subfolder:
            params["subfolder"] = subfolder
        if preview:
            params["preview"] = preview
        if channel:
            params["channel"] = channel

        response = requests.get(
            f"{self.base_url}/view",
            params=params,
            timeout=30
        )
        response.raise_for_status()
        return response.content

    def upload_image(
        self,
        file_path: Union[str, Path],
        folder_type: str = "input",
        subfolder: str = "",
        overwrite: bool = True
    ) -> Dict:
        """
        Upload an image file.

        Args:
            file_path: Path to image file
            folder_type: Folder type (input, temp, output)
            subfolder: Subfolder within the folder type
            overwrite: Overwrite if exists

        Returns:
            Dict with name, subfolder, type
        """
        file_path = Path(file_path)
        with open(file_path, "rb") as f:
            files = {"image": (file_path.name, f, "image/png")}
            data = {
                "type": folder_type,
                "overwrite": str(overwrite).lower()
            }
            if subfolder:
                data["subfolder"] = subfolder

            return self._post("/upload/image", data=data, files=files)

    def upload_mask(
        self,
        file_path: Union[str, Path],
        original_ref: Dict,
        folder_type: str = "input",
        subfolder: str = "",
        overwrite: bool = True
    ) -> Dict:
        """
        Upload a mask image.

        Args:
            file_path: Path to mask image
            original_ref: Reference to original image {filename, subfolder, type}
            folder_type: Folder type
            subfolder: Subfolder
            overwrite: Overwrite if exists

        Returns:
            Dict with name, subfolder, type
        """
        file_path = Path(file_path)
        with open(file_path, "rb") as f:
            files = {"image": (file_path.name, f, "image/png")}
            data = {
                "original_ref": json.dumps(original_ref),
                "type": folder_type,
                "overwrite": str(overwrite).lower()
            }
            if subfolder:
                data["subfolder"] = subfolder

            return self._post("/upload/mask", data=data, files=files)

    def get_extensions(self) -> List[str]:
        """
        Get list of available frontend extensions.

        Returns:
            List of extension paths
        """
        return self._get("/extensions")

    # =========================================================================
    # USER DATA
    # =========================================================================

    def list_userdata(
        self,
        directory: str,
        recurse: bool = False,
        full_info: bool = False
    ) -> List:
        """
        List user data files.

        Args:
            directory: Directory to list (e.g., "workflows")
            recurse: Recurse into subdirectories
            full_info: Return full file info

        Returns:
            List of files/directories
        """
        params = {
            "dir": directory,
            "recurse": str(recurse).lower(),
            "full_info": str(full_info).lower()
        }
        return self._get("/userdata", params=params)

    def get_userdata(self, file_path: str) -> bytes:
        """
        Get user data file content.

        Args:
            file_path: Relative path to file

        Returns:
            File content bytes
        """
        response = requests.get(
            f"{self.base_url}/userdata/{file_path}",
            timeout=30
        )
        response.raise_for_status()
        return response.content

    def save_userdata(
        self,
        file_path: str,
        content: Union[str, bytes],
        overwrite: bool = True
    ) -> Dict:
        """
        Save user data file.

        Args:
            file_path: Relative path to file
            content: File content
            overwrite: Overwrite if exists

        Returns:
            File info
        """
        if isinstance(content, str):
            content = content.encode()

        response = requests.post(
            f"{self.base_url}/userdata/{file_path}",
            params={"overwrite": str(overwrite).lower()},
            data=content,
            timeout=30
        )
        response.raise_for_status()
        return response.json() if response.content else {}

    def delete_userdata(self, file_path: str) -> bool:
        """
        Delete user data file.

        Args:
            file_path: Relative path to file

        Returns:
            True if deleted
        """
        return self._delete(f"/userdata/{file_path}")

    def move_userdata(
        self,
        source: str,
        dest: str,
        overwrite: bool = True
    ) -> Dict:
        """
        Move/rename user data file.

        Args:
            source: Source path
            dest: Destination path
            overwrite: Overwrite if exists

        Returns:
            File info
        """
        response = requests.post(
            f"{self.base_url}/userdata/{source}/move/{dest}",
            params={"overwrite": str(overwrite).lower()},
            timeout=30
        )
        response.raise_for_status()
        return response.json() if response.content else {}

    # =========================================================================
    # SETTINGS
    # =========================================================================

    def get_settings(self) -> Dict:
        """
        Get all user settings.

        Returns:
            Dict of settings
        """
        return self._get("/settings")

    def get_setting(self, setting_id: str) -> Any:
        """
        Get specific setting value.

        Args:
            setting_id: Setting ID

        Returns:
            Setting value
        """
        return self._get(f"/settings/{setting_id}")

    def update_settings(self, settings: Dict) -> None:
        """
        Update multiple settings.

        Args:
            settings: Dict of setting_id -> value
        """
        self._post("/settings", json_data=settings)

    def update_setting(self, setting_id: str, value: Any) -> None:
        """
        Update a single setting.

        Args:
            setting_id: Setting ID
            value: New value
        """
        self._post(f"/settings/{setting_id}", json_data=value)

    # =========================================================================
    # WORKFLOW TEMPLATES
    # =========================================================================

    def get_workflow_templates(self) -> Dict:
        """
        Get workflow templates from custom nodes.

        Returns:
            Dict mapping custom_node_name to template names
        """
        return self._get("/workflow_templates")

    # =========================================================================
    # SUBGRAPHS (Blueprints)
    # =========================================================================

    def get_subgraphs(self) -> List[Dict]:
        """
        Get list of available subgraphs/blueprints.

        Returns:
            List of subgraph metadata
        """
        return self._get("/global_subgraphs")

    def get_subgraph(self, subgraph_id: str) -> Optional[Dict]:
        """
        Get specific subgraph data.

        Args:
            subgraph_id: Subgraph ID

        Returns:
            Subgraph data or None
        """
        return self._get(f"/global_subgraphs/{subgraph_id}")

    # =========================================================================
    # INTERNAL ENDPOINTS (Frontend use, not stable)
    # =========================================================================

    def get_logs(self, raw: bool = False) -> Union[str, Dict]:
        """
        Get system logs.

        Args:
            raw: If True, get raw logs with terminal size info

        Returns:
            Logs string or Dict with entries and size
        """
        endpoint = "/internal/logs/raw" if raw else "/internal/logs"
        return self._get(endpoint)

    def get_folder_paths(self) -> Dict:
        """
        Get folder paths configuration.

        Returns:
            Dict of folder path configurations
        """
        return self._get("/internal/folder_paths")

    def list_files(self, directory_type: str) -> List[str]:
        """
        List files in a directory.

        Args:
            directory_type: Directory type (output, input, temp)

        Returns:
            Sorted list of filenames
        """
        return self._get(f"/internal/files/{directory_type}")

    # =========================================================================
    # WEBSOCKET (Real-time Updates)
    # =========================================================================

    def connect_websocket(
        self,
        client_id: Optional[str] = None,
        on_message: Optional[Callable] = None,
        on_error: Optional[Callable] = None,
        on_close: Optional[Callable] = None
    ) -> None:
        """
        Connect to WebSocket for real-time updates.

        Args:
            client_id: Client ID (used for prompt routing)
            on_message: Callback for messages (msg_type, data)
            on_error: Callback for errors
            on_close: Callback for close
        """
        if not WEBSOCKET_AVAILABLE:
            raise ImportError("websocket-client library not available")

        self._client_id = client_id

        def _on_message(ws, message):
            try:
                data = json.loads(message)
                msg_type = data.get("type", "unknown")
                msg_data = data.get("data", {})
                if on_message:
                    on_message(msg_type, msg_data)
                # Call registered callbacks
                for callback in self._ws_callbacks.get(msg_type, []):
                    callback(msg_data)
            except json.JSONDecodeError:
                # Binary message
                if on_message:
                    on_message("binary", message)

        def _on_error(ws, error):
            if on_error:
                on_error(error)

        def _on_close(ws, close_status_code, close_msg):
            if on_close:
                on_close(close_status_code, close_msg)

        def _run():
            self._ws = websocket.WebSocketApp(
                self.ws_url,
                on_message=_on_message,
                on_error=_on_error,
                on_close=_on_close
            )
            self._ws.run_forever()

        self._ws_thread = threading.Thread(target=_run, daemon=True)
        self._ws_thread.start()

    def disconnect_websocket(self) -> None:
        """Disconnect WebSocket."""
        if self._ws:
            self._ws.close()
            self._ws = None

    def on(self, event_type: str, callback: Callable) -> None:
        """
        Register callback for WebSocket event type.

        Args:
            event_type: Event type (status, executing, executed, progress, etc.)
            callback: Callback function (data)
        """
        if event_type not in self._ws_callbacks:
            self._ws_callbacks[event_type] = []
        self._ws_callbacks[event_type].append(callback)

    def off(self, event_type: str, callback: Optional[Callable] = None) -> None:
        """
        Unregister callback for WebSocket event type.

        Args:
            event_type: Event type
            callback: Specific callback to remove (None removes all)
        """
        if event_type in self._ws_callbacks:
            if callback:
                self._ws_callbacks[event_type].remove(callback)
            else:
                self._ws_callbacks[event_type] = []

    # =========================================================================
    # HIGH-LEVEL HELPERS
    # =========================================================================

    def wait_for_prompt(
        self,
        prompt_id: str,
        timeout: float = 300,
        poll_interval: float = 1.0
    ) -> Optional[Dict]:
        """
        Wait for a prompt to complete and return its history.

        Args:
            prompt_id: The prompt ID to wait for
            timeout: Maximum time to wait in seconds
            poll_interval: Time between polls in seconds

        Returns:
            History entry when complete, or None on timeout
        """
        import time
        start_time = time.time()

        while time.time() - start_time < timeout:
            history = self.get_history_item(prompt_id)
            if history:
                return history

            # Check if still in queue
            queue = self.get_queue()
            in_queue = any(
                item[1] == prompt_id
                for item in queue.queue_running + queue.queue_pending
            )

            if not in_queue and not history:
                # Not in queue and not in history - might have failed
                time.sleep(poll_interval)
                # Check history one more time
                history = self.get_history_item(prompt_id)
                if history:
                    return history

            time.sleep(poll_interval)

        return None

    def execute_workflow(
        self,
        workflow: Dict,
        wait: bool = True,
        timeout: float = 300
    ) -> Dict:
        """
        Execute a workflow and optionally wait for completion.

        Args:
            workflow: The workflow prompt
            wait: Whether to wait for completion
            timeout: Timeout if waiting

        Returns:
            If wait=True, returns history entry; otherwise returns queue response
        """
        result = self.queue_prompt(workflow)
        prompt_id = result.get("prompt_id")

        if not wait:
            return result

        history = self.wait_for_prompt(prompt_id, timeout)
        if history is None:
            raise TimeoutError(f"Workflow {prompt_id} did not complete within {timeout}s")

        return history

    def get_output_images(self, history_entry: Dict) -> List[Dict]:
        """
        Extract output images from a history entry.

        Args:
            history_entry: History entry from get_history_item()

        Returns:
            List of image info dicts with filename, subfolder, type
        """
        images = []
        outputs = history_entry.get("outputs", {})

        for node_id, node_output in outputs.items():
            if "images" in node_output:
                images.extend(node_output["images"])

        return images
