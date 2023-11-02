import config
import telebot

bot = telebot.TeleBot(config.BOT_TOKEN)

@bot.message_handler(content_types = 'text')
def gettext(message):
    bot.send_message(message.from_user.id,'```Hello```',parse_mode = 'MarkdownV2')

bot.polling(none_stop = True,interval = 0)
