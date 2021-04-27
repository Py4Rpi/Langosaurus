import asyncio
import time
import config
import sqlite3
import re
import random
import telebot
import superlangbot
from datetime import datetime, timedelta


# from apscheduler.events import EVENT_JOB_EXECUTED
# from apscheduler.schedulers.blocking import BlockingScheduler


def set_reboot_state(value):
    database = sqlite3.connect("superlangbot.sqlite")
    cursor = database.cursor()
    cursor.execute("UPDATE users SET state = ?",
                   (value,))
    database.commit()
    database.close()
    return True


# Пытаемся узнать из базы «состояние» пользователя
def get_current_state(user_id):
    try:
        database = sqlite3.connect("superlangbot.sqlite")
        cursor = database.cursor()
        cursor.execute("SELECT state FROM users WHERE user_id = ?", (user_id,))
        state = cursor.fetchone()
        database.close()

        return state[0]
    except KeyError:

        # Если такого ключа почему-то не оказалось
        return config.States.S_START.value  # значение по умолчанию - начало диалога


# Сохраняем текущее «состояние» пользователя в нашу базу
def set_current_state(user_id, value):
    database = sqlite3.connect("superlangbot.sqlite")
    cursor = database.cursor()
    cursor.execute("UPDATE users SET state = ? WHERE user_id = ?",
                   (value, user_id))
    database.commit()
    database.close()
    return True


def set_msg_id(user_id, value):
    database = sqlite3.connect("superlangbot.sqlite")
    cursor = database.cursor()
    cursor.execute("UPDATE users SET msg_id = ? WHERE user_id = ?",
                   (value, user_id))
    database.commit()
    database.close()
    return True


def get_msg_id(user_id):
    database = sqlite3.connect("superlangbot.sqlite")
    cursor = database.cursor()
    cursor.execute("SELECT msg_id FROM users WHERE user_id = ?", (user_id,))
    msg_id = cursor.fetchone()
    database.close()

    return msg_id[0]


def reset_msg_counter(user_id):
    database = sqlite3.connect("superlangbot.sqlite")
    cursor = database.cursor()
    cursor.execute("UPDATE users SET msg_counter = ? WHERE user_id = ?",
                   (1, user_id))
    database.commit()
    database.close()
    return True


def increase_msg_counter(user_id):
    database = sqlite3.connect("superlangbot.sqlite")
    cursor = database.cursor()
    cursor.execute("UPDATE users SET msg_counter = msg_counter + 1 WHERE user_id = ?",
                   (user_id,))
    database.commit()
    database.close()
    return True


def get_msg_counter(user_id):
    database = sqlite3.connect("superlangbot.sqlite")
    cursor = database.cursor()
    cursor.execute("SELECT msg_counter FROM users WHERE user_id = ?", (user_id,))
    msg_counter = cursor.fetchone()
    database.close()

    return msg_counter


def select_and_update_user_current_word(user_id):
    database = sqlite3.connect("superlangbot.sqlite")
    cursor = database.cursor()
    cursor.execute(
        'SELECT progress.user_id, progress.word_id, progress.intervals, progress.repeat_date, users.random_or_repeat '
        'FROM progress, users WHERE progress.user_id = ? ORDER BY random()',
        (user_id,))
    progress_data = cursor.fetchall()
    print('SELECT: selected data from progress table')
    print(progress_data)
    if progress_data:

        for row in progress_data:
            print('SELECT: check for interval words in progress data')
            if row[2] == 1 and row[3] + 86400 <= time.time() and row[4] == 1:
                print('SELECT: found interval 1')
                cursor.execute("UPDATE users SET current_word_id = ?, random_or_repeat = ? WHERE user_id = ?",
                               (row[1], 0, user_id))
                print('SELECT: switch set to random - 0')
                database.commit()
                database.close()
                return

            elif row[2] == 2 and row[3] + 172800 <= time.time() and row[4] == 1:
                print('SELECT: found interval 2')
                cursor.execute("UPDATE users SET current_word_id = ?, random_or_repeat = ? WHERE user_id = ?",
                               (row[1], 0, user_id))
                print('SELECT: switch set to random - 0')
                database.commit()
                database.close()
                return

            elif row[2] == 4 and row[3] + 345600 <= time.time() and row[4] == 1:
                print('SELECT: found interval 4')
                cursor.execute("UPDATE users SET current_word_id = ?, random_or_repeat = ? WHERE user_id = ?",
                               (row[1], 0, user_id))
                print('SELECT: switch set to random - 0')
                database.commit()
                database.close()
                return

            elif row[2] == 8 and row[3] + 691200 <= time.time() and row[4] == 1:
                print('SELECT: found interval 8')
                cursor.execute("UPDATE users SET current_word_id = ?, random_or_repeat = ? WHERE user_id = ?",
                               (row[1], 0, user_id))
                print('SELECT: switch set to random - 0')
                database.commit()
                database.close()
                return


            else:
                print('SELECT: select random word in cycle and update current word id')
                cursor.execute(
                    "SELECT words.id, words.rate, words.eng, words.rus FROM words, progress WHERE words.id != progress.word_id ORDER BY random()")
                random_word_from_database = cursor.fetchone()
                cursor.execute("UPDATE users SET current_word_id = ?, random_or_repeat = ? WHERE user_id = ?",
                               (random_word_from_database[0], 1, user_id))
                print('SELECT: switch set to intervals - 1')
                database.commit()
                database.close()
                return

    else:
        print('SELECT: select random word outside cycle and update current word id')
        cursor.execute(
            "SELECT words.id, words.rate, words.eng, words.rus FROM words, progress WHERE words.id != progress.word_id ORDER BY random()")
        random_word_from_database = cursor.fetchone()
        cursor.execute("UPDATE users SET current_word_id = ?, random_or_repeat = ? WHERE user_id = ?",
                       (random_word_from_database[0], 1, user_id))
        print('SELECT: switch set to intervals - 1')
        database.commit()
        database.close()
        return

    return


def select_and_update_user_current_word_list(user_id):
    database = sqlite3.connect("superlangbot.sqlite")
    cursor = database.cursor()
    cursor.execute("SELECT words.id FROM words, progress WHERE words.id != progress.word_id ORDER BY random() LIMIT 10")
    list_of_10_words = cursor.fetchall()

    str_list_of_10_words = re.sub(r"[()\[,\]]", "", str(list_of_10_words))
    cursor.execute("UPDATE users SET current_ten_words_list = ? WHERE user_id = ?",
                   (str_list_of_10_words, user_id))
    database.commit()
    database.close()

    return list_of_10_words


def cycl(user_id):
    database = sqlite3.connect("superlangbot.sqlite")
    cursor = database.cursor()
    cursor.execute("SELECT current_ten_words_list FROM users WHERE (user_id=?)", (user_id,))
    str_ten_words_list = cursor.fetchone()
    cursor.execute(
        "SELECT id, eng, rus FROM words WHERE id IN (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ORDER BY id",
        (int(str_ten_words_list[0].split()[0]), int(str_ten_words_list[0].split()[1]),
         int(str_ten_words_list[0].split()[2]), int(str_ten_words_list[0].split()[3]),
         int(str_ten_words_list[0].split()[4]), int(str_ten_words_list[0].split()[5]),
         int(str_ten_words_list[0].split()[6]), int(str_ten_words_list[0].split()[7]),
         int(str_ten_words_list[0].split()[8]), int(str_ten_words_list[0].split()[9]),))

    ten_words_list = cursor.fetchall()
    database.close()
    return ten_words_list


def pop_user_current_word_list(user_id):
    database = sqlite3.connect("superlangbot.sqlite")
    cursor = database.cursor()
    cursor.execute("SELECT current_ten_words_list FROM users WHERE (user_id=?)", (user_id,))
    str_ten_words_list = cursor.fetchone()

    try:
        split_list = str_ten_words_list[0].split()
        pops = int(split_list.pop())
        back_to_str = re.sub(r"[()\[,\]']", "", str(split_list))
        cursor.execute("UPDATE users SET current_ten_words_list = ? WHERE user_id = ?",
                       (back_to_str, user_id))
        database.commit()
        cursor.execute("UPDATE users SET current_word_id = ? WHERE user_id = ?", (pops, user_id,))

        database.commit()
        database.close()
    except:
        return False


def user_current_data_from_db(user_id):
    database = sqlite3.connect("superlangbot.sqlite")
    cursor = database.cursor()
    cursor.execute("SELECT id, rate, eng, rus FROM words ORDER BY random() LIMIT 3")
    for_random_answers = cursor.fetchall()
    cursor.execute('SELECT words.id, words.eng, words.rus, users.current_word_id, users.user_id FROM words, users'
                   ' WHERE users.user_id = ? AND words.id =users.current_word_id', (user_id,))
    current_state = cursor.fetchone()
    database.close()

    word = current_state[1]
    correct = current_state[2]
    current_word_id = current_state[3]
    usrid = current_state[4]

    list_of_four_answers = [for_random_answers[0][3],
                            for_random_answers[1][3],
                            for_random_answers[2][3],
                            correct]
    random.shuffle(list_of_four_answers)
    answerkeyboard = telebot.types.ReplyKeyboardMarkup()
    answerkeyboard.row(list_of_four_answers.pop())
    answerkeyboard.row(list_of_four_answers.pop())
    answerkeyboard.row(list_of_four_answers.pop())
    answerkeyboard.row(list_of_four_answers.pop())

    return word, correct, current_word_id, usrid, answerkeyboard, for_random_answers


def check_word_id_in_progress(word_id, user_id):
    db = sqlite3.connect("superlangbot.sqlite")
    cursor = db.cursor()
    cursor.execute('SELECT word_id, intervals FROM progress WHERE user_id = ? and word_id = ?', (user_id, word_id))
    entry = cursor.fetchone()
    db.close()

    print('CHECK WORD: checking if word already in progress table or not')
    print(entry)
    if entry:
        if entry[0] == word_id:
            print('CHECK WORD: word id found in progress table')
            if entry[1] == 1:
                print('CHECK WORD: word already  exists in progress table with intreval 1')
                return 1
            elif entry[1] == 2:
                print('CHECK WORD: word already  exists in progress table with intreval  2')
                return 2
            elif entry[1] == 4:
                print('CHECK WORD: word already  exists in progress table with intreval  4')
                return 4
            elif entry[1] == 8:
                print('CHECK WORD: word already  exists in progress table with intreval  8')
                return 8
            elif entry[1] == 9:
                print('CHECK WORD: word already  exists in progress table with intreval  9')
                return 9
    else:

        print('CHECK WORD: word id not found in progress table ')
        return False


def progress_check(user_id):
    db = sqlite3.connect("superlangbot.sqlite")
    cursor = db.cursor()
    cursor.execute('SELECT intervals FROM progress WHERE (user_id=?)', (user_id,))
    entry = cursor.fetchall()
    db.close()
    in_progress = entry.count((1,)) + entry.count((2,)) + entry.count((4,)) + entry.count((8,))
    completed = entry.count((9,))
    all = in_progress + completed
    print(all)

    return in_progress, completed, all


def insert_new_user_into_db(usr_id, usr_name, msg_date):
    db = sqlite3.connect("superlangbot.sqlite")
    cursor = db.cursor()
    cursor.execute("INSERT INTO users (user_id, user_name_col, date_col) VALUES (?, ?, ?)",
                   (usr_id, usr_name, msg_date))
    db.commit()
    db.close()
    return


def insert_user_progress_into_db(usr_id, wrd_id, itrvl, msg_date):
    db = sqlite3.connect("superlangbot.sqlite")
    cursor = db.cursor()
    cursor.execute("INSERT INTO progress (user_id, word_id, intervals, repeat_date) VALUES (?, ?, ?, ?)",
                   (usr_id, wrd_id, itrvl, msg_date))
    db.commit()
    db.close()

    return


async def sched_msg(user_id):
    db = sqlite3.connect("superlangbot.sqlite")
    cursor = db.cursor()
    cursor.execute('SELECT repeat_date, intervals FROM progress WHERE (user_id=?)', (user_id,))
    entry = cursor.fetchall()
    db.close()
    if datetime.now() == datetime.now():
        superlangbot.schedule_msg(user_id)
    # for row in entry:
    #     if datetime.now() >= row[0] + timedelta(days=row[1]):
    #         superlangbot.schedule_msg(user_id)
    await asyncio.sleep(1)
