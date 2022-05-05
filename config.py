# token = "???" # superlangbot
# token = "???"  # test
token = "???"  #LangoSaurus

from enum import Enum
import sqlite3

db_file = "superlangbot.sqlite"


class States(Enum):
    S_START = "0"  # Начало нового диалога
    S_TEST = "1"
    S_CARDS = "2"
    S_REBOOT = "3"

