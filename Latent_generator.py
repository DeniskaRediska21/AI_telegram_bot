import torch

def generate_latents(pipe, height=512, width=512, seed = 0,generator=torch.Generator()):
    latents = None
    #Get a new random seed, store it and use it as the generator state
    if seed == 0:
        seed = generator.seed()
    torch.cuda.manual_seed(seed)
    torch.backends.cudnn.deterministic=True
        
    generator = generator.manual_seed(seed)
    image_latents = torch.randn(
    (1, pipe.unet.config.in_channels, height // 8, width // 8),
    generator = generator,
    dtype = torch.float16,
    )
    return image_latents, seed
  
