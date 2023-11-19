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
import re

def match_True_False(line,command):
    return re.findall(f'(?<={command} )(True|False)*',line)

def match_number(line,command):
    return re.findall(f'(?<={command} )[0-9]*',line)


def match_text(line,command):
    return re.findall(f'(?<={command} )[^;]*',line)

def match_word(line,command):
    return re.findall(f'(?<={command} )[a-z]*',line)

def parse_diffusion_options(diffusion_options,message):
    line = message.text
    if message.from_user.id in diffusion_options:
        current_options = diffusion_options[message.from_user.id]
    else:
        current_options = diffusion_options[1]

    refine = match_True_False(line,'refine')
    upscale = match_True_False(line,'upscale')
    negative = match_text(line,'negative')
    guidance = match_number(line,'guidance')
    height = match_number(line,'height')
    width = match_number(line,'width')
    refiner_steps = match_number(line,'refiner_steps')
    steps = match_number(line,'steps')
    model = match_word(line,'model')
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
            ]
    diffusion_options[message.from_user.id] = options
    print(options)
    return diffusion_options




    
