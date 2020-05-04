from glob import glob
import logging
from random import choice

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

import settings

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='bot.log')

def greet_user(bot, update):
    text = 'Вызван /start'
    logging.info(text)
    update.message.reply_text(text)

def talk_to_me(bot, update):
    user_text = "Привет {}! Ты написал: {}".format(update.message.chat.first_name, 
                 update.message.text)
    logging.info("User: %s, Chat id: %s, Message: %s",update.message.chat.username,
                 update.message.chat.id, update.message.text)
    update.message.reply_text(user_text)

def send_hedgehog_picture(bot, update):
    hedgehog_list = glob('images/hedgehog*.jp*g')
    hedgehog_pic = choice(hedgehog_list)
    bot.send_photo(chat_id=update.message.chat_id, photo=open(hedgehog_pic, 'rb'))

def main():
    mybot = Updater(settings.API_KEY, request_kwargs=settings.PROXY)
    
    logging.info('Bot starts')

    dp = mybot.dispatcher
    dp.add_handler(CommandHandler('start', greet_user))
    dp.add_handler(CommandHandler("hedgehog", send_hedgehog_picture))

    dp.add_handler(MessageHandler(Filters.text, talk_to_me))
    

    mybot.start_polling()
    mybot.idle()

main()