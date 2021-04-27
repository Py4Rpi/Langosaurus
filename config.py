# token = "1756142897:AAGNvo64_LP2FLSYcU0V-V5giaE9femaW_Q" # superlangbot
# token = "1646801741:AAG5euit4OcfRGXzZJS3Ch5r4x_LI2ZodrQ"  # test
token = "1589590128:AAG7he3PT-rPBsuum14tzPnjl42uUMMrFxs"  #LangoSaurus

from enum import Enum
import sqlite3

db_file = "superlangbot.sqlite"


class States(Enum):
    S_START = "0"  # Начало нового диалога
    S_TEST = "1"
    S_CARDS = "2"
    S_REBOOT = "3"

