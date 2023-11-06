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

translator = Translator()

bot = telebot.TeleBot(config.BOT_TOKEN)

lang = {123 : 'en'}
global history
history = {123 : ['test', 'test']}
history_max_length = 4
m = Manager()
q = m.Queue()

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
    print(prompt)
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
*/help* \- to see this message again
    """, parse_mode ='MarkdownV2')

@bot.message_handler(commands = ['new'])
def clear_history(message):
    if message.from_user.id in history:
        del history[message.from_user.id]
    bot.send_message(message.from_user.id, "New dialogue started")


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
    print(history)
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

        print(f'Processed {message.from_user.id}, provider: {provider}')

    except:
        bot.send_message(message.from_user.id, "Что-то пошло не так :( Повторите запрос")

        
def run_bot():
    bot.polling(none_stop=True,interval = 0)

run_bot()

