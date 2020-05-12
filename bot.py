import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler

from handlers import *
import settings


logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='bot.log')

subscribers = set()
"""
def my_test(bot, job):
    bot.sendMessage(chat_id=403721672, text="HAHA SPAM")
    job.interval += 5
    if job.interval > 15:
        bot.sendMessage(chat_id=403721672, text="Enough..")
        job.schedule_removal()
"""

def main():
    mybot = Updater(settings.API_KEY, request_kwargs=settings.PROXY)
    
    logging.info('Bot starts')

    dp = mybot.dispatcher

    mybot.job_queue.run_repeating(send_updates, interval=5)
    #mybot.job_queue.run_repeating(my_test, interval=3)


    anketa = ConversationHandler(
    entry_points = [RegexHandler('^(Заполнить анкету)$', anketa_start, 
                    pass_user_data=True)],
    states = {
        'name': [MessageHandler(Filters.text, anketa_get_name, pass_user_data=True)],
        'rating': [RegexHandler('^(1|2|3|4|5)$', anketa_rating, pass_user_data=True)],
        'comment': [MessageHandler(Filters.text, anketa_comment, pass_user_data=True),
                    CommandHandler('skip', anketa_skip_comment, pass_user_data=True)]
        },
    fallbacks = [MessageHandler(Filters.text | Filters.video | Filters.photo | 
                                Filters.document, dontknow, pass_user_data=True
        )]
    )
    
    dp.add_handler(CommandHandler('start', greet_user, pass_user_data=True))
    dp.add_handler(anketa)
    dp.add_handler(CommandHandler("cat", send_cat_picture, pass_user_data=True))
    dp.add_handler(RegexHandler('^(Прислать котика)$', send_cat_picture, pass_user_data=True))
    dp.add_handler(RegexHandler('^(Сменить аватарку)$', change_avatar, pass_user_data=True))
    dp.add_handler(MessageHandler(Filters.contact, get_contact, pass_user_data=True))
    dp.add_handler(MessageHandler(Filters.location, get_location, pass_user_data=True))
    dp.add_handler(CommandHandler('subscribe', subscribe))
    dp.add_handler(CommandHandler('unsubscribe', unsubscribe))

    dp.add_handler(MessageHandler(Filters.photo, check_user_photo, pass_user_data=True))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me, pass_user_data=True))
    
    mybot.start_polling()
    mybot.idle()

if __name__ == "__main__":
    main()