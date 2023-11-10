import torch


def generate_image(prompt,height=1024,width=768,n_refiner_steps = 100, n_steps = 100):
    if torch.cuda.is_available():
        from diffusers import StableDiffusionXLPipeline
        from diffusers import DiffusionPipeline
        from PIL import Image
        model_id = "stabilityai/stable-diffusion-xl-base-1.0"
        pipe = StableDiffusionXLPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
        pipe.enable_model_cpu_offload()

        image = pipe(prompt,height=height, width = width,num_inference_steps=n_steps).images[0]

        refiner = DiffusionPipeline.from_pretrained(
            "stabilityai/stable-diffusion-xl-refiner-1.0",
            text_encoder_2=pipe.text_encoder_2,
            vae=pipe.vae,
            torch_dtype=torch.float16,
            use_safetensors=True,
            variant="fp16",
        )

        refiner.enable_model_cpu_offload()
        high_noise_frac = 0.8
        torch.cuda.empty_cache()

        strength=0.6
        image = refiner(
            prompt,
            num_inference_steps=n_refiner_steps,
            # denoising_start=high_noise_frac,
            image=image,
        ).images[0]

        return image
    else:
        return None
