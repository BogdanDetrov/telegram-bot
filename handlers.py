from glob import glob
from random import choice
import logging
import os

from telegram import ReplyKeyboardRemove, ReplyKeyboardMarkup, ParseMode, error
from telegram.ext import ConversationHandler
from telegram.ext import messagequeue as mq

from utils import get_keyboard, is_cat
from db import db, get_or_create_user, get_user_emo, toogle_subscription, get_subscribers
from bot import subscribers


def greet_user(bot, update, user_data):
    user = get_or_create_user(db, update.effective_user, update.message)
    emo = get_user_emo(db, user)
    user_data['emo'] = emo
    text = 'Привет {}'.format(emo)
    update.message.reply_text(text, reply_markup=get_keyboard())

def talk_to_me(bot, update, user_data):
    user = get_or_create_user(db, update.effective_user, update.message)
    emo = get_user_emo(db, user)
    user_text = "Привет {} {}! Ты написал: {}".format(user['first_name'], 
                emo, update.message.text)
    logging.info("User: %s, Chat id: %s, Message: %s",user['username'],
                 update.message.chat.id, update.message.text)
    update.message.reply_text(user_text, reply_markup=get_keyboard())

def send_cat_picture(bot, update, user_data):
    user = get_or_create_user(db, update.effective_user, update.message)
    cat_list = glob('images/cat*.jp*g')
    cat_pic = choice(cat_list)
    bot.send_photo(chat_id=update.message.chat_id, photo=open(cat_pic, 'rb'), reply_markup=get_keyboard())

def change_avatar(bot, update, user_data):
    user = get_or_create_user(db, update.effective_user, update.message)
    if 'emo' in user:
        del user['emo']
    emo = get_user_emo(db, user)
    update.message.reply_text('Готово: {}'.format(emo), reply_markup=get_keyboard())


def get_contact(bot, update, user_data):
    user = get_or_create_user(db, update.effective_user, update.message)
    print(update.message.contact)
    update.message.reply_text('Готово {}'.format(get_user_emo(db, user)),                reply_markup=get_keyboard()) 


def get_location(bot, update, user_data):
    user = get_or_create_user(db, update.effective_user, update.message)
    print(update.message.location)
    update.message.reply_text('Готово {}'.format(get_user_emo(db, user)), reply_markup=get_keyboard())   


def check_user_photo(bot, update, user_data):
    user = get_or_create_user(db, update.effective_user, update.message)
    update.message.reply_text('Обрабатываем фото')
    os.makedirs('downloads', exist_ok=True)
    photo_file = bot.getFile(update.message.photo[-1].file_id)
    filename = os.path.join('downloads', '{}.jpg'.format(photo_file.file_id))
    photo_file.download(filename)
    if is_cat(filename):
        update.message.reply_text('Обнаружен котик, добавляю в библиотеку.')
        new_filename = os.path.join('images', 'cat{}.jpg'.format(photo_file.file_id))
        os.rename(filename, new_filename)
    else:
        os.remove(filename)
        update.message.reply_text("Котик не обнаружен.")


def anketa_start(bot, update, user_data):
    user = get_or_create_user(db, update.effective_user, update.message)
    update.message.reply_text('Как вас зовут? Напишите имя и фамилию',
    reply_markup=ReplyKeyboardRemove())
    return 'name'

def anketa_get_name(bot, update, user_data):
    user = get_or_create_user(db, update.effective_user, update.message)
    user_name = update.message.text
    if len(user_name.split(" ")) != 2:
        update.message.reply_text('Пожалуйста введите имя и фамилию')
        return 'name'
    else:
        user_data['anketa_name'] = user_name
        reply_keyboard = [['1','2','3','4','5']]

        update.message.reply_text(
            'Оцените нашего бота от 1 до 5',
            reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
            resize_keyboard = True
        )
        return 'rating'

def anketa_rating(bot, update, user_data):
    user = get_or_create_user(db, update.effective_user, update.message)
    user_data['anketa_rating'] = update.message.text
    update.message.reply_text('''Пожалуйста напишите отзыв в свободной форме или /cancel чтобы пропустить данный этап''')
    return "comment"

def anketa_comment(bot, update, user_data):
    user = get_or_create_user(db, update.effective_user, update.message)
    user_data['anketa_comment'] = update.message.text
    text = """
<b>Ваше имя и фамлия: </b>{anketa_name}
<b>Ваша оценка: </b>{anketa_rating}
<b>Ваш комментарий: </b>{anketa_comment}""".format(**user_data)
    update.message.reply_text(text, reply_markup=get_keyboard(), parse_mode=ParseMode.HTML)
    return ConversationHandler.END

def anketa_skip_comment(bot, update, user_data):
    user = get_or_create_user(db, update.effective_user, update.message)
    text = """
<b>Ваше имя и фамилия: </b>{anketa_name}
<b>Ваша оценка: </b>{anketa_rating}""".format(**user_data)
    update.message.reply_text(text, reply_markup=get_keyboard(), parse_mode=ParseMode.HTML)
    return ConversationHandler.END


def dontknow(bot, update, user_data):
    user = get_or_create_user(db, update.effective_user, update.message)
    update.message.reply_text('Не понимаю')

def subscribe(bot, update):
    user = get_or_create_user(db, update.effective_user, update.message)
    if not user.get('subscribed'):
        toogle_subscription(db, user)
        update.message.reply_text('Вы подписались')
    elif user.get('subscribed'):
        update.message.reply_text('Вы уже подписаны :)')

@mq.queuedmessage
def send_updates(bot, job):
    for user in get_subscribers(db):
        try:
            bot.sendMessage(chat_id=user['chat_id'], text="BUZZ")
        except error.BadRequest:
            print('Chat {} not found'.format(user['chat_id']))
            


def unsubscribe(bot, update):
    user = get_or_create_user(db, update.effective_user, update.message)
    if user.get('subscribed'):
        toogle_subscription(db, user)
        update.message.reply_text('Вы отписались')
    else:
        update.message.reply_text('Вы не подписаны :) Можете набрать /sub чтобы подписаться')


def set_alarm(bot, update, args, job_queue):
    try:
        seconds = abs(int(args[0]))
        job_queue.run_once(alarm, seconds, context=update.message.chat_id)
        if seconds:
            update.message.reply_text(f'Будильник сработает через {seconds} секунд')
    except (IndexError, ValueError):
        update.message.reply_text("Введите число секунд после команды /alarm")

@mq.queuedmessage
def alarm(bot, job):
    bot.sendMessage(chat_id=job.context, text='БУДИЛЬНИК!!!')