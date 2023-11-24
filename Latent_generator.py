import torch

def generate_latents(pipe, height=512, width=512, seed = 0,generator):
    latents = None
    #Get a new random seed, store it and use it as the generator state
    if seed == 0:
        seed = generator.seed()
    
    generator = generator.manual_seed(seed)
    image_latents = torch.randn(
    (1, pipe.unet.in_channels, height // 8, width // 8),
    generator = generator,
    dtype = torch.float16,
    )
    return image_latents, seed
  
