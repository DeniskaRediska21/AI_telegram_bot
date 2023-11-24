import config
import g4f
from googletrans import Translator
import telebot
from proxy_randomizer import RegisteredProviders
import re
import formatting
from multiprocessing import Process, Manager
import random
import multiprocessing
import time
import os
import wolframalpha
from pprint import pprint
import requests
import urllib.parse
import Stable_diffusion_XL
from PIL import Image
from io import BytesIO
import pickle
import Diffusers_options_parser
import torch

translator = Translator()

bot = telebot.TeleBot(config.BOT_TOKEN)
generator = torch.Generator()

#lang = {1 : 'en'}
#global history
#history = {1 : ['test', 'test']}
#diffusion_options= {1 : [False, False,'',8,512,512,100,100,'xl',True,'original']}

users = {}

history_max_length = 4

m = Manager()
q = m.Queue()

class User:
    def __init__(self,message):
        self.id = message.from_user.id
        self.history = []
        self.lang = 'en'
        self.diffusion_options = [False, False,'',8,512,512,100,100,'xl',True,'original',0]
        self.diffusion_messages = []
    def diffusion_settings_message(self):
        text = f'''/diffusion
refine {self.diffusion_options[0]};
upscale {self.diffusion_options[1]};
negative {self.diffusion_options[2]};
guidance {self.diffusion_options[3]};
height {self.diffusion_options[4]};
width {self.diffusion_options[5]};
refiner_steps {self.diffusion_options[6]};
steps {self.diffusion_options[7]};
model {self.diffusion_options[8]};
lcm {self.diffusion_options[9]};
vae {self.diffusion_options[10]};
seed {self.diffusion_options[11]};
'''
        return text

def add_user(message,users):
    if message.from_user.id not in users:
        users[message.from_user.id] = User(message)

    return users


def make_directory(directory):
    if not os.path.exists(directory):
        # Create the directory
        os.makedirs(directory)
        print("Directory created successfully!")
    else:
        print("Directory already exists!")

make_directory('Logs')
make_directory('User_files')
make_directory('Cache')

#if os.path.isfile('Cache/lang.pickle'):
#    with open('Cache/lang.pickle', 'rb') as handle:
#        lang = pickle.load(handle)

if os.path.isfile('Cache/users.pickle'):
    with open('Cache/users.pickle', 'rb') as handle:
        users = pickle.load(handle)

#if os.path.isfile('Cache/diffusion.pickle'):
#    with open('Cache/diffusion.pickle', 'rb') as handle:
#        diffusion_options = pickle.load(handle)
    
def send_file_via_telegram(bot, chat_id, file_path):
    with open(file_path, 'rb') as file:
        bot.send_document(chat_id, file)


def write_text_to_file(file_path, text):
    try:
        with open('User_files/'+file_path, 'w') as file:
            file.write(text)
    except IOError:
        print("Error: Failed to write text to", file_path)


def get_last_item(queue):
    last_item = None
    while not queue.empty():
        last_item = queue.get()
    return last_item


def gpt_answer(prompt):
    providers = [
    g4f.Provider.GPTalk, # Worked with proxi
    g4f.Provider.Liaobots,# Worked with proxi
    g4f.Provider.Phind,# Worked with proxi
    g4f.Provider.ChatBase,# Worked with proxi
    g4f.Provider.ChatgptAi,# Worked with proxi
    #g4f.Provider.Llama2,# Worked with proxi
    ]
    random.shuffle(providers)
    for provider in providers:
        try:
            rp = RegisteredProviders()
            rp.parse_providers()
            proxi = rp.get_random_proxy()
            completion = g4f.ChatCompletion.create(timeout=120,proxi=proxi,model = "gpt-3.5-turbo",messages = [{"role":"user","content":prompt}])
            break
        except:
            continue

    return completion,provider

@bot.message_handler(commands = ['help','start'])
def list_commands(message):
    global users
    users = add_user(message,users)
    bot.send_message(message.from_user.id,
    """
This is a multilanguage ChatGPT3\.5 based chatbot\.    
*/new* \- to start new dialogue
*/lang \<language\>* \- to set output language
*/translate \<language\> \<text\>* \- to translate text to language
*/file \<filename\> \<text\>* \- to write text to file and recieve written file via telegram
*/draw \<image description\>* \- to generate image using StableDiffusionXL 
*/math \<math problem\>* \- to solve math problems using WolframAlpha
*/help* \- to see this message again
    """, parse_mode ='MarkdownV2')

@bot.message_handler(commands = ['new'])
def clear_history(message):
    global users
    users = add_user(message,users)
    users[message.from_user.id].history = []
    bot.send_message(message.from_user.id, "New dialogue started")

@bot.message_handler(commands = ['models'])
def model_prompt(message):
    global users
    users = add_user(message,users)
    bot_message = bot.send_message(message.from_user.id, Diffusers_options_parser.DIFFUSION_MODEL_PROMPT)
    users[message.from_user.id].diffusion_messages.append(message)
    users[message.from_user.id].diffusion_messages.append(bot_message)


def delete_messages(message,users,bot):
    for dm in users[message.from_user.id].diffusion_messages:
        bot.delete_message(dm.chat.id,dm.message_id)
    users[message.from_user.id].diffusion_messages=[]
    return users


@bot.message_handler(commands = ['draw'])
def generate_image_handler(message):
    global users
    users = add_user(message,users)
    users = delete_messages(message,users,bot)
    try:
        prompt = message.text[6:]
        prompt = translator.translate(prompt,dest = 'en').text
        bot_message = bot.send_message(message.from_user.id, "One minute...")
        p = Process(target = generate_and_send_img, args = (bot,message,prompt,users[message.from_user.id],bot_message)).start()
            
        with open('Cache/users.pickle', 'wb') as handle:
            pickle.dump(users,handle)
    except:
        bot.send_message(message.from_user.id, "Something went wrong while generating :c")
        
        
def generate_and_send_img(bot,message,prompt,user,bot_message):
    image,seed = Stable_diffusion_XL.generate_image(prompt,*user.diffusion_options,generator)
    if image is not None:
        image_bytes = BytesIO()
        image.save(image_bytes, format='JPEG')
        image_bytes.seek(0)
        caption = ('\n').join([formatting.format_for_markdown('Prompt:'),'```',message.text,'```','Settings\:','```',user.diffusion_settings_message(),'```',formatting.format_for_markdown(f'Seed: \n`/diffusion seed {seed}`')])
        bot.send_photo(message.from_user.id, photo=image_bytes,caption = caption,parse_mode = 'MarkdownV2')
        
        bot.delete_message(message.chat.id,message.message_id)
        bot.delete_message(bot_message.chat.id,bot_message.message_id)
    else:
        bot.send_message(message.from_user.id,"Image generation is not working at the moment.")



@bot.message_handler(commands = ['math'])
def talk_to_wolfram(message):
    global users
    users = add_user(message,users)
    prompt = message.text[6:]
    prompt = translator.translate(prompt,dest = 'en').text
    bot.send_message(message.from_user.id, "One minute...")
    p = Process(target = wolfram, args = (bot,message,prompt,users)).start()
            
        
        
def wolfram(bot,message,prompt,users):
    try:
        query = urllib.parse.quote_plus(translator.translate(prompt,dest = 'en').text)
        query_url = f"http://api.wolframalpha.com/v2/query?" \
                    f"appid={config.WOLFRAM_ID}" \
                    f"&input={query}" \
                    f"&scanner=Solve" \
                    f"&podstate=Result__Step-by-step+solution" \
                    "&format=plaintext" \
                    f"&output=json"

        r = requests.get(query_url).json()

        data = r["queryresult"]["pods"][0]["subpods"]
        result = data[0]["plaintext"]
        steps = data[1]["plaintext"]

        answer_text = translator.translate(f"Result of \n'{prompt}'\nis\n{result}",dest = users[message.from_user.id].lang).text
        solution_text = translator.translate(f"Possible steps to solution:\n{steps}",dest = users[message.from_user.id].lang).text

        bot.send_message(message.from_user.id,answer_text)
        bot.send_message(message.from_user.id,solution_text)
    except:
        bot.send_message(message.from_user.id, "Something went wrong while calculating :c")
    
@bot.message_handler(commands = ['file'])
def send_file(message):
    global users
    users = add_user(message,users)
    line = message.text
    filename = re.findall('(?<=\/file )[A-Za-z_.]*',line)[0]
    text = line[5+len(filename)+2:]
    try:
        os.mkdir('User_files')
    except FileExistsError:
        pass
    write_text_to_file(filename,text)
    send_file_via_telegram(bot,message.from_user.id,'User_files/'+filename)
    os.remove('User_files/'+filename)


@bot.message_handler(commands = ['lang'])
def lang_process(message):
    global users
    users = add_user(message,users)

    line = message.text
    try:
        users[message.from_user.id].lang = re.search('(?<=\/lang )[A-Za-z]{2}',line).group(0) 
        lang[message.from_user.id] = re.search('(?<=\/lang )[A-Za-z]{2}',line).group(0)
    except:
        if not (message.from_user.id in lang):
            lang[message.from_user.id] = 'en'
#    with open('Cache/lang.pickle', 'wb') as handle:
#        pickle.dump(lang,handle)

    with open('Cache/users.pickle', 'wb') as handle:
        pickle.dump(users,handle)

    bot.send_message(message.from_user.id, f"Language set to: {lang[message.from_user.id]}")


@bot.message_handler(commands = ['diffusion'])
def diffusion_setup(message):
    global users
    users = add_user(message,users)
#    global diffusion_options
    try:
        if len(message.text) != 10:
            users[message.from_user.id].diffusion_options = Diffusers_options_parser.parse_diffusion_options(users[message.from_user.id].diffusion_options,message)
            with open('Cache/users.pickle', 'wb') as handle:
                pickle.dump(users,handle)

        sent_message = bot.send_message(message.from_user.id,users[message.from_user.id].diffusion_settings_message())
            
#            with open('Cache/diffusion.pickle', 'wb') as handle:
#                pickle.dump(diffusion_options,handle)
    except:
        sent_message = bot.send_message(message.from_user.id, 'Something went wrong while parsing options')

    if len(users[message.from_user.id].diffusion_messages)<10:
        users[message.from_user.id].diffusion_messages.append(message)
        users[message.from_user.id].diffusion_messages.append(sent_message)


@bot.message_handler(commands = ['translate'])
def translate_message(message):
    global users
    users = add_user(message,users)
    try:
        line = message.text
        dest = re.search('(?<=\/translate )[A-Za-z]{2}',line).group(0)
        #text = re.search('(?<=\/translate .. ).*',line).group(0)
        if len(line) >13:
            text = line[13:]
        else:

            try:
                users[message.from_user.id].history = q.get(False)
            except: 
                pass

            if users[message.from_user.id].history:
                text = users[message.from_user.id].history[-1]
            else:
                bot.send_message(message.from_user.id, "Please make sure your message is structured like this: /translate <language> <text>")
 
            
        bot.send_message(message.from_user.id, f"{translator.translate(text,dest = dest).text}")
    except:
        bot.send_message(message.from_user.id, "Please make sure your message is structured like this: /translate <language> <text>")
    

@bot.message_handler(content_types='text')
def handler(message):
    global users
    users = add_user(message,users)
    try:
        users[message.from_user.id].history = q.get(False)
    except: 
        pass
    thread_history = users[message.from_user.id].history
        
    p = Process(target = gettext, args = (bot,message,thread_history,users[message.from_user.id].lang,q)).start()


def gettext(bot,message,history,lang,q):
    try:
        print(f'Started processing {message.from_user.id}')
        bot_message = bot.send_message(message.from_user.id, "One minute...")

        en_txt = translator.translate(message.text,dest = 'en') 
        if history:
            prompt ='\n'.join(['Dont include the dialogue in your answer, dont include "AI assistant in answer"','\n'.join(history),"user: " + en_txt.text]) 
        else:
            prompt = en_txt.text 
        
        ans,provider = gpt_answer(prompt)

        try:
            ans_ru = translator.translate(ans,dest = lang).text
        except:
            bot.send_message(message.from_user.id,f'I dont know language {lang}, I will answer in en')
            lang = 'en'
            ans_ru = translator.translate(ans,dest = lang).text

        if len(history)+2 <= history_max_length:
                history.extend(['user: ' + message.text, 'AI assistant: ' + ans])
        else:
            history[0:2] = []  
            history.extend(['user: ' + message.text, 'AI assistant: ' + ans])
        q.put(history)

        if lang == 'en': 
            try:
                bot.send_message(message.from_user.id, formatting.format_for_markdown(ans_ru),parse_mode = 'MarkdownV2')
            except:
                bot.send_message(message.from_user.id, ans_ru)
        else:
            bot.send_message(message.from_user.id, ans_ru)
        with open(f"Logs/{message.from_user.id}.txt", "a") as log_file:
            log_file.write(f'{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}: {message.text}\nbot: {ans_ru}\n')
            
        print(f'Processed {message.from_user.id}, provider: {provider}')

    except:
        bot.send_message(message.from_user.id, "Что-то пошло не так :( Повторите запрос")
    bot.delete_message(bot_message.chat.id,bot_message.message_id)        

        
def run_bot():
    try:
        bot.polling(none_stop=True,interval = 0)
    except:
        print('Error while polling')
while True:
    run_bot()
    time.sleep(5)

