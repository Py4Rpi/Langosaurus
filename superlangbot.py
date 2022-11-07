#!/usr/bin/python
# -*- coding: UTF-8 -*-
import dbworker
import config
import time
from datetime import datetime
import random
import sqlite3
import telebot
from telebot import types
from telebot import apihelper
import schedule
from threading import Thread

'''
FUTURE AUDIO FILE FEATURE

bot.send_voice(737422517, open('abandon.ogg', 'rb'), '*abandon*:   _покидать_\n\nəˈbandən', parse_mode='Markdown')
bot.send_photo(737422517, open('abandon.jpg', 'rb'))
'''

bot = telebot.TeleBot(config.token)

main_keyboard = telebot.types.ReplyKeyboardMarkup()
main_keyboard.row('/TEST', '/CARDS')
startTest_keyboard = telebot.types.ReplyKeyboardMarkup()
startTest_keyboard.row('СТАРТ 🏁')
startCard_keyboard = telebot.types.ReplyKeyboardMarkup()
startCard_keyboard.row('НАЧАТЬ 📚')
testKeyboard = telebot.types.ReplyKeyboardMarkup()
testKeyboard.row("ТЕСТ 📝")


def ask_word(mcid, usr_data, usr_id):
    bot.send_message(mcid, f'❓  Переведи:  *{usr_data(usr_id)[0]}*',
                     reply_markup=usr_data(usr_id)[4],
                     parse_mode="markdown")


@bot.message_handler(commands=['sudo_reboot'])
def reboot(message):
    print('reboot command.')
    dbworker.set_reboot_state(config.States.S_REBOOT.value)


@bot.message_handler(commands=['sudo_get_users'])
def reboot(message):
    print('get users command.')
    bot.send_message(message.chat.id, f'All users info:\n {dbworker.get_all_users_info__admin()}\n',
                     parse_mode="Markdown")


@bot.message_handler(commands=['START', 'start'])
def start(message):
    dbworker.set_current_state(message.chat.id, config.States.S_START.value)
    bot.send_message(message.chat.id, f'<b>Привет  </b> {message.from_user.first_name}\n\n'
                                      f'Для просмотра отчета о процессе обучения введи - /progress\n\n'
                                      f'Для возврата в меню из любого режима введи - /start\n\n\n'
                                      f'<b>Выбери режим работы:</b>\n\n'
                                      f'😎  тест без подготовки  -  /TEST\n\n'
                                      f'🤓  работа с карточками  -  /CARDS', parse_mode='html',
                     reply_markup=main_keyboard)
    print(message.from_user.first_name, message.chat.id,
          datetime.utcfromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S'))
    dbworker.insert_new_user_into_db(message.chat.id, message.from_user.first_name,
                                     datetime.utcfromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S'))

    dbworker.test_reminder_msg(message.from_user.id)


@bot.message_handler(commands=['progress'])
def show_progress_command(message):
    progress_chk = dbworker.progress_check(message.chat.id)
    bot.send_message(message.chat.id, f'{progress_chk[1]}  - слов выучено\n'
                                      f'{int((progress_chk[1]) / 42.45)} %  '
                                      f'{"⭐" * (int(int((int(progress_chk[1])) / 42.45) / 10))} \n\n'
                                      f'{(progress_chk[0])}  - слов в процессе изучения\n'
                                      f'{int((progress_chk[0]) / 42.45)} %  '
                                      f'{"🔎" * (int(int((int(progress_chk[0])) / 42.45) / 10))}  \n\n'
                                      f'{4245 - int(progress_chk[2])}  - слов осталость в базе \n'
                                      f'{int((4245 - int(progress_chk[2])) / 42.45)} %  '
                                      f'{"📚" * (int(int((4245 - int(progress_chk[2])) / 42.45) / 10))}')


@bot.message_handler(commands=['TEST'])
def test_mode(message):
    mcid = message.chat.id
    usr_data = dbworker.user_current_data_from_db
    usr_id = message.from_user.id
    usr_progress = dbworker.check_word_id_in_progress
    usr_prog_insert = dbworker.insert_user_progress_into_db
    bot.send_message(message.chat.id, '*Режим*:  _тест без подготовки_',
                     parse_mode='Markdown',
                     reply_markup=startTest_keyboard)
    dbworker.set_current_state(message.chat.id, config.States.S_TEST.value)

    @bot.message_handler(content_types=['text'],
                         func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_TEST.value)
    def nested_test_mode(message):

        if message.text == 'СТАРТ 🏁':

            dbworker.reset_msg_counter(message.from_user.id)
            dbworker.select_and_update_user_current_word(message.from_user.id)

            ask_word(mcid, usr_data, usr_id)



        elif message.text.lower() == usr_data(usr_id)[1]:

            if usr_progress(usr_data(usr_id)[2], usr_data(usr_id)[3]) is False:

                usr_prog_insert(message.chat.id, usr_data(usr_id)[2], 172800, int(time.time()))
                bot.send_message(message.chat.id,
                                 random.choice(dbworker.emoji_win()[0]) + ' ' + random.choice(dbworker.words_win()[0]))

            elif usr_progress(usr_data(usr_id)[2], usr_data(usr_id)[3]) == 86400:

                usr_prog_insert(message.chat.id, usr_data(usr_id)[2], 172800, int(time.time()))
                bot.send_message(message.chat.id,
                                 random.choice(dbworker.emoji_win()[0]) + ' ' + random.choice(dbworker.words_win()[0]))

            elif usr_progress(usr_data(usr_id)[2], usr_data(usr_id)[3]) == 172800:

                usr_prog_insert(message.chat.id, usr_data(usr_id)[2], 345600, int(time.time()))
                bot.send_message(message.chat.id,
                                 random.choice(dbworker.emoji_win()[0]) + ' ' + random.choice(dbworker.words_win()[0]))

            elif usr_progress(usr_data(usr_id)[2], usr_data(usr_id)[3]) == 345600:

                usr_prog_insert(message.chat.id, usr_data(usr_id)[2], 691200, int(time.time()))
                bot.send_message(message.chat.id,
                                 random.choice(dbworker.emoji_win()[0]) + ' ' + random.choice(dbworker.words_win()[0]))

            elif usr_progress(usr_data(usr_id)[2], usr_data(usr_id)[3]) == 691200:

                usr_prog_insert(message.chat.id, usr_data(usr_id)[2], 777600, int(time.time()))
                bot.send_message(message.chat.id, '🎈🎉🎊🎉  Поздравляю! Слово выучено! 😃  🎉🎊🎉🎈')

            elif usr_progress(usr_data(usr_id)[2], usr_data(usr_id)[3]) == 777600:

                usr_prog_insert(message.chat.id, usr_data(usr_id)[2], 777600, int(time.time()))
                bot.send_message(message.chat.id, 'Слово уже выучено...')

            if int(dbworker.get_msg_counter(message.from_user.id)[0]) >= 20:
                time.sleep(1)
                bot.send_message(message.chat.id, dbworker.links()[random.randint(0, 2)])
                time.sleep(1.5)
                dbworker.reset_msg_counter(message.from_user.id)

            else:
                dbworker.increase_msg_counter(message.from_user.id)

            dbworker.select_and_update_user_current_word(message.from_user.id)
            ask_word(mcid, usr_data, usr_id)

        elif message.text.lower() != usr_data(usr_id)[1]:

            usr_prog_insert(message.chat.id, usr_data(usr_id)[2], 86400, int(time.time()))

            bot.send_message(message.chat.id,
                             f'{random.choice(dbworker.emoji_lost()[0])}\n\n{random.choice(dbworker.motivation()[0])}\n\nЗапомни перевод\n'
                             f'*{usr_data(usr_id)[0]}* : _{usr_data(usr_id)[1]}_', parse_mode="markdown")

            if int(dbworker.get_msg_counter(message.from_user.id)[0]) >= 15:
                time.sleep(1)
                bot.send_message(message.chat.id, dbworker.links()[random.randint(0, 2)])
                time.sleep(1.5)
                dbworker.reset_msg_counter(message.from_user.id)

            else:
                dbworker.increase_msg_counter(message.from_user.id)

            dbworker.select_and_update_user_current_word(message.from_user.id)
            ask_word(mcid, usr_data, usr_id)


@bot.message_handler(commands=['CARDS'])
def carding(message):
    mcid = message.chat.id
    usr_data = dbworker.user_current_data_from_db
    usr_id = message.from_user.id
    usr_progress = dbworker.check_word_id_in_progress
    usr_prog_insert = dbworker.insert_user_progress_into_db
    bot.send_message(message.chat.id, '*Режим*:  _работа с карточками_', parse_mode='Markdown',
                     reply_markup=startCard_keyboard)
    dbworker.set_current_state(message.chat.id, config.States.S_CARDS.value)

    @bot.message_handler(content_types=['text'], func=lambda message: dbworker.get_current_state(message.chat.id)
                                                                      == config.States.S_CARDS.value)
    def nest_carding(message):
        def lesson_over():

            markup = types.ReplyKeyboardRemove(selective=True)
            bot.send_message(message.chat.id, 'Урок пройден 🎓\n', reply_markup=markup)
            time.sleep(1)
            bot.send_message(message.chat.id, dbworker.links()[random.randint(0, 2)])
            bot.send_message(message.chat.id, 'Вернуться в меню /start')
            dbworker.set_current_state(message.chat.id, config.States.S_START.value)

        if message.text == 'НАЧАТЬ 📚':

            dbworker.select_and_update_user_current_word_list(message.from_user.id)
            dbworker.cycl(message.from_user.id)
            cycl = dbworker.cycl(message.from_user.id)

            card = bot.send_message(message.chat.id, '📖 *Слова для запоминания* 📖  \n\n'
                                                     f'*{cycl[0][1]}*:    _{cycl[0][2]} _ \n'
                                                     f'*{cycl[1][1]}*:    _{cycl[1][2]} _ \n'
                                                     f'*{cycl[2][1]}*:    _{cycl[2][2]} _ \n'
                                                     f'*{cycl[3][1]}*:    _{cycl[3][2]} _ \n'
                                                     f'*{cycl[4][1]}*:    _{cycl[4][2]} _ \n'
                                                     f'*{cycl[5][1]}*:    _{cycl[5][2]} _ \n'
                                                     f'*{cycl[6][1]}*:    _{cycl[6][2]} _ \n'
                                                     f'*{cycl[7][1]}*:    _{cycl[7][2]} _ \n'
                                                     f'*{cycl[8][1]}*:    _{cycl[8][2]} _ \n'
                                                     f'*{cycl[9][1]}*:    _{cycl[9][2]} _ \n',
                                    reply_markup=testKeyboard,
                                    parse_mode='markdown')

            dbworker.set_msg_id(message.chat.id, card.message_id)

        elif message.text == "ТЕСТ 📝":

            bot.delete_message(message.from_user.id, dbworker.get_msg_id(message.chat.id))

            dbworker.pop_user_current_word_list(message.from_user.id)
            ask_word(mcid, usr_data, usr_id)

        elif message.text.lower() == usr_data(usr_id)[1]:

            usr_progress(usr_data(usr_id)[2], usr_data(usr_id)[3])
            if usr_progress(usr_data(usr_id)[2], usr_data(usr_id)[3]) is True:
                usr_prog_insert(message.chat.id, usr_data(usr_id)[2], 345600, int(time.time()))

            elif usr_progress(usr_data(usr_id)[2], usr_data(usr_id)[3]) is False:
                usr_prog_insert(message.chat.id, usr_data(usr_id)[2], 172800, int(time.time()))

            bot.send_message(message.chat.id,
                             random.choice(dbworker.emoji_win()[0]) + ' ' + random.choice(dbworker.words_win()[0]))

            if dbworker.pop_user_current_word_list(message.from_user.id) is not False:
                ask_word(mcid, usr_data, usr_id)
            else:
                lesson_over()

        elif message.text.lower() != usr_data(usr_id)[1]:

            usr_progress(usr_data(usr_id)[2], usr_data(usr_id)[3])
            if usr_progress(usr_data(usr_id)[2], usr_data(usr_id)[3]) is True:
                usr_prog_insert(message.chat.id, usr_data(usr_id)[2], 86400, int(time.time()))

            elif usr_progress(
                    usr_data(message.from_user.id)[2],
                    usr_data(message.from_user.id)[3]) is False:
                usr_prog_insert(message.chat.id,
                                usr_data(message.from_user.id)[2],
                                86400,
                                int(time.time()))

            bot.send_message(message.chat.id,
                             f'{random.choice(dbworker.emoji_lost()[0])}\n\n{random.choice(dbworker.motivation()[0])}',
                             parse_mode="markdown")

            if dbworker.pop_user_current_word_list(message.from_user.id) is not False:
                ask_word(mcid, usr_data, usr_id)

            else:
                lesson_over()


@bot.message_handler(content_types=['text'],
                     func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_REBOOT.value)
def reboot_msg(message):
    bot.send_message(message.from_user.id,
                     '🛠️ Проводились технические работы. Приносим извинения за предоставленные неудобства. 😉 ⚙',
                     disable_notification=True)
    time.sleep(2)
    return start(message)


def schedule_checker():
    while True:
        schedule.run_pending()
        time.sleep(1)


def msg_itself(user_id):
    db = sqlite3.connect("superlangbot.sqlite")
    cursor = db.cursor()
    cursor.execute('SELECT intervals, repeat_date FROM progress WHERE (user_id=?)', (user_id,))
    entry = cursor.fetchall()
    db.close()

    def loop():
        for row in entry:
            if row[0] + row[1] <= int(time.time()):
                return True

    if loop() is True:
        return bot.send_message(user_id, 'Появились слова для повторения. Рекомендуется пройти тест. /TEST')
    else:
        pass


apihelper.SESSION_TIME_TO_LIVE = 5 * 60

if __name__ == '__main__':
    print("Langosaurus running...")
    Thread(target=schedule_checker).start()
    while True:
        try:
            bot.polling()
        except:
            time.sleep(2)
