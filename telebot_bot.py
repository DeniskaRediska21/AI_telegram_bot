import config
import g4f
from googletrans import Translator
import telebot
from proxy_randomizer import RegisteredProviders
import re
import formatting
from multiprocessing import Process


translator = Translator()

bot = telebot.TeleBot(config.BOT_TOKEN)

lang = {123 : 'en'}
history = {123 : ['test', 'test']}
history_max_length = 4

def gpt_answer(prompt):
    providers = [g4f.Provider.Aichat,
                g4f.Provider.ChatBase,
                g4f.Provider.Bing,
                g4f.Provider.GptGo,
                g4f.Provider.You,
                g4f.Provider.Yqcloud]
    for provider in providers:
        try:
            rp = RegisteredProviders()
            rp.parse_providers()
            proxi = rp.get_random_proxy()
            completion = g4f.ChatCompletion.create(proxi=proxi,model = "gpt-3.5-turbo",messages = [{"role":"user","content":prompt}])
            break
        except:
            pass

    return completion

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
        text = re.search('(?<=\/translate .. ).*',line).group(0)
        bot.send_message(message.from_user.id, f"{translator.translate(text,dest = dest).text}")
    except:
        bot.send_message(message.from_user.id, "Please make sure your message is structured like this: /translate <language> <text>")
    

@bot.message_handler(content_types='text')
def handler(message):
    p = Process(target = gettext, args = (bot,message)).start()

def gettext(bot,message):
    try:
        print(f'Started processing {message.from_user.id}')
        bot.send_message(message.from_user.id, "One minute...")

        en_txt = translator.translate(message.text,dest = 'en') 

        if message.from_user.id in history:
            prompt ='\n'.join(['Dont include the dialogue in your answer, dont include "AI assistant in answer"','\n'.join(history[message.from_user.id]),"user: " + en_txt.text]) 
        else:
            prompt = en_txt.text 
        
        ans = gpt_answer(prompt)

        try:
            ans_ru = translator.translate(ans,dest = lang[message.from_user.id]).text
        except:
            lang[message.from_user.id] = 'en'
            ans_ru = translator.translate(ans,dest = lang[message.from_user.id]).text

        if message.from_user.id in history:
            if len(history[message.from_user.id])+2 <= history_max_length:
                    history[message.from_user.id].extend(['user: ' + message.text, 'AI assistant: ' + ans])
            else:
                history[message.from_user.id][0:2] = []  
                history[message.from_user.id].extend(['user: ' + message.text, 'AI assistant: ' + ans])
        else:
            history[message.from_user.id] = ['user: ' + message.text, 'AI assistant: ' + ans] 
        
        try:
            bot.send_message(message.from_user.id, formatting.format_for_markdown(ans_ru),parse_mode = 'MarkdownV2')
        except:
            bot.send_message(message.from_user.id, ans_ru)
        print(f'Processed {message.from_user.id}')

    except:
        bot.send_message(message.from_user.id, "Что-то пошло не так :( Повторите запрос")

        
def run_bot():
    bot.polling(none_stop=True,interval = 0)

run_bot()

