import torch
import numpy as np
import random

def generate_latents(pipe, height=512, width=512, seed = 0,generator=torch.Generator()):
    latents = None
    #Get a new random seed, store it and use it as the generator state
    if seed == 0:
        seed = generator.seed()
    torch.cuda.manual_seed(seed)
    np.random.seed(seed)
    random.seed(seed)
    torch.backends.cudnn.deterministic=True
        
    generator = generator.manual_seed(seed)
    image_latents = torch.randn(
    (1, pipe.unet.in_channels, height // 8, width // 8),
    generator = generator,
    dtype = torch.float16,
    )
    return image_latents, seed
  
