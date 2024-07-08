from modules.message_manager import get_phrase  # импорт своей функции по генерации фраз


class CommandsNames:
    HELP = "help"
    BOTS_KICKED = "bots-kicked"
    MODERATION = "mod"
    AUTOKICK = "autokick"
    DAILY = "daily"
    TOGGLE = "toggle"
    STREAM = "stream"
    MOVE = "move"
    COPY = "copy"
    ADDSTREAM = "addstream"
    CLEAR = "clear"
    TRANSLATE = "tt"
    LANG = "lang"
    EMBED = "embed"
    EMBED_EDIT = "embed-edit"
    SYNC = "sync"

    COMMANDS = (f'**Список доступных команд:**\n'
                f'\n'
                f'- `/help` - получить справку по командам\n'
                f'- `/bots-kicked` - посмотреть количество автоматически кикнутых ботов на сервере\n'
                f'- `/toggle (leave)` - включить/выключить оповещения о выходе человека с сервера'
                f'*(не применяется к оповещениям о автоматически кикнутых бот-аккаунтах)*\n'
                f'\n'
                f'- `/stream-post-to-channel [id]` - указать куда отправлять оповещения\n'
                f'- `/stream-add-channel [url]` - добавить канал в список отслеживаемых\n'
                f'- `/stream-remove-channel [url]` - удалить канал из списка отслеживаемых\n'
                f'- `/toggle notify-stream` - включить/выключить оповещения о стримах\n'
                f'- `/stream-list` - показать весь список отслеживаемых стрим-каналов\n'
                f'\n'
                f'- `/addstream [url]` - добавить канал в список отслеживаемых (для пользователя)\n'
                f'- `/toggle allow-user-streams` - переключить возможность использовать комманду /addstream\n'
                f'\n'
                f'- `/autokick setup-trap [message_url] [emoji]` - установить ловушку, при нажатии на которую юзера-бота кикнет\n'
                f'- `/autokick remove-traps [message_url]` - удалить с указанного сообщения все ловушки\n'
                f'- `/autokick required-role [id | @user_mention]` - добавить требуемую роль для срабатывания ловушки\n' 
                f'- `/autokick notify-here [channel_id | #channel_mention]` - место, куда оповещать о авто-киках\n'
                f'- `/autokick ban-instead [yes | no]` - включить бан вместо кика при срабатывании ловушки\n' 
                f'- `/autokick clear-all` - удалить все реакции-ловушки с сервера, и все поставленные на них реакции\n'
                f'\n'
                f'- `/move [начальное сообщение] [конечное сообщение] [канал куда перенести] - перенос сообщений (удаляет оригиналы)\n'
                f'- `/copy [начальное сообщение] [конечное сообщение] [канал куда перенести] - копирование сообщений (не удаляет оригиналы)\n'
                f'- `/clear [начальное сообщение] [конечное сообщение] - удалить сообщения\n'
                f'\n'
                f'- `/lang [ru | en | pl | pt]` - переключить язык на который переводить текст при ПКМ - Приложения - Translate It\n'
                f'')






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


class CachedBans:
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
