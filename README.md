# G4f Telegram Bot

Chat GPT telegram bot powered by gpt4free and telebot

## Phone setup

To host the bot localy on Android phone follow this steps:

 1) [Get the bot token from @BotFather in telegram app](https://t.me/botfather)
 2) [Install Termux](https://f-droid.org/packages/com.termux/)
 3) [Install AnLinux](https://f-droid.org/packages/exa.lnx.a/)
 4) Install Ubuntu dashboard following instructions in AnLinux

 In termux:

 5) ```./start-ubuntu.sh```
 6) ```apt update && apt upgrade```
 7) ```apt install python3 pip kakoune git```
 8) ```git clone https://github.com/DeniskaRediska21/G4f_telegram_bot.git```
 9) ```cd G4f_telegram_bot```
 10) ```source g4f_telebot```
 11) ```cat requirements.txt | xargs -n 1 pip install```
 12) ```kak config.py```
 13) Paste to config.py:  ```BOT_TOKEN = "Token provided by @BotFather"```
 14) ```python3 telebot_bot.py```
