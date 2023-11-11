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

translator = Translator()

bot = telebot.TeleBot(config.BOT_TOKEN)

lang = {123 : 'en'}
global history
history = {123 : ['test', 'test']}
history_max_length = 4
m = Manager()
q = m.Queue()


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
    #g4f.Provider.ChatBase,# Worked with proxi
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
    bot.send_message(message.from_user.id,
    """
This is a multilanguage ChatGPT3\.5 based chatbot\.    
*/new* \- to start new dialogue
*/lang \<language\>* \- to set output language
*/translate \<language\> \<text\>* \- to translate text to language
*/file \<filename\> \<text\>* \- to write text to file and recieve written file via telegram
*/draw \<image description\>* \- to generate image using StableDiffusionXL 
*/math \<math problem\>* \- to solve math problems
*/help* \- to see this message again
    """, parse_mode ='MarkdownV2')

@bot.message_handler(commands = ['new'])
def clear_history(message):
    if message.from_user.id in history:
        del history[message.from_user.id]
    bot.send_message(message.from_user.id, "New dialogue started")

import Stable_diffusion_XL
from PIL import Image
from io import BytesIO
@bot.message_handler(commands = ['draw'])
def generate_image_handler(message):
    try:
        prompt = message.text[6:]
        prompt = translator.translate(prompt,dest = 'en').text
        bot.send_message(message.from_user.id, "One minute...")
        p = Process(target = generate_and_send_img, args = (bot,message,prompt)).start()
            
    except:
        bot.send_message(message.from_user.id, "Something went wrong while generating :c")
        
        
def generate_and_send_img(bot,message,prompt):
    image = Stable_diffusion_XL.generate_image(prompt,n_steps = 100,n_refiner_steps = 100)
    if image is not None:
        image_bytes = BytesIO()
        image.save(image_bytes, format='JPEG')
        image_bytes.seek(0)
        bot.send_photo(message.from_user.id, photo=image_bytes)
    else:
        bot.send_message(message.from_user.id,"Image generation is not working at the moment.")



@bot.message_handler(commands = ['math'])
def talk_to_wolfram(message):
        prompt = message.text[6:]
        prompt = translator.translate(prompt,dest = 'en').text
        bot.send_message(message.from_user.id, "One minute...")
        p = Process(target = wolfram, args = (bot,message,prompt)).start()
            
        
        
def wolfram(bot,message,prompt):
    try:
        query = urllib.parse.quote_plus(prompt)
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

        bot.send_message(message.from_user.id, f"Result of {prompt} is '{result}'.")
        bot.send_message(message.from_user.id, f"Possible steps to solution:{steps}")
    except:
        bot.send_message(message.from_user.id, "Something went wrong while calculating :c")
    
@bot.message_handler(commands = ['file'])
def send_file(message):
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
def lang_process(language):
    line = language.text
    try:
        lang[language.from_user.id] = re.search('(?<=\/lang )[A-Za-z]{2}',line).group(0)
    except:
        if not (language.from_user.id in lang):
            lang[language.from_user.id] = 'en'
    bot.send_message(language.from_user.id, f"Language set to: {lang[language.from_user.id]}")

@bot.message_handler(commands = ['translate'])
def translate_message(message):
    try:
        line = message.text
        dest = re.search('(?<=\/translate )[A-Za-z]{2}',line).group(0)
        #text = re.search('(?<=\/translate .. ).*',line).group(0)
        if len(line) >13:
            text = line[13:]
        else:

            try:
                history[message.from_user.id] = q.get(False)
            except: 
                pass

            if message.from_user.id in history:
                text = history[message.from_user.id][-1]
            else:
                bot.send_message(message.from_user.id, "Please make sure your message is structured like this: /translate <language> <text>")
 
            
        bot.send_message(message.from_user.id, f"{translator.translate(text,dest = dest).text}")
    except:
        bot.send_message(message.from_user.id, "Please make sure your message is structured like this: /translate <language> <text>")
    

@bot.message_handler(content_types='text')
def handler(message):
    global history
    try:
        history[message.from_user.id] = q.get(False)
    except: 
        pass
    if message.from_user.id in history:
            thread_history = history[message.from_user.id]
    else:
        thread_history = []
        
    p = Process(target = gettext, args = (bot,message,thread_history,lang,q)).start()


def gettext(bot,message,history,lang,q):
    try:
        print(f'Started processing {message.from_user.id}')
        bot.send_message(message.from_user.id, "One minute...")

        en_txt = translator.translate(message.text,dest = 'en') 
        if len(history)>0:
            prompt ='\n'.join(['Dont include the dialogue in your answer, dont include "AI assistant in answer"','\n'.join(history),"user: " + en_txt.text]) 
        else:
            prompt = en_txt.text 
        
        ans,provider = gpt_answer(prompt)

        try:
            ans_ru = translator.translate(ans,dest = lang[message.from_user.id]).text
        except:
            lang[message.from_user.id] = 'en'
            ans_ru = translator.translate(ans,dest = lang[message.from_user.id]).text

        if len(history)+2 <= history_max_length:
                history.extend(['user: ' + message.text, 'AI assistant: ' + ans])
        else:
            history[0:2] = []  
            history.extend(['user: ' + message.text, 'AI assistant: ' + ans])
        q.put(history)

        if lang[message.from_user.id] == 'en': 
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

        
def run_bot():
    try:
        bot.polling(none_stop=True,interval = 0)
    except:
        print('Error while polling')
while True:
    run_bot()
    time.sleep(5)

