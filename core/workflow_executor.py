"""
Workflow Executor - High-level workflow execution with progress tracking

Provides easy-to-use workflow execution with:
- Progress callbacks via WebSocket
- Output collection
- Error handling
- Retry logic
"""
import uuid
import time
import threading
from pathlib import Path
from typing import Optional, Callable, Dict, List, Any, Union
from dataclasses import dataclass, field

from .comfy_api import ComfyAPI


@dataclass
class ExecutionProgress:
    """Progress information during execution."""
    status: str = "pending"  # pending, running, completed, failed, cancelled
    current_node: Optional[str] = None
    current_node_title: Optional[str] = None
    step: int = 0
    total_steps: int = 0
    preview_image: Optional[bytes] = None
    message: str = ""


@dataclass
class ExecutionResult:
    """Result of workflow execution."""
    success: bool
    prompt_id: str
    outputs: Dict = field(default_factory=dict)
    images: List[Dict] = field(default_factory=list)
    error: Optional[str] = None
    execution_time: float = 0.0


class WorkflowExecutor:
    """
    High-level workflow executor with progress tracking.

    Example:
        executor = WorkflowExecutor()

        def on_progress(progress):
            print(f"Status: {progress.status}, Node: {progress.current_node}")

        result = executor.execute(workflow, on_progress=on_progress)
        if result.success:
            for img in result.images:
                print(f"Output: {img['filename']}")
    """

    def __init__(
        self,
        api: Optional[ComfyAPI] = None,
        host: str = "127.0.0.1",
        port: int = 8188
    ):
        self.api = api or ComfyAPI(host, port)
        self._client_id = str(uuid.uuid4())
        self._current_execution: Optional[Dict] = None
        self._progress = ExecutionProgress()
        self._progress_callback: Optional[Callable] = None
        self._ws_connected = False

    def execute(
        self,
        workflow: Dict,
        on_progress: Optional[Callable[[ExecutionProgress], None]] = None,
        timeout: float = 600,
        use_websocket: bool = True
    ) -> ExecutionResult:
        """
        Execute a workflow with progress tracking.

        Args:
            workflow: The workflow prompt (node graph)
            on_progress: Callback for progress updates
            timeout: Maximum execution time in seconds
            use_websocket: Use WebSocket for real-time progress (recommended)

        Returns:
            ExecutionResult with outputs and status
        """
        self._progress_callback = on_progress
        self._progress = ExecutionProgress(status="pending")
        start_time = time.time()

        # Connect WebSocket for progress
        if use_websocket:
            self._connect_ws()

        try:
            # Queue the workflow
            self._update_progress(status="queued", message="Queuing workflow...")

            result = self.api.queue_prompt(workflow, client_id=self._client_id)
            prompt_id = result.get("prompt_id")

            if not prompt_id:
                return ExecutionResult(
                    success=False,
                    prompt_id="",
                    error="Failed to queue workflow"
                )

            # Check for immediate errors
            if result.get("node_errors"):
                return ExecutionResult(
                    success=False,
                    prompt_id=prompt_id,
                    error=f"Node errors: {result['node_errors']}"
                )

            self._update_progress(status="running", message="Executing workflow...")

            # Wait for completion
            if use_websocket:
                # WebSocket will handle progress updates
                history = self._wait_with_ws(prompt_id, timeout)
            else:
                # Poll for completion
                history = self.api.wait_for_prompt(prompt_id, timeout)

            execution_time = time.time() - start_time

            if history is None:
                return ExecutionResult(
                    success=False,
                    prompt_id=prompt_id,
                    error="Execution timed out",
                    execution_time=execution_time
                )

            # Check for execution errors
            if history.get("status", {}).get("status_str") == "error":
                error_msg = history.get("status", {}).get("messages", [])
                return ExecutionResult(
                    success=False,
                    prompt_id=prompt_id,
                    error=str(error_msg),
                    execution_time=execution_time
                )

            # Extract outputs
            outputs = history.get("outputs", {})
            images = self.api.get_output_images(history)

            self._update_progress(status="completed", message="Execution complete")

            return ExecutionResult(
                success=True,
                prompt_id=prompt_id,
                outputs=outputs,
                images=images,
                execution_time=execution_time
            )

        except Exception as e:
            return ExecutionResult(
                success=False,
                prompt_id="",
                error=str(e),
                execution_time=time.time() - start_time
            )
        finally:
            if use_websocket:
                self._disconnect_ws()

    def _connect_ws(self):
        """Connect WebSocket for progress."""
        def on_message(msg_type, data):
            if msg_type == "status":
                queue_remaining = data.get("status", {}).get("exec_info", {}).get("queue_remaining", 0)
                if queue_remaining == 0:
                    self._update_progress(message="Queue empty")

            elif msg_type == "executing":
                node_id = data.get("node")
                if node_id:
                    self._update_progress(
                        current_node=node_id,
                        message=f"Executing node: {node_id}"
                    )
                else:
                    # Execution complete
                    self._update_progress(status="completed")

            elif msg_type == "progress":
                value = data.get("value", 0)
                max_value = data.get("max", 100)
                self._update_progress(
                    step=value,
                    total_steps=max_value,
                    message=f"Progress: {value}/{max_value}"
                )

            elif msg_type == "executed":
                # Node finished, outputs available
                pass

        def on_error(error):
            self._update_progress(status="error", message=str(error))

        try:
            self.api.connect_websocket(
                client_id=self._client_id,
                on_message=on_message,
                on_error=on_error
            )
            self._ws_connected = True
            time.sleep(0.5)  # Wait for connection
        except Exception:
            self._ws_connected = False

    def _disconnect_ws(self):
        """Disconnect WebSocket."""
        if self._ws_connected:
            self.api.disconnect_websocket()
            self._ws_connected = False

    def _wait_with_ws(self, prompt_id: str, timeout: float) -> Optional[Dict]:
        """Wait for completion using WebSocket updates."""
        start_time = time.time()

        while time.time() - start_time < timeout:
            # Check if completed
            if self._progress.status == "completed":
                return self.api.get_history_item(prompt_id)

            # Check if errored
            if self._progress.status in ("error", "failed"):
                return self.api.get_history_item(prompt_id)

            # Check history
            history = self.api.get_history_item(prompt_id)
            if history:
                return history

            time.sleep(0.5)

        return None

    def _update_progress(
        self,
        status: Optional[str] = None,
        current_node: Optional[str] = None,
        current_node_title: Optional[str] = None,
        step: Optional[int] = None,
        total_steps: Optional[int] = None,
        preview_image: Optional[bytes] = None,
        message: Optional[str] = None
    ):
        """Update progress and notify callback."""
        if status:
            self._progress.status = status
        if current_node:
            self._progress.current_node = current_node
        if current_node_title:
            self._progress.current_node_title = current_node_title
        if step is not None:
            self._progress.step = step
        if total_steps is not None:
            self._progress.total_steps = total_steps
        if preview_image:
            self._progress.preview_image = preview_image
        if message:
            self._progress.message = message

        if self._progress_callback:
            try:
                self._progress_callback(self._progress)
            except Exception:
                pass

    def cancel(self, prompt_id: Optional[str] = None):
        """Cancel current or specific execution."""
        self.api.interrupt(prompt_id)
        self._update_progress(status="cancelled", message="Execution cancelled")

    def get_outputs_as_files(
        self,
        result: ExecutionResult,
        output_dir: Union[str, Path]
    ) -> List[Path]:
        """
        Download output images to files.

        Args:
            result: Execution result
            output_dir: Directory to save files

        Returns:
            List of saved file paths
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        saved_files = []
        for img_info in result.images:
            filename = img_info.get("filename", "")
            subfolder = img_info.get("subfolder", "")
            folder_type = img_info.get("type", "output")

            try:
                content = self.api.view_image(
                    filename=filename,
                    subfolder=subfolder,
                    folder_type=folder_type
                )

                output_path = output_dir / filename
                output_path.write_bytes(content)
                saved_files.append(output_path)
            except Exception:
                continue

        return saved_files


class BatchExecutor:
    """
    Execute multiple workflows in batch.

    Example:
        batch = BatchExecutor()
        results = batch.execute_batch([workflow1, workflow2, workflow3])
    """

    def __init__(
        self,
        api: Optional[ComfyAPI] = None,
        host: str = "127.0.0.1",
        port: int = 8188,
        max_concurrent: int = 1
    ):
        self.api = api or ComfyAPI(host, port)
        self.max_concurrent = max_concurrent
        self.executor = WorkflowExecutor(self.api)

    def execute_batch(
        self,
        workflows: List[Dict],
        on_progress: Optional[Callable[[int, int, ExecutionResult], None]] = None,
        timeout_per_workflow: float = 600
    ) -> List[ExecutionResult]:
        """
        Execute multiple workflows sequentially.

        Args:
            workflows: List of workflow prompts
            on_progress: Callback (index, total, result)
            timeout_per_workflow: Timeout per workflow

        Returns:
            List of ExecutionResults
        """
        results = []
        total = len(workflows)

        for i, workflow in enumerate(workflows):
            result = self.executor.execute(
                workflow,
                timeout=timeout_per_workflow,
                use_websocket=True
            )
            results.append(result)

            if on_progress:
                on_progress(i + 1, total, result)

        return results

    def cancel_all(self):
        """Cancel all pending and running workflows."""
        self.api.clear_queue()
        self.api.interrupt()
