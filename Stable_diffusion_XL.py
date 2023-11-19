import torch
from diffusers import StableDiffusionXLImg2ImgPipeline
import os.path
from diffusers import StableDiffusionXLPipeline, LCMScheduler, AutoPipelineForText2Image
from diffusers import DiffusionPipeline
from PIL import Image
from upscalers import upscale


def plot_images(image):
    import matplotlib.pyplot as plt
    plt.imshow(image)
    plt.axis("off")
    plt.show()


def generate_image(prompt,do_refine = False, do_upscale = False,negative_prompt = '',guidance_scale = 8,height=768,width=1024,n_refiner_steps = 100, n_steps = 100,type = 'xl',lcm = True):
    
    if torch.cuda.is_available():

        if type == 'dsm':
            model_id = 'stablediffusionapi/dark-sushi-mix'
            adapter_id = 'latent-consistency/lcm-lora-sdv1-5'
        elif type == 'ds':
            model_id = 'Lykon/DreamShaper'
            adapter_id = 'latent-consistency/lcm-lora-sdv1-5'
        elif type == 'rv':
            model_id = 'SG161222/Realistic_Vision_V5.1_noVAE'
            adapter_id = 'latent-consistency/lcm-lora-sdv1-5'
        elif type == 'gd':
            model_id = 'IShallRiseAgain/StudioGhibli'
            adapter_id = 'latent-consistency/lcm-lora-sdv1-5'
        elif type == 'av5':
            model_id = 'stablediffusionapi/anything-v5'
            adapter_id = 'latent-consistency/lcm-lora-sdv1-5'
        elif type == 'rvxl':
            model_id = 'SG161222/RealVisXL_V2.0'
            adapter_id = "latent-consistency/lcm-lora-sdxl"
        elif type == 'dsxl':
            model_id = "Lykon/dreamshaper-xl-1-0"
            adapter_id = "latent-consistency/lcm-lora-sdxl"
        elif type == 'ssd':
            model_id = "segmind/SSD-1B"
            adapter_id = "latent-consistency/lcm-lora-ssd-1b"
            
        else:
            model_id = "stabilityai/stable-diffusion-xl-base-1.0"
            adapter_id = "latent-consistency/lcm-lora-sdxl"

        HF_TOKEN = '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' 
        pipe = DiffusionPipeline.from_pretrained(
                model_id,
                #safety_checker = None,
                torch_dtype=torch.float16,
                use_auth_token = HF_TOKEN,
            )
        if lcm:
            n_steps = int(n_steps/10)
            guidance_scale = 1
            pipe.scheduler = LCMScheduler.from_config(pipe.scheduler.config)
            pipe.load_lora_weights(adapter_id,adapter_name = 'lcm')
            pipe.set_adapters(["lcm"],adapter_weights=[1.0])


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
        return image
    else:
        return None
