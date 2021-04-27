#!/usr/bin/python
# -*- coding: UTF-8 -*-

import telebot
import time
import config
import sqlite3
import random
from telebot import types
from datetime import datetime, timedelta
from copy import deepcopy
import re
import asyncio
import dbworker
from telebot import apihelper
from datetime import datetime

# import exam_sched

# from apscheduler.schedulers.blocking import BlockingScheduler


bot = telebot.TeleBot(config.token)

links = ['https://www.patreon.com/langosaurus',
         'https://ad.admitad.com/g/0abba212ffaf2e72e1f61ac5a4392d',
         'https://ad.admitad.com/g/roblgzy8c5af2e72e1f6e1b1bba22e']
# bot.send_voice(737422517, open('abandon.ogg', 'rb'), '*abandon*:   _покидать_\n\nəˈbandən', parse_mode='Markdown')
# bot.send_photo(737422517, open('abandon.jpg', 'rb'))

words_gut = ['Согласен!', 'В лучшем виде!', 'Идеально!', 'Образцово!', 'Недурно!', 'Здорово!', 'На пять баллов!',
             'Грех жаловаться!', 'Шикарно!', 'Чудесно!', 'Колоссально!', 'Подходяще!', 'Круто!', 'Да будет так!',
             'Первоклассно!', 'Чудно!', 'На уровне!', 'Изумительно!', 'Блестяще!', 'Точно!', 'Как следует!', 'Красота!',
             'Шик-блеск!', 'Балдеж!', 'Чётко!', 'Нормалёк!', 'Замечательно!', 'Пять с плюсом!', 'Все хоккей!',
             'Великолепно!', 'Ладушки!', 'Хорошо!', 'Ништяк!', 'Нормально!', 'Восхитительно!', 'Вправду!',
             'Высшая отметка!', 'Окей!', 'Всё окей!', 'На зависть!', 'Класс!', 'Безошибочно!', 'Действительно!',
             'Высший класс!', 'Пять баллов!', 'Очень хорошо!', 'Совершенно верно!', 'Клево!', 'Виртуозно!',
             'Высшая оценка!', 'Блеск!', 'Прекрасно!', 'Мастерски!', 'Тип-топ!', 'Пятёрочка!', 'Превосходно!',
             'Это пять!', 'Неплохо!', 'Порядок!', 'Верно!', 'Так тому и быть!', 'Как нельзя лучше!', 'Обалденно!',
             'Славно!', 'Чудненько!', 'На должном уровне!', 'Классно!', 'Вау класс!', 'Отменно!']

words_bad = []

emoji_gut = ['😀', '😃', '😄', '😁', '😆', '😅', '🤣', '😂', '🙂', '🙃', '😉', '😊', '😇', '🥰', '😍', '🤩', '😘', '😋',
             '😛', '😜', '🤪', '😝', '🤑', '🤗', '🤭', '😏', '🤠', '🥳', '😎', '🤓', '🧐', '💯', '🖐', '🖖', '👌', '✌',
             '🤟', '🤘', '🤙', '👍', '🤛', '🤜', '👏', '🙌', '👐', '🤲', '💪', '🧠', '👨‍🎓', '👩‍🎓', '👨‍🚀', '👩‍🚀',
             '💂', '💂‍♂️', '💂‍♀️', '🤴', '🦸', '🦸‍♂️', '🦸‍♀️', '👯', '👯‍♂️', '👯‍♀️', '🌼', '🌱', '🌴', '🍀', '🍒',
             '🍄', '🍻', '🥂', '🗽', '🚀', '🌞', '⭐', '🌈', '⚡', '🔥', '✨', '🎈', '🎉', '🎀', '🎁', '🏆', '🥇', '🎯',
             '💎', '📈', '✅', '🆒', '🆗']

emoji_bad = ['🤫', '🤔', '🤐', '🤨', '😐', '😑', '😶', '😒', '🙄', '😬', '🤥', '😔', '😪', '😴', '😷', '🤒', '🤕', '🤢',
             '🥴', '😵', '🤯', '😕', '😟', '🙁', '😮', '😯', '😲', '😳', '🥺', '😦', '😧', '😨', '😰', '😥', '😢', '😭',
             '😱', '😖', '😣', '😞', '😓', '😩', '😫', '💩', '🙈', '🙉', '🙊', '👎', '🚑', '🚒', '🚓', '🚔', '🚨', '🛑',
             '💧', '🎃', '📉', '⛔', '🚫', '❌', '🆘', '🔴']

main_keyboard = telebot.types.ReplyKeyboardMarkup()
main_keyboard.row('/TEST', '/CARDS')
startTest_keyboard = telebot.types.ReplyKeyboardMarkup()
startTest_keyboard.row('СТАРТ 🏁')
startCard_keyboard = telebot.types.ReplyKeyboardMarkup()
startCard_keyboard.row('НАЧАТЬ 📚')
testKeyboard = telebot.types.ReplyKeyboardMarkup()
testKeyboard.row("ТЕСТ 📝")

db = sqlite3.connect("superlangbot.sqlite")
cursor = db.cursor()
cursor.execute("SELECT frase FROM motivation ORDER BY random()")
motivation = cursor.fetchall()
db.close()


@bot.message_handler(content_types=['text'],
                     func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_REBOOT.value)
def reboot_msg(message):
    bot.send_message(message.from_user.id,
                     '🛠️ Проводились технические работы. Приносим извинения за предоставленные неудобства. 😉 ⚙', disable_notification=True)
    time.sleep(2)
    return start(message)


@bot.message_handler(commands=['sudo_reboot'])
def reboot(message):
    dbworker.set_reboot_state(config.States.S_REBOOT.value)


def schedule_msg(user_id):
    bot.send_message(user_id, 'Появились слова для повторения. Рекомендуется пройти тест. /TEST', disable_notification=False)


# def schedule_msg():
#     time.sleep(1)
#     bot.send_message(737422517, 'Рекомендуется пройти тест! /TEST')
#
#
# schedule_msg()


@bot.message_handler(commands=['START', 'start'])
def start(message):
    dbworker.set_current_state(message.chat.id, config.States.S_START.value)
    bot.send_message(message.chat.id, f'<b>Привет  </b> {message.from_user.first_name}\n\n'
                                      f'Для просмотра отчета о процессе обучения введи - /progress\n\n'
                                      f'Для возврата в меню из любого режима введи - /start\n\n\n'
                                      f'<b>Выбери режим работы:</b>\n\n'
                                      '😎  тест без подготовки  -  /TEST\n\n'
                                      '🤓  работа с карточками  -  /CARDS', parse_mode='html',
                     reply_markup=main_keyboard)
    print(message.from_user.first_name, message.chat.id,
          datetime.utcfromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S'))
    dbworker.insert_new_user_into_db(message.chat.id, message.from_user.first_name,
                                     datetime.utcfromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S'))
    asyncio.run(dbworker.sched_msg(message.from_user.id))
    return


@bot.message_handler(commands=['progress'])
def show_progress_command(message):
    bot.send_message(message.chat.id, str(dbworker.progress_check(message.chat.id)[1]) + ' - слов выучено\n ' +
                     '[█▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒]' + str(
        int((dbworker.progress_check(message.chat.id)[1]) / 42.45)) + '%\n' +
                     str(dbworker.progress_check(message.chat.id)[0]) + ' - слов в процессе изучения\n' +
                     '[█▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒]' + str(
        int((dbworker.progress_check(message.chat.id)[0]) / 42.45)) + '%\n' +
                     str(4245 - int(dbworker.progress_check(message.chat.id)[2])) + ' - слов осталость в базе\n' +
                     '[████████████████████]' + str(
        int((4245 - int(dbworker.progress_check(message.chat.id)[2])) / 42.45)) + '%')
    return


###############################################################################################################


@bot.message_handler(commands=['TEST'])
def test_mode(message):
    bot.send_message(message.chat.id, '*Режим*:  _тест без подготовки_', parse_mode='Markdown',
                     reply_markup=startTest_keyboard)
    dbworker.set_current_state(message.chat.id, config.States.S_TEST.value)

    @bot.message_handler(content_types=['text'],
                         func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_TEST.value)
    def nested_test_mode(message):

        if message.text == 'СТАРТ 🏁':
            dbworker.reset_msg_counter(message.from_user.id)
            dbworker.select_and_update_user_current_word(message.from_user.id)

            bot.send_message(message.chat.id,
                             '❓  Переведи:  ' + '*' +
                             dbworker.user_current_data_from_db(message.from_user.id)[0] + '*',
                             reply_markup=dbworker.user_current_data_from_db(message.from_user.id)[4],
                             parse_mode="markdown")
            return

        elif message.text.lower() == dbworker.user_current_data_from_db(message.from_user.id)[1]:
            print('TEST: correct answer')

            # dbworker.check_word_id_in_progress(dbworker.user_current_data_from_db(message.from_user.id)[2],
            #                                    dbworker.user_current_data_from_db(message.from_user.id)[3])
            if dbworker.check_word_id_in_progress(dbworker.user_current_data_from_db(message.from_user.id)[2],
                                                  dbworker.user_current_data_from_db(message.from_user.id)[3]) == False:
                print('TEST: false  returned to test mode. set interval - 2')
                dbworker.insert_user_progress_into_db(message.chat.id,
                                                      dbworker.user_current_data_from_db(message.from_user.id)[2],
                                                      2,
                                                      int(time.time()))
                bot.send_message(message.chat.id, random.choice(emoji_gut) + ' ' + random.choice(words_gut))

            elif dbworker.check_word_id_in_progress(dbworker.user_current_data_from_db(message.from_user.id)[2],
                                                    dbworker.user_current_data_from_db(message.from_user.id)[3]) == 1:
                print('TEST: 1 returned to test mode. set interval - 2')
                dbworker.insert_user_progress_into_db(message.chat.id,
                                                      dbworker.user_current_data_from_db(message.from_user.id)[2],
                                                      2,
                                                      int(time.time()))
                bot.send_message(message.chat.id, random.choice(emoji_gut) + ' ' + random.choice(words_gut))

            elif dbworker.check_word_id_in_progress(
                    dbworker.user_current_data_from_db(message.from_user.id)[2],
                    dbworker.user_current_data_from_db(message.from_user.id)[3]) == 2:
                print('TEST: 2 returned to test mode. set interval - 4')
                dbworker.insert_user_progress_into_db(message.chat.id,
                                                      dbworker.user_current_data_from_db(message.from_user.id)[2],
                                                      4,
                                                      int(time.time()))
                bot.send_message(message.chat.id, random.choice(emoji_gut) + ' ' + random.choice(words_gut))

            elif dbworker.check_word_id_in_progress(dbworker.user_current_data_from_db(message.from_user.id)[2],
                                                    dbworker.user_current_data_from_db(message.from_user.id)[
                                                        3]) == 4:
                print('TEST: 4 returned to test mode. set interval - 8')
                dbworker.insert_user_progress_into_db(message.chat.id,
                                                      dbworker.user_current_data_from_db(message.from_user.id)[2],
                                                      8,
                                                      int(time.time()))
                bot.send_message(message.chat.id, random.choice(emoji_gut) + ' ' + random.choice(words_gut))

            elif dbworker.check_word_id_in_progress(dbworker.user_current_data_from_db(message.from_user.id)[2],
                                                    dbworker.user_current_data_from_db(message.from_user.id)[
                                                        3]) == 8:
                print('TEST: 8 returned to test mode. set interval - 9')
                dbworker.insert_user_progress_into_db(message.chat.id,
                                                      dbworker.user_current_data_from_db(message.from_user.id)[2],
                                                      9,
                                                      int(time.time()))
                bot.send_message(message.chat.id, '🎈🎉🎊🎉  Поздравляю! Слово выучено! 😃  🎉🎊🎉🎈')

            elif dbworker.check_word_id_in_progress(dbworker.user_current_data_from_db(message.from_user.id)[2],
                                                    dbworker.user_current_data_from_db(message.from_user.id)[
                                                        3]) == 9:
                print('9 returned to test mode. set interval - 9')
                dbworker.insert_user_progress_into_db(message.chat.id,
                                                      dbworker.user_current_data_from_db(message.from_user.id)[2],
                                                      9,
                                                      int(time.time()))
                bot.send_message(message.chat.id, 'Слово уже выучено...')

            # bot.send_message(message.chat.id, random.choice(emoji_gut) + ' ' + random.choice(words_gut))

            if int(dbworker.get_msg_counter(message.from_user.id)[0]) >= 20:
                time.sleep(1)
                bot.send_message(message.chat.id, links[random.randint(0, 2)])
                time.sleep(1.5)
                dbworker.reset_msg_counter(message.from_user.id)


            else:
                dbworker.increase_msg_counter(message.from_user.id)

            dbworker.select_and_update_user_current_word(message.from_user.id)
            bot.send_message(message.chat.id,
                             '❓  Переведи:  ' + '*' +
                             dbworker.user_current_data_from_db(message.from_user.id)[0] + '*',
                             reply_markup=dbworker.user_current_data_from_db(message.from_user.id)[4],
                             parse_mode="markdown")
            return

        elif message.text.lower() != dbworker.user_current_data_from_db(message.from_user.id)[1]:
            print('incorrect')

            # dbworker.check_word_id_in_progress(dbworker.user_current_data_from_db(message.from_user.id)[2],
            #                                    dbworker.user_current_data_from_db(message.from_user.id)[3])
            # if dbworker.check_word_id_in_progress(dbworker.user_current_data_from_db(message.from_user.id)[2],
            #                                       dbworker.user_current_data_from_db(message.from_user.id)[3]) is True:
            dbworker.insert_user_progress_into_db(message.chat.id,
                                                  dbworker.user_current_data_from_db(message.from_user.id)[2],
                                                  1,
                                                  int(time.time()))

            # elif dbworker.check_word_id_in_progress(
            #         dbworker.user_current_data_from_db(message.from_user.id)[2],
            #         dbworker.user_current_data_from_db(message.from_user.id)[3]) is False:
            #     dbworker.insert_user_progress_into_db(message.chat.id,
            #                                           dbworker.user_current_data_from_db(message.from_user.id)[2],
            #                                           1,
            #                                           int(time.time()))

            bot.send_message(message.chat.id,
                             '"' + (random.choice(motivation))[0] + '"\n\n' + random.choice(emoji_bad) +
                             ' Запомни перевод    \n' + '*' +
                             dbworker.user_current_data_from_db(message.from_user.id)[
                                 0] + '*' + ':  ' + '_' +
                             dbworker.user_current_data_from_db(message.from_user.id)[1] + '_',
                             parse_mode="markdown")

            if int(dbworker.get_msg_counter(message.from_user.id)[0]) >= 15:
                time.sleep(1)
                bot.send_message(message.chat.id, links[random.randint(0, 2)])
                time.sleep(1.5)
                dbworker.reset_msg_counter(message.from_user.id)

            else:
                dbworker.increase_msg_counter(message.from_user.id)

            dbworker.select_and_update_user_current_word(message.from_user.id)
            bot.send_message(message.chat.id,
                             '❓  Переведи:  ' + '*' +
                             dbworker.user_current_data_from_db(message.from_user.id)[0] + '*',
                             reply_markup=dbworker.user_current_data_from_db(message.from_user.id)[4],
                             parse_mode="markdown")
            return


@bot.message_handler(commands=['CARDS'])
def carding(message):
    bot.send_message(message.chat.id, '*Режим*:  _работа с карточками_', parse_mode='Markdown',
                     reply_markup=startCard_keyboard)
    dbworker.set_current_state(message.chat.id, config.States.S_CARDS.value)

    @bot.message_handler(content_types=['text'], func=lambda message: dbworker.get_current_state(
        message.chat.id) == config.States.S_CARDS.value)
    def nest_carding(message):

        if message.text == 'НАЧАТЬ 📚':
            dbworker.select_and_update_user_current_word_list(message.from_user.id)
            dbworker.cycl(message.from_user.id)

            card = bot.send_message(message.chat.id, '📖 *Слова для запоминания* 📖  \n\n'
                                    + '*' + dbworker.cycl(message.from_user.id)[0][1] + '* :    ' + '_' +
                                    dbworker.cycl(message.from_user.id)[0][
                                        2] + '_' + '\n'
                                    + '*' + dbworker.cycl(message.from_user.id)[1][1] + '* :    ' + '_' +
                                    dbworker.cycl(message.from_user.id)[1][
                                        2] + '_' + '\n'
                                    + '*' + dbworker.cycl(message.from_user.id)[2][1] + '* :    ' + '_' +
                                    dbworker.cycl(message.from_user.id)[2][
                                        2] + '_' + '\n'
                                    + '*' + dbworker.cycl(message.from_user.id)[3][1] + '* :    ' + '_' +
                                    dbworker.cycl(message.from_user.id)[3][
                                        2] + '_' + '\n'
                                    + '*' + dbworker.cycl(message.from_user.id)[4][1] + '* :    ' + '_' +
                                    dbworker.cycl(message.from_user.id)[4][
                                        2] + '_' + '\n'
                                    + '*' + dbworker.cycl(message.from_user.id)[5][1] + '* :    ' + '_' +
                                    dbworker.cycl(message.from_user.id)[5][
                                        2] + '_' + '\n'
                                    + '*' + dbworker.cycl(message.from_user.id)[6][1] + '* :    ' + '_' +
                                    dbworker.cycl(message.from_user.id)[6][
                                        2] + '_' + '\n'
                                    + '*' + dbworker.cycl(message.from_user.id)[7][1] + '* :    ' + '_' +
                                    dbworker.cycl(message.from_user.id)[7][
                                        2] + '_' + '\n'
                                    + '*' + dbworker.cycl(message.from_user.id)[8][1] + '* :    ' + '_' +
                                    dbworker.cycl(message.from_user.id)[8][
                                        2] + '_' + '\n'
                                    + '*' + dbworker.cycl(message.from_user.id)[9][1] + '* :    ' + '_' +
                                    dbworker.cycl(message.from_user.id)[9][
                                        2] + '_' + '\n'
                                    , parse_mode='Markdown', reply_markup=testKeyboard)

            dbworker.set_msg_id(message.chat.id, card.message_id)

        elif message.text == "ТЕСТ 📝":

            bot.delete_message(message.from_user.id, dbworker.get_msg_id(message.chat.id))

            dbworker.pop_user_current_word_list(message.from_user.id)
            bot.send_message(message.chat.id,
                             '❓  Переведи:  ' + '*' +
                             dbworker.user_current_data_from_db(message.from_user.id)[0] + '*',
                             reply_markup=dbworker.user_current_data_from_db(message.from_user.id)[4],
                             parse_mode="markdown")

            return

        elif message.text.lower() == dbworker.user_current_data_from_db(message.from_user.id)[1]:

            dbworker.check_word_id_in_progress(dbworker.user_current_data_from_db(message.from_user.id)[2],
                                               dbworker.user_current_data_from_db(message.from_user.id)[3])
            if dbworker.check_word_id_in_progress(dbworker.user_current_data_from_db(message.from_user.id)[2],
                                                  dbworker.user_current_data_from_db(message.from_user.id)[3]) is True:
                dbworker.insert_user_progress_into_db(message.chat.id,
                                                      dbworker.user_current_data_from_db(message.from_user.id)[2],
                                                      4,
                                                      int(time.time()))

            elif dbworker.check_word_id_in_progress(
                    dbworker.user_current_data_from_db(message.from_user.id)[2],
                    dbworker.user_current_data_from_db(message.from_user.id)[3]) is False:
                dbworker.insert_user_progress_into_db(message.chat.id,
                                                      dbworker.user_current_data_from_db(message.from_user.id)[2],
                                                      2,
                                                      int(time.time()))

            bot.send_message(message.chat.id, random.choice(emoji_gut) + ' ' + random.choice(words_gut))

            if dbworker.pop_user_current_word_list(message.from_user.id) is not False:
                bot.send_message(message.chat.id,
                                 '❓  Переведи:  ' + '*' +
                                 dbworker.user_current_data_from_db(message.from_user.id)[0] + '*',
                                 reply_markup=dbworker.user_current_data_from_db(message.from_user.id)[4],
                                 parse_mode="markdown", )
            else:
                markup = types.ReplyKeyboardRemove(selective=True)
                bot.send_message(message.chat.id, 'Урок пройден 🎓\n', reply_markup=markup)
                time.sleep(1)
                bot.send_message(message.chat.id, links[random.randint(0, 2)])
                bot.send_message(message.chat.id, 'Вернуться в меню /start')
                dbworker.set_current_state(message.chat.id, config.States.S_START.value)

        elif message.text.lower() != dbworker.user_current_data_from_db(message.from_user.id)[1]:

            dbworker.check_word_id_in_progress(dbworker.user_current_data_from_db(message.from_user.id)[2],
                                               dbworker.user_current_data_from_db(message.from_user.id)[3])
            if dbworker.check_word_id_in_progress(dbworker.user_current_data_from_db(message.from_user.id)[2],
                                                  dbworker.user_current_data_from_db(message.from_user.id)[3]) is True:
                dbworker.insert_user_progress_into_db(message.chat.id,
                                                      dbworker.user_current_data_from_db(message.from_user.id)[2],
                                                      1,
                                                      int(time.time()))

            elif dbworker.check_word_id_in_progress(
                    dbworker.user_current_data_from_db(message.from_user.id)[2],
                    dbworker.user_current_data_from_db(message.from_user.id)[3]) is False:
                dbworker.insert_user_progress_into_db(message.chat.id,
                                                      dbworker.user_current_data_from_db(message.from_user.id)[2],
                                                      1,
                                                      int(time.time()))

            bot.send_message(message.chat.id,
                             '"' + (random.choice(motivation))[0] + '"\n\n' + random.choice(emoji_bad)
                             ,
                             parse_mode="markdown")

            if dbworker.pop_user_current_word_list(message.from_user.id) is not False:
                bot.send_message(message.chat.id,
                                 '❓  Переведи:  ' + '*' +
                                 dbworker.user_current_data_from_db(message.from_user.id)[0] + '*',
                                 reply_markup=dbworker.user_current_data_from_db(message.from_user.id)[4],
                                 parse_mode="markdown")

            else:
                markup = types.ReplyKeyboardRemove(selective=True)
                bot.send_message(message.chat.id, 'Урок пройден 🎓\n', reply_markup=markup)
                time.sleep(1)
                bot.send_message(message.chat.id, links[random.randint(0, 2)])
                bot.send_message(message.chat.id, 'Вернуться в меню /start')
                dbworker.set_current_state(message.chat.id, config.States.S_START.value)


"""How can I handle reocurring ConnectionResetErrors?

Bot instances that were idle for a long time might be rejected by the server when sending a message due to a timeout 
of the last used session. Add apihelper.SESSION_TIME_TO_LIVE = 5 * 60 to your initialisation to force recreation 
after 5 minutes without any activity. """

apihelper.SESSION_TIME_TO_LIVE = 5 * 60
if __name__ == '__main__':
    print("bot running...")
    while True:
        try:
            bot.polling()


        except:
            time.sleep(2)
