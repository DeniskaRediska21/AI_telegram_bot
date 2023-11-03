import config
import g4f
from googletrans import Translator
import telebot
from proxy_randomizer import RegisteredProviders



translator = Translator()

bot = telebot.TeleBot(config.BOT_TOKEN)
lang = 'en'

@bot.message_handler(commands = ['lang'])
def lang_process(language):
    line = language.text
    lang = line[line.find('/')+line[line.find('/')+1:].strip().find(' ')+1:].strip() 
    bot.send_message(language.from_user.id, f"lang set to: {lang}")

@bot.message_handler(content_types='text')
def gettext(message):
    try:

        bot.send_message(message.from_user.id, "Минуточку...")

        rp = RegisteredProviders()
        rp.parse_providers()
        proxi = rp.get_random_proxy()


        en_txt = translator.translate(message.text,dest = 'en') 

        ans = g4f.ChatCompletion.create(proxi=proxi,model = "gpt-3.5-turbo",messages = [{"role":"user","content":en_txt.text}])
        try:
            ans_ru = translator.translate(ans,dest = lang).text
        except:
            lang = 'en'
            ans_ru = translator.translate(ans,dest = lang).text
        

        bot.send_message(message.from_user.id, ans_ru)
   except:
        bot.send_message(message.from_user.id, "Что-то пошло не так :( Повторите запрос")

        


bot.polling(none_stop=True,interval = 0)
