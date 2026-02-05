"""
Models Registry for ComfyUI Module
Comprehensive registry of popular models with download information.
"""

# All supported model categories
MODEL_CATEGORIES = [
    "checkpoints",
    "diffusion_models",  # New models use this folder
    "vae",
    "clip",
    "text_encoders",     # Text encoders for newer models
    "loras",
    "controlnet",
    "gguf",
    "unet",
    "embeddings",
    "upscale_models",
    "clip_vision",
    "model_patches",     # For control adapters, projectors
    "latent_upscale_models",  # For video upscalers
]

# Model registry with HuggingFace repos and filenames
MODELS = {
    # ===================
    # CHECKPOINTS
    # ===================

    # Stable Diffusion 1.5 variants
    "sd15": {
        "name": "SD 1.5 (Pruned EMA - 4.3GB)",
        "repo": "runwayml/stable-diffusion-v1-5",
        "filename": "v1-5-pruned-emaonly.safetensors",
        "folder": "checkpoints",
        "size_gb": 4.27,
        "category": "sd15",
    },
    "sd15_fp16": {
        "name": "SD 1.5 (FP16 - 2.0GB)",
        "repo": "runwayml/stable-diffusion-v1-5",
        "filename": "v1-5-pruned-emaonly.fp16.safetensors",
        "folder": "checkpoints",
        "size_gb": 2.0,
        "category": "sd15",
    },
    "sd15_inpainting": {
        "name": "SD 1.5 Inpainting (4.3GB)",
        "repo": "runwayml/stable-diffusion-inpainting",
        "filename": "sd-v1-5-inpainting.ckpt",
        "folder": "checkpoints",
        "size_gb": 4.27,
        "category": "sd15",
    },

    # Stable Diffusion 2.1 variants
    "sd21": {
        "name": "SD 2.1 768 (Pruned - 5.2GB)",
        "repo": "stabilityai/stable-diffusion-2-1",
        "filename": "v2-1_768-ema-pruned.safetensors",
        "folder": "checkpoints",
        "size_gb": 5.21,
        "category": "sd21",
    },
    "sd21_base": {
        "name": "SD 2.1 Base 512 (5.2GB)",
        "repo": "stabilityai/stable-diffusion-2-1-base",
        "filename": "v2-1_512-ema-pruned.safetensors",
        "folder": "checkpoints",
        "size_gb": 5.21,
        "category": "sd21",
    },

    # SDXL - Full Precision
    "sdxl_base": {
        "name": "SDXL 1.0 Base (FP32 - 6.9GB)",
        "repo": "stabilityai/stable-diffusion-xl-base-1.0",
        "filename": "sd_xl_base_1.0.safetensors",
        "folder": "checkpoints",
        "size_gb": 6.94,
        "category": "sdxl",
    },
    "sdxl_base_fp16": {
        "name": "SDXL 1.0 Base (FP16 - 6.9GB)",
        "repo": "stabilityai/stable-diffusion-xl-base-1.0",
        "filename": "sd_xl_base_1.0_0.9vae.safetensors",
        "folder": "checkpoints",
        "size_gb": 6.94,
        "category": "sdxl",
    },
    "sdxl_refiner": {
        "name": "SDXL 1.0 Refiner (6.1GB)",
        "repo": "stabilityai/stable-diffusion-xl-refiner-1.0",
        "filename": "sd_xl_refiner_1.0.safetensors",
        "folder": "checkpoints",
        "size_gb": 6.08,
        "category": "sdxl",
    },
    "sdxl_turbo": {
        "name": "SDXL Turbo (FP16 - 6.9GB)",
        "repo": "stabilityai/sdxl-turbo",
        "filename": "sd_xl_turbo_1.0_fp16.safetensors",
        "folder": "checkpoints",
        "size_gb": 6.94,
        "category": "sdxl",
    },

    # SDXL Lightning (Fast inference - fewer steps)
    "sdxl_lightning_4step": {
        "name": "SDXL Lightning (4-step LoRA)",
        "repo": "ByteDance/SDXL-Lightning",
        "filename": "sdxl_lightning_4step_lora.safetensors",
        "folder": "loras",
        "size_gb": 0.39,
        "category": "sdxl",
    },
    "sdxl_lightning_8step": {
        "name": "SDXL Lightning (8-step LoRA)",
        "repo": "ByteDance/SDXL-Lightning",
        "filename": "sdxl_lightning_8step_lora.safetensors",
        "folder": "loras",
        "size_gb": 0.39,
        "category": "sdxl",
    },
    "sdxl_lightning_4step_unet": {
        "name": "SDXL Lightning (4-step UNet - 5.1GB)",
        "repo": "ByteDance/SDXL-Lightning",
        "filename": "sdxl_lightning_4step_unet.safetensors",
        "folder": "unet",
        "size_gb": 5.14,
        "category": "sdxl",
    },
    "sdxl_lightning_8step_unet": {
        "name": "SDXL Lightning (8-step UNet - 5.1GB)",
        "repo": "ByteDance/SDXL-Lightning",
        "filename": "sdxl_lightning_8step_unet.safetensors",
        "folder": "unet",
        "size_gb": 5.14,
        "category": "sdxl",
    },

    # SDXL Hyper (Even faster - 1-2 steps)
    "sdxl_hyper_1step_unet": {
        "name": "SDXL Hyper (1-step UNet - 5.1GB)",
        "repo": "ByteDance/Hyper-SD",
        "filename": "Hyper-SDXL-1step-Unet.safetensors",
        "folder": "unet",
        "size_gb": 5.14,
        "category": "sdxl",
    },
    "sdxl_hyper_8step_lora": {
        "name": "SDXL Hyper (8-step LoRA)",
        "repo": "ByteDance/Hyper-SD",
        "filename": "Hyper-SDXL-8steps-lora.safetensors",
        "folder": "loras",
        "size_gb": 0.79,
        "category": "sdxl",
    },

    # Flux - Full Precision
    "flux_schnell": {
        "name": "Flux.1 Schnell (BF16 - 23.8GB)",
        "repo": "black-forest-labs/FLUX.1-schnell",
        "filename": "flux1-schnell.safetensors",
        "folder": "checkpoints",
        "size_gb": 23.8,
        "category": "flux",
    },
    "flux_dev": {
        "name": "Flux.1 Dev (BF16 - 23.8GB)",
        "repo": "black-forest-labs/FLUX.1-dev",
        "filename": "flux1-dev.safetensors",
        "folder": "checkpoints",
        "size_gb": 23.8,
        "category": "flux",
    },

    # Flux - FP8 Quantized (Official Comfy)
    "flux_schnell_fp8": {
        "name": "Flux.1 Schnell (FP8 - 11.9GB)",
        "repo": "Comfy-Org/flux1-schnell",
        "filename": "flux1-schnell-fp8.safetensors",
        "folder": "checkpoints",
        "size_gb": 11.9,
        "category": "flux",
    },
    "flux_dev_fp8": {
        "name": "Flux.1 Dev (FP8 - 11.9GB)",
        "repo": "Comfy-Org/flux1-dev",
        "filename": "flux1-dev-fp8.safetensors",
        "folder": "checkpoints",
        "size_gb": 11.9,
        "category": "flux",
    },

    # Flux - GGUF Quantized (for lower VRAM)
    "flux_schnell_gguf_q8": {
        "name": "Flux.1 Schnell GGUF (Q8_0 - 12.9GB)",
        "repo": "city96/FLUX.1-schnell-gguf",
        "filename": "flux1-schnell-Q8_0.gguf",
        "folder": "gguf",
        "size_gb": 12.9,
        "category": "flux",
    },
    "flux_schnell_gguf_q5": {
        "name": "Flux.1 Schnell GGUF (Q5_K_S - 8.5GB)",
        "repo": "city96/FLUX.1-schnell-gguf",
        "filename": "flux1-schnell-Q5_K_S.gguf",
        "folder": "gguf",
        "size_gb": 8.5,
        "category": "flux",
    },
    "flux_schnell_gguf_q4": {
        "name": "Flux.1 Schnell GGUF (Q4_K_S - 7.0GB)",
        "repo": "city96/FLUX.1-schnell-gguf",
        "filename": "flux1-schnell-Q4_K_S.gguf",
        "folder": "gguf",
        "size_gb": 7.0,
        "category": "flux",
    },
    "flux_dev_gguf_q8": {
        "name": "Flux.1 Dev GGUF (Q8_0 - 12.9GB)",
        "repo": "city96/FLUX.1-dev-gguf",
        "filename": "flux1-dev-Q8_0.gguf",
        "folder": "gguf",
        "size_gb": 12.9,
        "category": "flux",
    },
    "flux_dev_gguf_q5": {
        "name": "Flux.1 Dev GGUF (Q5_K_S - 8.5GB)",
        "repo": "city96/FLUX.1-dev-gguf",
        "filename": "flux1-dev-Q5_K_S.gguf",
        "folder": "gguf",
        "size_gb": 8.5,
        "category": "flux",
    },
    "flux_dev_gguf_q4": {
        "name": "Flux.1 Dev GGUF (Q4_K_S - 7.0GB)",
        "repo": "city96/FLUX.1-dev-gguf",
        "filename": "flux1-dev-Q4_K_S.gguf",
        "folder": "gguf",
        "size_gb": 7.0,
        "category": "flux",
    },

    # Stable Diffusion 3 / 3.5
    "sd3_medium": {
        "name": "SD3 Medium (4.3GB)",
        "repo": "stabilityai/stable-diffusion-3-medium",
        "filename": "sd3_medium.safetensors",
        "folder": "checkpoints",
        "size_gb": 4.34,
        "category": "sd3",
    },
    "sd3_medium_incl_clips": {
        "name": "SD3 Medium w/ CLIP (5.9GB)",
        "repo": "stabilityai/stable-diffusion-3-medium",
        "filename": "sd3_medium_incl_clips.safetensors",
        "folder": "checkpoints",
        "size_gb": 5.94,
        "category": "sd3",
    },
    "sd3_medium_incl_clips_t5": {
        "name": "SD3 Medium w/ CLIP+T5 (15.7GB)",
        "repo": "stabilityai/stable-diffusion-3-medium",
        "filename": "sd3_medium_incl_clips_t5xxlfp16.safetensors",
        "folder": "checkpoints",
        "size_gb": 15.73,
        "category": "sd3",
    },
    "sd35_medium": {
        "name": "SD 3.5 Medium (5.4GB)",
        "repo": "stabilityai/stable-diffusion-3.5-medium",
        "filename": "sd3.5_medium.safetensors",
        "folder": "checkpoints",
        "size_gb": 5.4,
        "category": "sd3",
    },
    "sd35_large": {
        "name": "SD 3.5 Large (8.9GB)",
        "repo": "stabilityai/stable-diffusion-3.5-large",
        "filename": "sd3.5_large.safetensors",
        "folder": "checkpoints",
        "size_gb": 8.9,
        "category": "sd3",
    },
    "sd35_large_turbo": {
        "name": "SD 3.5 Large Turbo (8.9GB)",
        "repo": "stabilityai/stable-diffusion-3.5-large-turbo",
        "filename": "sd3.5_large_turbo.safetensors",
        "folder": "checkpoints",
        "size_gb": 8.9,
        "category": "sd3",
    },

    # Video Models - LTX Video 1.x
    "ltx_video": {
        "name": "LTX Video 2B v0.9.5",
        "repo": "Lightricks/LTX-Video",
        "filename": "ltx-video-2b-v0.9.5.safetensors",
        "folder": "checkpoints",
        "size_gb": 9.37,
        "category": "video",
    },
    "svd": {
        "name": "Stable Video Diffusion",
        "repo": "stabilityai/stable-video-diffusion-img2vid-xt",
        "filename": "svd_xt.safetensors",
        "folder": "checkpoints",
        "size_gb": 9.56,
        "category": "video",
    },

    # ===================
    # LTX-2 (Video - New Default Templates)
    # ===================
    "ltx2_19b_dev": {
        "name": "LTX-2 19B Dev (Full)",
        "repo": "Lightricks/LTX-2",
        "filename": "ltx-2-19b-dev.safetensors",
        "folder": "checkpoints",
        "size_gb": 19.0,
        "category": "ltx2",
    },
    "ltx2_19b_dev_fp8": {
        "name": "LTX-2 19B Dev (FP8 - 9.5GB)",
        "repo": "Lightricks/LTX-2",
        "filename": "ltx-2-19b-dev-fp8.safetensors",
        "folder": "checkpoints",
        "size_gb": 9.5,
        "category": "ltx2",
    },
    "ltx2_19b_distilled": {
        "name": "LTX-2 19B Distilled (Full)",
        "repo": "Lightricks/LTX-2",
        "filename": "ltx-2-19b-distilled.safetensors",
        "folder": "checkpoints",
        "size_gb": 19.0,
        "category": "ltx2",
    },
    "ltx2_19b_distilled_fp8": {
        "name": "LTX-2 19B Distilled (FP8 - 9.5GB)",
        "repo": "Lightricks/LTX-2",
        "filename": "ltx-2-19b-distilled-fp8.safetensors",
        "folder": "checkpoints",
        "size_gb": 9.5,
        "category": "ltx2",
    },
    "ltx2_distilled_lora": {
        "name": "LTX-2 Distilled LoRA",
        "repo": "Lightricks/LTX-2",
        "filename": "ltx-2-19b-distilled-lora-384.safetensors",
        "folder": "loras",
        "size_gb": 0.38,
        "category": "ltx2",
    },
    "ltx2_upscaler": {
        "name": "LTX-2 Spatial Upscaler x2",
        "repo": "Lightricks/LTX-2",
        "filename": "ltx-2-spatial-upscaler-x2-1.0.safetensors",
        "folder": "latent_upscale_models",
        "size_gb": 0.15,
        "category": "ltx2",
    },
    "ltx2_text_encoder": {
        "name": "LTX-2 Gemma 12B (FP4 Mixed)",
        "repo": "Comfy-Org/ltx-2",
        "filename": "split_files/text_encoders/gemma_3_12B_it_fp4_mixed.safetensors",
        "folder": "text_encoders",
        "size_gb": 6.0,
        "category": "ltx2",
    },
    "ltx2_canny_lora": {
        "name": "LTX-2 Canny Control LoRA",
        "repo": "Lightricks/LTX-2-19b-IC-LoRA-Canny-Control",
        "filename": "ltx-2-19b-ic-lora-canny-control.safetensors",
        "folder": "loras",
        "size_gb": 0.38,
        "category": "ltx2",
    },
    "ltx2_depth_lora": {
        "name": "LTX-2 Depth Control LoRA",
        "repo": "Lightricks/LTX-2-19b-IC-LoRA-Depth-Control",
        "filename": "ltx-2-19b-ic-lora-depth-control.safetensors",
        "folder": "loras",
        "size_gb": 0.38,
        "category": "ltx2",
    },

    # ===================
    # FLUX 2 (Image - New Default Templates)
    # ===================
    "flux2_dev_fp8": {
        "name": "Flux 2 Dev (FP8 Mixed)",
        "repo": "Comfy-Org/flux2-dev",
        "filename": "split_files/diffusion_models/flux2_dev_fp8mixed.safetensors",
        "folder": "diffusion_models",
        "size_gb": 12.0,
        "category": "flux2",
    },
    "flux2_vae": {
        "name": "Flux 2 VAE",
        "repo": "Comfy-Org/flux2-dev",
        "filename": "split_files/vae/flux2-vae.safetensors",
        "folder": "vae",
        "size_gb": 0.17,
        "category": "flux2",
    },
    "flux2_text_encoder_fp8": {
        "name": "Flux 2 Mistral 3 Small (FP8)",
        "repo": "Comfy-Org/flux2-dev",
        "filename": "split_files/text_encoders/mistral_3_small_flux2_fp8.safetensors",
        "folder": "text_encoders",
        "size_gb": 12.0,
        "category": "flux2",
    },
    "flux2_text_encoder_bf16": {
        "name": "Flux 2 Mistral 3 Small (BF16)",
        "repo": "Comfy-Org/flux2-dev",
        "filename": "split_files/text_encoders/mistral_3_small_flux2_bf16.safetensors",
        "folder": "text_encoders",
        "size_gb": 24.0,
        "category": "flux2",
    },
    "flux2_turbo_lora": {
        "name": "Flux 2 Turbo LoRA",
        "repo": "Comfy-Org/flux2-dev",
        "filename": "split_files/loras/Flux2TurboComfyv2.safetensors",
        "folder": "loras",
        "size_gb": 0.4,
        "category": "flux2",
    },
    "flux2_klein_4b": {
        "name": "Flux 2 Klein 4B",
        "repo": "Comfy-Org/flux2-klein",
        "filename": "split_files/diffusion_models/flux-2-klein-4b.safetensors",
        "folder": "diffusion_models",
        "size_gb": 4.0,
        "category": "flux2",
    },
    "flux2_klein_4b_fp8": {
        "name": "Flux 2 Klein 4B (FP8)",
        "repo": "black-forest-labs/FLUX.2-klein-4b-fp8",
        "filename": "flux-2-klein-4b-fp8.safetensors",
        "folder": "checkpoints",
        "size_gb": 4.0,
        "category": "flux2",
    },
    "flux2_klein_qwen_text": {
        "name": "Flux 2 Klein Qwen 3 4B Text Encoder",
        "repo": "Comfy-Org/flux2-klein",
        "filename": "split_files/text_encoders/qwen_3_4b.safetensors",
        "folder": "text_encoders",
        "size_gb": 4.0,
        "category": "flux2",
    },

    # ===================
    # QWEN IMAGE (New Default Templates)
    # ===================
    "qwen_image_fp8": {
        "name": "Qwen Image 2512 (FP8)",
        "repo": "Comfy-Org/Qwen-Image_ComfyUI",
        "filename": "split_files/diffusion_models/qwen_image_2512_fp8_e4m3fn.safetensors",
        "folder": "diffusion_models",
        "size_gb": 6.0,
        "category": "qwen",
    },
    "qwen_image_vae": {
        "name": "Qwen Image VAE",
        "repo": "Comfy-Org/Qwen-Image_ComfyUI",
        "filename": "split_files/vae/qwen_image_vae.safetensors",
        "folder": "vae",
        "size_gb": 0.17,
        "category": "qwen",
    },
    "qwen_image_text_encoder": {
        "name": "Qwen 2.5 VL 7B (FP8)",
        "repo": "Comfy-Org/Qwen-Image_ComfyUI",
        "filename": "split_files/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors",
        "folder": "text_encoders",
        "size_gb": 7.5,
        "category": "qwen",
    },
    "qwen_image_edit_fp8": {
        "name": "Qwen Image Edit 2511 (FP8)",
        "repo": "Comfy-Org/Qwen-Image-Edit_ComfyUI",
        "filename": "split_files/diffusion_models/qwen_image_edit_fp8_e4m3fn.safetensors",
        "folder": "diffusion_models",
        "size_gb": 6.0,
        "category": "qwen",
    },
    "qwen_image_edit_bf16": {
        "name": "Qwen Image Edit 2511 (BF16)",
        "repo": "Comfy-Org/Qwen-Image-Edit_ComfyUI",
        "filename": "split_files/diffusion_models/qwen_image_edit_2511_bf16.safetensors",
        "folder": "diffusion_models",
        "size_gb": 12.0,
        "category": "qwen",
    },
    "qwen_image_lightning_4step": {
        "name": "Qwen Image Lightning (4-step)",
        "repo": "lightx2v/Qwen-Image-Lightning",
        "filename": "Qwen-Image-Lightning-4steps-V1.0.safetensors",
        "folder": "loras",
        "size_gb": 0.8,
        "category": "qwen",
    },
    "qwen_image_controlnet_union": {
        "name": "Qwen Image ControlNet Union",
        "repo": "Comfy-Org/Qwen-Image-InstantX-ControlNets",
        "filename": "split_files/controlnet/Qwen-Image-InstantX-ControlNet-Union.safetensors",
        "folder": "controlnet",
        "size_gb": 1.5,
        "category": "qwen",
    },

    # ===================
    # HUNYUAN VIDEO 1.5 (New Default Templates)
    # ===================
    "hunyuan_video_15_i2v": {
        "name": "HunyuanVideo 1.5 720p I2V (FP16)",
        "repo": "Comfy-Org/HunyuanVideo_1.5_repackaged",
        "filename": "split_files/diffusion_models/hunyuanvideo1.5_720p_i2v_fp16.safetensors",
        "folder": "diffusion_models",
        "size_gb": 12.0,
        "category": "hunyuan",
    },
    "hunyuan_video_15_vae": {
        "name": "HunyuanVideo 1.5 VAE (FP16)",
        "repo": "Comfy-Org/HunyuanVideo_1.5_repackaged",
        "filename": "split_files/vae/hunyuanvideo15_vae_fp16.safetensors",
        "folder": "vae",
        "size_gb": 0.5,
        "category": "hunyuan",
    },
    "hunyuan_video_15_upscaler": {
        "name": "HunyuanVideo 1.5 1080p Upscaler",
        "repo": "Comfy-Org/HunyuanVideo_1.5_repackaged",
        "filename": "split_files/diffusion_models/hunyuanvideo1.5_1080p_sr_distilled_fp16.safetensors",
        "folder": "diffusion_models",
        "size_gb": 3.0,
        "category": "hunyuan",
    },
    "hunyuan_video_text_encoder": {
        "name": "Qwen 2.5 VL 7B (FP8) - for HunyuanVideo",
        "repo": "Comfy-Org/HunyuanVideo_1.5_repackaged",
        "filename": "split_files/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors",
        "folder": "text_encoders",
        "size_gb": 7.5,
        "category": "hunyuan",
    },

    # ===================
    # WAN 2.1 (Video - New Default Templates)
    # ===================
    "wan21_i2v_14b_fp8": {
        "name": "Wan 2.1 I2V 14B 480p (FP8)",
        "repo": "Kijai/WanVideo_comfy_fp8_scaled",
        "filename": "I2V/Wan2_1-I2V-14B-480p_fp8_e4m3fn_scaled_KJ.safetensors",
        "folder": "diffusion_models",
        "size_gb": 14.0,
        "category": "wan",
    },
    "wan21_vae": {
        "name": "Wan 2.1 VAE (BF16)",
        "repo": "Kijai/WanVideo_comfy",
        "filename": "Wan2_1_VAE_bf16.safetensors",
        "folder": "vae",
        "size_gb": 0.5,
        "category": "wan",
    },
    "wan21_text_encoder": {
        "name": "UMT5-XXL (FP8) - for Wan",
        "repo": "Comfy-Org/Wan_2.1_ComfyUI_repackaged",
        "filename": "split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors",
        "folder": "text_encoders",
        "size_gb": 5.0,
        "category": "wan",
    },

    # ===================
    # Z-IMAGE TURBO (New Default Templates)
    # ===================
    "z_image_turbo": {
        "name": "Z-Image Turbo (BF16)",
        "repo": "Comfy-Org/z_image_turbo",
        "filename": "split_files/diffusion_models/z_image_turbo_bf16.safetensors",
        "folder": "diffusion_models",
        "size_gb": 4.5,
        "category": "z_image",
    },
    "z_image_turbo_vae": {
        "name": "Z-Image Turbo VAE",
        "repo": "Comfy-Org/z_image_turbo",
        "filename": "split_files/vae/ae.safetensors",
        "folder": "vae",
        "size_gb": 0.17,
        "category": "z_image",
    },
    "z_image_turbo_text_encoder": {
        "name": "Qwen 3 4B Text Encoder (for Z-Image)",
        "repo": "Comfy-Org/z_image_turbo",
        "filename": "split_files/text_encoders/qwen_3_4b.safetensors",
        "folder": "text_encoders",
        "size_gb": 4.0,
        "category": "z_image",
    },
    "z_image_turbo_controlnet": {
        "name": "Z-Image Turbo ControlNet Union",
        "repo": "alibaba-pai/Z-Image-Turbo-Fun-Controlnet-Union",
        "filename": "Z-Image-Turbo-Fun-Controlnet-Union.safetensors",
        "folder": "controlnet",
        "size_gb": 1.5,
        "category": "z_image",
    },

    # ===================
    # HIDREAM (New Default Templates)
    # ===================
    "hidream_i1_fp8": {
        "name": "HiDream I1 Full (FP8)",
        "repo": "Comfy-Org/HiDream-I1_ComfyUI",
        "filename": "split_files/diffusion_models/hidream_i1_full_fp8.safetensors",
        "folder": "diffusion_models",
        "size_gb": 8.0,
        "category": "hidream",
    },
    "hidream_e1_bf16": {
        "name": "HiDream E1 Full (BF16)",
        "repo": "Comfy-Org/HiDream-I1_ComfyUI",
        "filename": "split_files/diffusion_models/hidream_e1_full_bf16.safetensors",
        "folder": "diffusion_models",
        "size_gb": 16.0,
        "category": "hidream",
    },
    "hidream_clip_l": {
        "name": "HiDream CLIP-L",
        "repo": "Comfy-Org/HiDream-I1_ComfyUI",
        "filename": "split_files/text_encoders/clip_l_hidream.safetensors",
        "folder": "text_encoders",
        "size_gb": 0.25,
        "category": "hidream",
    },
    "hidream_clip_g": {
        "name": "HiDream CLIP-G",
        "repo": "Comfy-Org/HiDream-I1_ComfyUI",
        "filename": "split_files/text_encoders/clip_g_hidream.safetensors",
        "folder": "text_encoders",
        "size_gb": 1.4,
        "category": "hidream",
    },

    # ===================
    # KANDINSKY 5 (Video - New Default Templates)
    # ===================
    "kandinsky5_t2v": {
        "name": "Kandinsky 5 Lite T2V 5s",
        "repo": "kandinskylab/Kandinsky-5.0-T2V-Lite-sft-5s",
        "filename": "model/kandinsky5lite_t2v_sft_5s.safetensors",
        "folder": "diffusion_models",
        "size_gb": 5.0,
        "category": "kandinsky",
    },
    "kandinsky5_i2v": {
        "name": "Kandinsky 5 Lite I2V 5s",
        "repo": "kandinskylab/Kandinsky-5.0-I2V-Lite-5s",
        "filename": "model/kandinsky5lite_i2v_5s.safetensors",
        "folder": "diffusion_models",
        "size_gb": 5.0,
        "category": "kandinsky",
    },

    # ===================
    # CHROMA (Image - New Default Templates)
    # ===================
    "chroma_hd_fp8": {
        "name": "Chroma 1 HD (FP8 Mixed)",
        "repo": "Comfy-Org/Chroma1-HD_repackaged",
        "filename": "split_files/diffusion_models/Chroma1-HD-fp8mixed.safetensors",
        "folder": "diffusion_models",
        "size_gb": 6.0,
        "category": "chroma",
    },
    "chroma_radiance": {
        "name": "Chroma 1 Radiance",
        "repo": "Comfy-Org/Chroma1-Radiance_Repackaged",
        "filename": "split_files/diffusion_models/chroma-radiance-x0.safetensors",
        "folder": "diffusion_models",
        "size_gb": 12.0,
        "category": "chroma",
    },

    # ===================
    # VAE
    # ===================
    "sdxl_vae": {
        "name": "SDXL VAE (335MB)",
        "repo": "stabilityai/sdxl-vae",
        "filename": "sdxl_vae.safetensors",
        "folder": "vae",
        "size_gb": 0.33,
        "category": "sdxl",
    },
    "sdxl_vae_fp16": {
        "name": "SDXL VAE FP16 Fix (335MB)",
        "repo": "madebyollin/sdxl-vae-fp16-fix",
        "filename": "sdxl_vae.safetensors",
        "folder": "vae",
        "size_gb": 0.33,
        "category": "sdxl",
    },
    "sd_vae_ft_mse": {
        "name": "SD VAE ft-mse (335MB)",
        "repo": "stabilityai/sd-vae-ft-mse",
        "filename": "diffusion_pytorch_model.safetensors",
        "folder": "vae",
        "size_gb": 0.33,
        "category": "sd15",
    },
    "sd_vae_ft_ema": {
        "name": "SD VAE ft-ema (335MB)",
        "repo": "stabilityai/sd-vae-ft-ema",
        "filename": "diffusion_pytorch_model.safetensors",
        "folder": "vae",
        "size_gb": 0.33,
        "category": "sd15",
    },

    # Flux VAE (required for Flux models)
    "flux_vae": {
        "name": "Flux VAE (168MB)",
        "repo": "black-forest-labs/FLUX.1-schnell",
        "filename": "ae.safetensors",
        "folder": "vae",
        "size_gb": 0.168,
        "category": "flux",
    },

    # ===================
    # CLIP / Text Encoders
    # ===================
    "clip_vit_l": {
        "name": "CLIP ViT-L/14 (SD1.5/SDXL)",
        "repo": "openai/clip-vit-large-patch14",
        "filename": "model.safetensors",
        "folder": "clip",
        "size_gb": 0.89,
        "category": "clip",
    },
    "clip_vit_h": {
        "name": "CLIP ViT-H/14 (SDXL)",
        "repo": "laion/CLIP-ViT-H-14-laion2B-s32B-b79K",
        "filename": "open_clip_pytorch_model.safetensors",
        "folder": "clip",
        "size_gb": 3.94,
        "category": "clip",
    },

    # Flux Text Encoders (both needed for Flux)
    "flux_clip_l": {
        "name": "Flux CLIP-L Text Encoder",
        "repo": "comfyanonymous/flux_text_encoders",
        "filename": "clip_l.safetensors",
        "folder": "clip",
        "size_gb": 0.25,
        "category": "flux",
    },
    "flux_t5xxl": {
        "name": "Flux T5-XXL Text Encoder (FP16 - 9.8GB)",
        "repo": "comfyanonymous/flux_text_encoders",
        "filename": "t5xxl_fp16.safetensors",
        "folder": "clip",
        "size_gb": 9.79,
        "category": "flux",
    },
    "flux_t5xxl_fp8": {
        "name": "Flux T5-XXL Text Encoder (FP8 - 4.9GB)",
        "repo": "comfyanonymous/flux_text_encoders",
        "filename": "t5xxl_fp8_e4m3fn.safetensors",
        "folder": "clip",
        "size_gb": 4.89,
        "category": "flux",
    },
    "flux_t5xxl_gguf_q8": {
        "name": "Flux T5-XXL GGUF (Q8_0 - 5.2GB)",
        "repo": "city96/t5-v1_1-xxl-encoder-gguf",
        "filename": "t5-v1_1-xxl-encoder-Q8_0.gguf",
        "folder": "clip",
        "size_gb": 5.2,
        "category": "flux",
    },
    "flux_t5xxl_gguf_q4": {
        "name": "Flux T5-XXL GGUF (Q4_K_S - 2.8GB)",
        "repo": "city96/t5-v1_1-xxl-encoder-gguf",
        "filename": "t5-v1_1-xxl-encoder-Q4_K_S.gguf",
        "folder": "clip",
        "size_gb": 2.8,
        "category": "flux",
    },

    # SD3 Text Encoders
    "sd3_clip_g": {
        "name": "SD3 CLIP-G Text Encoder",
        "repo": "stabilityai/stable-diffusion-3-medium",
        "filename": "text_encoders/clip_g.safetensors",
        "subfolder": "text_encoders",
        "folder": "clip",
        "size_gb": 1.39,
        "category": "sd3",
    },
    "sd3_clip_l": {
        "name": "SD3 CLIP-L Text Encoder",
        "repo": "stabilityai/stable-diffusion-3-medium",
        "filename": "text_encoders/clip_l.safetensors",
        "subfolder": "text_encoders",
        "folder": "clip",
        "size_gb": 0.25,
        "category": "sd3",
    },
    "sd3_t5xxl": {
        "name": "SD3 T5-XXL Text Encoder (FP16)",
        "repo": "stabilityai/stable-diffusion-3-medium",
        "filename": "text_encoders/t5xxl_fp16.safetensors",
        "subfolder": "text_encoders",
        "folder": "clip",
        "size_gb": 9.79,
        "category": "sd3",
    },

    # ===================
    # CONTROLNET
    # ===================
    "controlnet_canny_sd15": {
        "name": "ControlNet Canny (SD1.5)",
        "repo": "lllyasviel/control_v11p_sd15_canny",
        "filename": "diffusion_pytorch_model.safetensors",
        "folder": "controlnet",
        "size_gb": 1.45,
        "category": "sd15",
    },
    "controlnet_depth_sd15": {
        "name": "ControlNet Depth (SD1.5)",
        "repo": "lllyasviel/control_v11f1p_sd15_depth",
        "filename": "diffusion_pytorch_model.safetensors",
        "folder": "controlnet",
        "size_gb": 1.45,
        "category": "sd15",
    },
    "controlnet_openpose_sd15": {
        "name": "ControlNet OpenPose (SD1.5)",
        "repo": "lllyasviel/control_v11p_sd15_openpose",
        "filename": "diffusion_pytorch_model.safetensors",
        "folder": "controlnet",
        "size_gb": 1.45,
        "category": "sd15",
    },
    "controlnet_canny_sdxl": {
        "name": "ControlNet Canny (SDXL)",
        "repo": "diffusers/controlnet-canny-sdxl-1.0",
        "filename": "diffusion_pytorch_model.safetensors",
        "folder": "controlnet",
        "size_gb": 2.50,
        "category": "sdxl",
    },
    "controlnet_depth_sdxl": {
        "name": "ControlNet Depth (SDXL)",
        "repo": "diffusers/controlnet-depth-sdxl-1.0",
        "filename": "diffusion_pytorch_model.safetensors",
        "folder": "controlnet",
        "size_gb": 2.50,
        "category": "sdxl",
    },

    # ===================
    # UPSCALE MODELS
    # ===================
    "realesrgan_x4": {
        "name": "RealESRGAN x4plus",
        "repo": "ai-forever/Real-ESRGAN",
        "filename": "RealESRGAN_x4.pth",
        "folder": "upscale_models",
        "size_gb": 0.064,
        "category": "upscale",
    },
    "4x_ultrasharp": {
        "name": "4x UltraSharp",
        "url": "https://huggingface.co/Kim2091/UltraSharp/resolve/main/4x-UltraSharp.pth",
        "filename": "4x-UltraSharp.pth",
        "folder": "upscale_models",
        "size_gb": 0.067,
        "category": "upscale",
    },

    # ===================
    # CLIP VISION
    # ===================
    "clip_vision_vit_h": {
        "name": "CLIP Vision ViT-H",
        "repo": "h94/IP-Adapter",
        "filename": "models/image_encoder/model.safetensors",
        "subfolder": "models/image_encoder",
        "folder": "clip_vision",
        "size_gb": 2.53,
        "category": "ipadapter",
    },

    # ===================
    # EMBEDDINGS (Textual Inversions)
    # ===================
    "easynegative": {
        "name": "EasyNegative",
        "repo": "gsdf/EasyNegative",
        "filename": "EasyNegative.safetensors",
        "folder": "embeddings",
        "size_gb": 0.024,
        "category": "embedding",
    },
    "badhandv4": {
        "name": "BadHand v4",
        "url": "https://civitai.com/api/download/models/20068",
        "filename": "badhandv4.pt",
        "folder": "embeddings",
        "size_gb": 0.035,
        "category": "embedding",
    },
}

# HuggingFace search patterns for auto-discovery
HF_SEARCH_PATTERNS = {
    "checkpoints": [
        "stable-diffusion",
        "sdxl",
        "flux",
        "checkpoint",
        "diffusion",
    ],
    "loras": [
        "lora",
        "loha",
        "lokr",
        "lycoris",
    ],
    "vae": [
        "vae",
        "variational-autoencoder",
    ],
    "controlnet": [
        "controlnet",
        "control_v",
        "control-net",
    ],
    "embeddings": [
        "embedding",
        "textual-inversion",
        "ti",
    ],
    "upscale_models": [
        "esrgan",
        "upscale",
        "super-resolution",
    ],
    "clip_vision": [
        "clip-vision",
        "image-encoder",
    ],
}

# Popular LoRA sources (for search guidance)
LORA_SOURCES = {
    "civitai": "https://civitai.com/models",
    "huggingface": "https://huggingface.co/models?other=lora",
}


def get_models_by_category(category: str) -> dict:
    """Get all models in a specific category folder."""
    return {
        model_id: info
        for model_id, info in MODELS.items()
        if info.get("folder") == category
    }


def get_models_by_model_category(model_category: str) -> dict:
    """Get all models by their model category (sd15, sdxl, flux, etc)."""
    return {
        model_id: info
        for model_id, info in MODELS.items()
        if info.get("category") == model_category
    }


def get_all_model_ids() -> list:
    """Get list of all model IDs."""
    return list(MODELS.keys())


def get_model_info(model_id: str) -> dict:
    """Get info for a specific model."""
    return MODELS.get(model_id, {})
