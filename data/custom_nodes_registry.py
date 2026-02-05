"""
Custom Nodes Registry for ComfyUI Module
Recommended and popular custom nodes for ComfyUI.
"""

# Custom nodes registry with installation info
CUSTOM_NODES = {
    # ===================
    # ESSENTIAL
    # ===================
    "comfyui-manager": {
        "name": "ComfyUI Manager",
        "repo": "https://github.com/ltdrdata/ComfyUI-Manager.git",
        "description": "Install and manage custom nodes directly from the UI. Essential for easy node management.",
        "required": True,
        "category": "essential",
        "tags": ["manager", "installer", "updates"],
    },

    # ===================
    # RECOMMENDED (High utility for API workflows)
    # ===================
    "impact-pack": {
        "name": "ComfyUI Impact Pack",
        "repo": "https://github.com/ltdrdata/ComfyUI-Impact-Pack.git",
        "description": "Detectors, detailers, iterative upscale, and more. Great for face fixing and detail enhancement.",
        "category": "recommended",
        "tags": ["face", "detailer", "upscale", "detector"],
    },
    "rgthree": {
        "name": "rgthree Nodes",
        "repo": "https://github.com/rgthree/rgthree-comfy.git",
        "description": "Context nodes, seed management, reroute, LoRA stacks. Essential workflow organization tools.",
        "category": "recommended",
        "tags": ["context", "seed", "lora", "organization"],
    },
    "efficiency-nodes": {
        "name": "Efficiency Nodes",
        "repo": "https://github.com/jags111/efficiency-nodes-comfyui.git",
        "description": "Streamlined nodes for efficient workflows. KSampler variants and batch processing.",
        "category": "recommended",
        "tags": ["sampler", "batch", "efficiency"],
    },
    "comfyui-tooling": {
        "name": "ComfyUI Tooling Nodes",
        "repo": "https://github.com/Acly/comfyui-tooling-nodes.git",
        "description": "Utility nodes for external integrations. Load/send images to external tools.",
        "category": "recommended",
        "tags": ["api", "integration", "external"],
    },

    # ===================
    # POPULAR (Widely used, feature-rich)
    # ===================
    "was-suite": {
        "name": "WAS Node Suite",
        "repo": "https://github.com/WASasquatch/was-node-suite-comfyui.git",
        "description": "Hundreds of utility nodes for image processing, prompts, and more.",
        "category": "popular",
        "tags": ["utility", "image", "prompt", "comprehensive"],
    },
    "essentials": {
        "name": "ComfyUI Essentials",
        "repo": "https://github.com/cubiq/ComfyUI_essentials.git",
        "description": "Quality-of-life workflow nodes. Dimension printing, simple transformations.",
        "category": "popular",
        "tags": ["utility", "qol", "transform"],
    },
    "animatediff": {
        "name": "AnimateDiff Evolved",
        "repo": "https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved.git",
        "description": "Animation generation framework. Create videos from image workflows.",
        "category": "popular",
        "tags": ["animation", "video", "motion"],
    },
    "ipadapter": {
        "name": "IPAdapter Plus",
        "repo": "https://github.com/cubiq/ComfyUI_IPAdapter_plus.git",
        "description": "Reference image guidance. Use images to guide generation style and content.",
        "category": "popular",
        "tags": ["ipadapter", "reference", "style"],
    },
    "controlnet-aux": {
        "name": "ControlNet Auxiliary Preprocessors",
        "repo": "https://github.com/Fannovel16/comfyui_controlnet_aux.git",
        "description": "Preprocessors for ControlNet (Canny, Depth, OpenPose, etc).",
        "category": "popular",
        "tags": ["controlnet", "preprocessor", "depth", "pose"],
    },
    "ultimate-upscale": {
        "name": "Ultimate SD Upscale",
        "repo": "https://github.com/ssitu/ComfyUI_UltimateSDUpscale.git",
        "description": "Tiled upscaling with seamless blending. Great for high-res outputs.",
        "category": "popular",
        "tags": ["upscale", "tile", "highres"],
    },

    # ===================
    # VIDEO & ANIMATION
    # ===================
    "video-helper": {
        "name": "Video Helper Suite",
        "repo": "https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git",
        "description": "Load, combine, and export videos. Essential for video workflows.",
        "category": "video",
        "tags": ["video", "export", "ffmpeg"],
    },
    "frame-interpolation": {
        "name": "Frame Interpolation",
        "repo": "https://github.com/Fannovel16/ComfyUI-Frame-Interpolation.git",
        "description": "FILM and RIFE frame interpolation for smooth video.",
        "category": "video",
        "tags": ["video", "interpolation", "smooth"],
    },

    # ===================
    # API & INTEGRATION
    # ===================
    "crystools": {
        "name": "CrysTools",
        "repo": "https://github.com/crystian/ComfyUI-Crystools.git",
        "description": "Debugging and metadata tools. Useful for workflow development.",
        "category": "api",
        "tags": ["debug", "metadata", "tools"],
    },

    # ===================
    # IMAGE PROCESSING
    # ===================
    "segment-anything": {
        "name": "Segment Anything",
        "repo": "https://github.com/storyicon/comfyui_segment_anything.git",
        "description": "SAM integration for automatic masking and segmentation.",
        "category": "image",
        "tags": ["segmentation", "mask", "sam"],
    },
    "inpaint-nodes": {
        "name": "Inpaint Nodes",
        "repo": "https://github.com/Acly/comfyui-inpaint-nodes.git",
        "description": "Advanced inpainting tools with better mask handling.",
        "category": "image",
        "tags": ["inpaint", "mask", "fill"],
    },
}


def get_nodes_by_category(category: str) -> dict:
    """Get all nodes in a specific category."""
    return {
        node_id: info
        for node_id, info in CUSTOM_NODES.items()
        if info.get("category") == category
    }


def get_essential_nodes() -> dict:
    """Get essential nodes that should always be installed."""
    return get_nodes_by_category("essential")


def get_recommended_nodes() -> dict:
    """Get recommended nodes for most users."""
    return {
        **get_nodes_by_category("essential"),
        **get_nodes_by_category("recommended"),
    }


def get_nodes_by_tag(tag: str) -> dict:
    """Get nodes that have a specific tag."""
    return {
        node_id: info
        for node_id, info in CUSTOM_NODES.items()
        if tag in info.get("tags", [])
    }


def get_all_node_ids() -> list:
    """Get list of all node IDs."""
    return list(CUSTOM_NODES.keys())


def get_node_info(node_id: str) -> dict:
    """Get info for a specific node."""
    return CUSTOM_NODES.get(node_id, {})


def get_all_categories() -> list:
    """Get list of all unique categories."""
    return list(set(info.get("category", "other") for info in CUSTOM_NODES.values()))


def get_all_tags() -> list:
    """Get list of all unique tags."""
    tags = set()
    for info in CUSTOM_NODES.values():
        tags.update(info.get("tags", []))
    return sorted(tags)
