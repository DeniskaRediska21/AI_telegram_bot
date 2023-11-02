import config
import g4f
from googletrans import Translator
import telebot

translator = Translator()

bot = telebot.TeleBot(config.BOT_TOKEN)
lang = 'en'

@bot.message_handler(commands = ['lang'])
def lang(language):
    line = language.text
    lang = line[line.find('/')+line[line.find('/')+1:].strip().find(' ')+1:].strip() 
    bot.send_message(language.from_user.id, f"lang set to: {lang}")

@bot.message_handler(content_types='text')
def gettext(message):
    try:

        bot.send_message(message.from_user.id, "Минуточку...")

        en_txt = translator.translate(message.text,dest = lang) 

        ans = g4f.ChatCompletion.create(model = "gpt-3.5-turbo",messages = [{"role":"user","content":en_txt.text}])

        ans_ru = translator.translate(ans,dest = 'en').text  

        bot.send_message(message.from_user.id, ans_ru)
    except:
        bot.send_message(message.from_user.id, "Что-то пошло не так :( Повторите запрос")

        


bot.polling(none_stop=True,interval = 0)
