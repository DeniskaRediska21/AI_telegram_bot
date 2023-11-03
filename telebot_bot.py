import config
import g4f
from googletrans import Translator
import telebot
from proxy_randomizer import RegisteredProviders



translator = Translator()

bot = telebot.TeleBot(config.BOT_TOKEN)
global lang
lang = 'en'

history = {123 : ['test', 'test']}
history_max_length = 4

@bot.message_handler(commands = ['new'])
def clear_history(message):
    if message.from_user.id in history:
        del history[message.from_user.id]
    bot.send_message(message.from_user.id, "New dialogue started")


@bot.message_handler(commands = ['lang'])
def lang_process(language):
    global lang
    line = language.text
    lang = line[line.find('/')+line[line.find('/')+1:].strip().find(' ')+1:].strip() 
    bot.send_message(language.from_user.id, f"Language set to: {lang}")

@bot.message_handler(content_types='text')
def gettext(message):
    try:
        global lang
        bot.send_message(message.from_user.id, "Минуточку...")

        rp = RegisteredProviders()
        rp.parse_providers()
        proxi = rp.get_random_proxy()

        en_txt = translator.translate(message.text,dest = 'en') 

        if message.from_user.id in history:
            prompt ='\n'.join(['Dont include the dialogue in your answer, dont include "AI assistant in answer"','\n'.join(history[message.from_user.id]),"user: " + en_txt.text]) 
        else:
            prompt = en_txt.text 
        
        ans = g4f.ChatCompletion.create(proxi=proxi,model = "gpt-3.5-turbo",messages = [{"role":"user","content":prompt}])
        try:
            ans_ru = translator.translate(ans,dest = lang).text
        except:
            lang = 'en'
            ans_ru = translator.translate(ans,dest = lang).text

        if message.from_user.id in history:
            if len(history[message.from_user.id])+2 <= history_max_length:
                    history[message.from_user.id].extend(['user: ' + message.text, 'AI assistant: ' + ans])
            else:
                history[message.from_user.id][0:2] = []  
                history[message.from_user.id].extend(['user: ' + message.text, 'AI assistant: ' + ans])
        else:
            history[message.from_user.id] = ['user: ' + message.text, 'AI assistant: ' + ans] 

        #print('\n'.join(history[message.from_user.id]))
        bot.send_message(message.from_user.id, ans_ru)
    except:
        bot.send_message(message.from_user.id, "Что-то пошло не так :( Повторите запрос")

        


bot.polling(none_stop=True,interval = 0)
