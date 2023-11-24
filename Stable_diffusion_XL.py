import torch

def plot_images(image):
    import matplotlib.pyplot as plt
    plt.imshow(image)
    plt.axis("off")
    plt.show()


def make_divisible_by_eight(number):
    remainder = number % 8
    if remainder != 0:
        number += 8 - remainder
    return number

    
def generate_image(prompt,do_refine = False, do_upscale = False,negative_prompt = '',guidance_scale = 8,height=768,width=1024,n_refiner_steps = 100, n_steps = 100,type = 'xl',lcm = True,VAE = 'original',seed = 0):
    width = make_divisible_by_eight(width)
    height = make_divisible_by_eight(height)
    
    if torch.cuda.is_available():
        import Latent_generator
        from diffusers import StableDiffusionXLImg2ImgPipeline
        import os.path
        from diffusers import StableDiffusionXLPipeline, LCMScheduler, AutoPipelineForText2Image
        from diffusers import DiffusionPipeline, AutoencoderKL
        from PIL import Image
        from upscalers import upscale
        import config
        if type == 'dsm':
            model_id = 'stablediffusionapi/dark-sushi-mix'
            adapter_id = 'latent-consistency/lcm-lora-sdv1-5'
            vae = AutoencoderKL.from_pretrained('stablediffusionapi/dark-sushi-mix',subfolder = 'vae',torch_dtype=torch.float16)
        if type == 'om':
            model_id = 'WarriorMama777/BloodOrangeMix'
            adapter_id = 'latent-consistency/lcm-lora-sdv1-5'
            vae = AutoencoderKL.from_pretrained('WarriorMama777/BloodOrangeMix',subfolder = 'vae',torch_dtype=torch.float16)
        elif type == 'ds':
            model_id = 'Lykon/DreamShaper'
            adapter_id = 'latent-consistency/lcm-lora-sdv1-5'
            vae = AutoencoderKL.from_pretrained('Lykon/DreamShaper',subfolder = 'vae',torch_dtype=torch.float16)
        elif type == 'rv':
            model_id = 'stablediffusionapi/realistic-vision-v51'
            adapter_id = 'latent-consistency/lcm-lora-sdv1-5'
            vae = AutoencoderKL.from_pretrained('stablediffusionapi/realistic-vision-v51',subfolder = 'vae',torch_dtype=torch.float16)
        elif type == 'av5':
            model_id = 'stablediffusionapi/anything-v5'
            adapter_id = 'latent-consistency/lcm-lora-sdv1-5'
            vae = AutoencoderKL.from_pretrained('stablediffusionapi/anything-v5',subfolder = 'vae',torch_dtype=torch.float16)
        elif type == 'cf':
            model_id = 'gsdf/Counterfeit-V2.5'
            adapter_id = 'latent-consistency/lcm-lora-sdv1-5'
            vae = AutoencoderKL.from_pretrained('gsdf/Counterfeit-V2.5',subfolder = 'vae',torch_dtype=torch.float16)
        elif type == 'f2a':
            model_id = 'jinaai/flat-2d-animerge'
            adapter_id = 'latent-consistency/lcm-lora-sdv1-5'
            vae = AutoencoderKL.from_pretrained('jinaai/flat-2d-animerge',subfolder = 'vae',torch_dtype=torch.float16)
        elif type == 'pm':
            model_id = 'JamesFlare/pastel-mix'
            adapter_id = 'latent-consistency/lcm-lora-sdv1-5'
            vae = AutoencoderKL.from_pretrained('JamesFlare/pastel-mix',subfolder = 'vae',torch_dtype=torch.float16)
        elif type == 'rvxl':
            model_id = 'SG161222/RealVisXL_V2.0'
            adapter_id = "latent-consistency/lcm-lora-sdxl"
            vae = AutoencoderKL.from_pretrained('SG161222/RealVisXL_V2.0',subfolder = 'vae',torch_dtype=torch.float16)
        elif type == 'dsxl':
            model_id = "Lykon/dreamshaper-xl-1-0"
            adapter_id = "latent-consistency/lcm-lora-sdxl"
            vae = AutoencoderKL.from_pretrained('Lykon/dreamshaper-xl-1-0',subfolder = 'vae',torch_dtype=torch.float16)
        elif type == 'ssd':
            model_id = "segmind/SSD-1B"
            adapter_id = "latent-consistency/lcm-lora-ssd-1b"
            vae = AutoencoderKL.from_pretrained('segmind/SSD-1B',subfolder = 'vae',torch_dtype=torch.float16)
            
        else:
            model_id = "stabilityai/stable-diffusion-xl-base-1.0"
            adapter_id = "latent-consistency/lcm-lora-sdxl"
            VAE = 'none'

        pipe = DiffusionPipeline.from_pretrained(
                model_id,
                #safety_checker = None,
                torch_dtype=torch.float16,
                use_auth_token = config.HF_TOKEN,
            )
        if lcm:
            n_steps = int(n_steps/10)
            guidance_scale = 1
            pipe.scheduler = LCMScheduler.from_config(pipe.scheduler.config)
            pipe.load_lora_weights(adapter_id,adapter_name = 'lcm')
            pipe.set_adapters(["lcm"],adapter_weights=[1.0])

        if VAE != 'original':
            if VAE == 'mse': 
                vae = AutoencoderKL.from_pretrained("stabilityai/sd-vae-ft-mse",torch_dtype=torch.float16)
            elif VAE == 'ema':
                vae = AutoencoderKL.from_pretrained("stabilityai/sd-vae-ft-ema",torch_dtype=torch.float16)
            elif VAE == 'none':
                vae = pipe.vae
        pipe.vae = vae
        latents,seed = Latent_generator.generate_latents(pipe,height,width,seed)
        pipe.enable_model_cpu_offload()
        #pipe.unet = torch.compile(pipe.unet, mode = 'max-autotune',fullgraph=True)

#        pipe = deepspeed.init_inference(
#            model = getattr(pipe,"model",pipe),
#            replace_with_kernel_inject = False,
#        )

            
        #pipe.vae = AutoencoderTiny.from_pretrained("madebyollin/taesdxl",torch_dtype = torch.float16)

        with torch.inference_mode():
            image = pipe(
                prompt,
                height=height,
                width = width,
                num_inference_steps=n_steps,
                guidance_scale = guidance_scale,
                latents = latents,
                negative_prompt = negative_prompt,
            ).images[0]
            if do_refine:
                refiner = StableDiffusionXLImg2ImgPipeline.from_pretrained(
                    "stabilityai/stable-diffusion-xl-refiner-1.0", torch_dtype=torch.float16, variant="fp16", use_safetensors=True
                )
                refiner.enable_model_cpu_offload()
                torch.cuda.empty_cache()
                image = refiner(
                   prompt,
                   num_inference_steps=n_refiner_steps,
                   image=image,
                ).images[0]
            if do_upscale:
                image = upscale('R-ESRGAN General 4xV3', image, 1.5)
        return image, seed
    else:
        return None
