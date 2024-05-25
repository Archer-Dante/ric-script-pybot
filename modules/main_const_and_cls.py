from modules.message_manager import get_phrase  # импорт своей функции по генерации фраз


class CommandsNames:
    BOTS_KICKED = "bots-kicked"
    TOGGLE = "toggle"
    CHECK_STREAM = "stream-check"


class Bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class FarewallManager:
    userid_list: list = []

    @classmethod
    def add_to_list(cls, userid: int):
        cls.userid_list.append(userid)
        return

    @classmethod
    def in_list(cls, userid: int):
        return True if userid in cls.userid_list else False

    @classmethod
    def remove_from_list(cls, userid):
        cls.userid_list.remove(userid)
        return

    @classmethod
    # принимает mention в виде строки и форматирует до конечного сообщения
    def get_formated_phrase(cls, user: str):
        return get_phrase("**" + user + "**")
