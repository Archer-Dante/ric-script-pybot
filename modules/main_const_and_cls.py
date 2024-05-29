from modules.message_manager import get_phrase  # импорт своей функции по генерации фраз


class CommandsNames:
    HELP = "help"
    BOTS_KICKED = "bots-kicked"
    TOGGLE = "toggle"
    STREAM = "stream"

    COMMANDS = (f'**Список доступных команд:**\n'
                f'\n'
                f'- `/help` - получить справку по командам\n'
                f'- `/bots-kicked` - посмотреть количество автоматически кикнутых ботов на сервере\n'
                f'- `/toggle (leave)` - включить/выключить оповещения о выходе человека с сервера'
                f'*(не применяется к оповещениям о автоматически кикнутых бот-аккаунтах)*\n'
                f'\n'
                f'- `/stream-post-to-channel (id)` - указать куда отправлять оповещения\n'
                f'- `/stream-add-channel (url)` - добавить канал в - список отслеживаемых\n'
                f'- `/stream-remove-channel (url)` - удалить канал из списка отслеживаемых\n'
                f'- `/toggle notify-stream` - включить/выключить оповещения о стримах\n'
                f'- `/stream-list` - показать весь список отслеживаемых стрим-каналов\n')






class SettingsName:
    pass


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
