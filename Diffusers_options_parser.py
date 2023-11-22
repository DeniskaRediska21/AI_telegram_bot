#do_refine = False,
#do_upscale = False,
#negative_prompt = '',
#guidance_scale = 8,
#height=768,
#width=1024,
#n_refiner_steps = 100,
#n_steps = 100,
#type = 'xl',
#lcm = True
#VAE = 'original'
import re

DIFFUSION_MODEL_PROMPT = '''
Model name: dsm
Usecase: dark toned anime
Huggingface link: stablediffusionapi/dark-sushi-mix

Model name: ds
Usecase: fantasy
Huggingface link: Lykon/DreamShaper

Model name: rv
Usecase: realistic
Huggingface link: SG161222/Realistic_Vision_V5.1_noVAE

Model name: av5
Usecase: bright colors anime
Huggingface link: stablediffusionapi/anything-v5

Model name: cf
Usecase: all anime, interesting camera work
Huggingface link: gsdf/Counterfeit-V2.5

Model name: f2a
Usecase: flat cartoony anime
Huggingface link: jinaai/flat-2d-animerge

Model name: pm
Usecase: pastel-stialysed anime
Huggingface link: JamesFlare/pastel-mix

Model name: rvxl
Usecase: realistic, but on SDXL
Huggingface link: SG161222/RealVisXL_V2.0

Model name: dsxl
Usecase: fantasy, but on SDXL
Huggingface link: Lykon/dreamshaper-xl-1-0

Model name: ssd
Usecase: smaller footprint genaral perpose
Huggingface link: segmind/SSD-1B

Model name: sdxl
Usecase: big footprint generation perpose
Huggingface link: stabilityai/stable-diffusion-xl-base-1.0
'''


def match_True_False(line,command):
    return re.findall(f'(?<={command} )(True|False)*',line)

def match_number(line,command):
    return re.findall(f'(?<={command} )[0-9]*',line)


def match_text(line,command):
    return re.findall(f'(?<={command} )[^;]*',line)

def match_word(line,command):
    return re.findall(f'(?<={command} )[a-z0-9]*',line)

def parse_diffusion_options(current_options,message):
    line = message.text

    refine = match_True_False(line,'refine')
    upscale = match_True_False(line,'upscale')
    negative = match_text(line,'negative')
    guidance = match_number(line,'guidance')
    height = match_number(line,'height')
    width = match_number(line,'width')
    refiner_steps = match_number(line,'refiner_steps')
    steps = match_number(line,'steps')
    model = match_word(line,'model')
    vae = match_word(line,'vae')
    lcm = match_True_False(line,'lcm')

    options = [
            refine[0] == 'True' if refine else current_options[0],
            upscale[0] == 'True'  if upscale else current_options[1],
            negative[0] if negative else current_options[2],
            int(guidance[0]) if guidance else current_options[3],
            int(height[0]) if height else current_options[4],
            int(width[0]) if width else current_options[5],
            int(refiner_steps[0]) if refiner_steps else current_options[6],
            int(steps[0]) if steps else current_options[7],
            model[0] if model else current_options[8],
            lcm[0] == 'True'  if lcm else current_options[9],
            vae[0] if vae else current_options[10],
            ]
    return options




    
