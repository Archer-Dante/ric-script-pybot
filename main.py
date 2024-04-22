# IMPORT DISCORD.PY. ALLOWS ACCESS TO DISCORD'S API.
import discord
import os
from dotenv import load_dotenv
from datetime import datetime

# импорт своего класса по работе с файлами
from modules.file_manager import FileAction
# импорт своей функции по генерации фраз
from modules.message_manager import get_phrase
# импорт результата отдельной загрузки для главного конфига
from modules.load_config import config

# LOADS THE .ENV FILE THAT RESIDES ON THE SAME LEVEL AS THE SCRIPT.
load_dotenv()
# GRAB THE API TOKEN FROM THE .ENV FILE.
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
# GETS THE CLIENT OBJECT FROM DISCORD.PY. CLIENT IS SYNONYMOUS WITH BOT.

intents = discord.Intents.default()
intents.members = True
bot = discord.Client(intents=intents)
# bot = discord.Client(intents=discord.Intents.default())

print(f'Выбранная локализация: {config["current_locale"]}')


class KickedTotal:
    # сколько всего кикнуто за текущую сессию
    value: int = 0

    @classmethod
    def increment(cls) -> str:
        cls.value += 1
        return f"{cls.value}) | "

    @classmethod
    def get_value(cls) -> int:
        cls.increment()
        return cls.value


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


# сообщение которое нужно заблочить
message_id_to_ban = 1072806217824600074
# канал где это сообщение для блока
channel_id_with_message = 925204884054229033
# какой смайл будет прокать работу кода
emoji_to_work_with = "<a:z_bye:1229599440352968725>"
emoji_to_work_with_id = 1229599440352968725
# кана куда писать прощальные сообщения
channel_id_to_farewall = 790367801532612619


# EVENT LISTENER FOR WHEN THE BOT HAS SWITCHED FROM OFFLINE TO ONLINE.
@bot.event
async def on_ready():
    # CREATES A COUNTER TO KEEP TRACK OF HOW MANY GUILDS / SERVERS THE BOT IS CONNECTED TO.
    guild_count = 0

    # LOOPS THROUGH ALL THE GUILD / SERVERS THAT THE BOT IS ASSOCIATED WITH.
    for guild in bot.guilds:
        # PRINT THE SERVER'S ID AND NAME.
        print(f"- {guild.id} (name: {guild.name})")

        # INCREMENTS THE GUILD COUNTER.
        guild_count = guild_count + 1

        FileAction.server_dir_check(guild.id)

    # PRINTS HOW MANY GUILDS / SERVERS THE BOT IS IN.
    print("SampleDiscordBot is in " + str(guild_count) + " guilds.\n")

    # т.к. нельзя получить сообщение без канала, а канал или сообщение без события, то зная ID канала
    # получаем сначала объект канала, потом объект сообщения, а потом ставим на него смайл указав ID смайла
    channel_obj = bot.get_channel(channel_id_with_message)
    message_obj = await channel_obj.fetch_message(message_id_to_ban)
    await message_obj.clear_reaction(emoji_to_work_with)
    try:
        await message_obj.add_reaction(emoji_to_work_with)
    except Exception as f:
        print("Ошибка: ", str(f))
    finally:
        pass


# EVENT LISTENER FOR WHEN A NEW MESSAGE IS SENT TO A CHANNEL.
@bot.event
async def on_message(message):
    # CHECKS IF THE MESSAGE THAT WAS SENT IS EQUAL TO "HELLO".
    if message.content == "blablapew":
        # SENDS BACK A MESSAGE TO THE CHANNEL.
        await message.channel.send("hey dirtbag")


@bot.event
# async def on_reaction_add(reaction, user): # только на новые сообщения
async def on_raw_reaction_add(reaction):  # должно работать даже на тех, что не в кэше
    if reaction.member.bot:
        return

    channel_id = bot.get_channel(reaction.channel_id)
    message_id = await channel_id.fetch_message(reaction.message_id)
    message_bdy = message_id.content

    time_string = f'{datetime.now().date().strftime("%d-%m-%Y")} - {datetime.now().time().strftime("%H:%M:%S")}'

    # голый запрос без await не успевает вернуться, вызывает ошибку
    print(
        f'{Bcolors.BOLD}Timestamp:{Bcolors.ENDC} {Bcolors.OKGREEN}{time_string}{Bcolors.ENDC}\n'
        f'{Bcolors.BOLD}ID Сервера:{Bcolors.ENDC} "{await bot.fetch_guild(reaction.guild_id)}" - {reaction.guild_id}\n'
        f'{Bcolors.BOLD}ID Сообщения:{Bcolors.ENDC} {reaction.message_id}\n'
        f'{Bcolors.BOLD}Эмодзи:{Bcolors.ENDC} <:{reaction.emoji.name}:{reaction.emoji.id}> \n'
        f'{Bcolors.BOLD}ID Юзера:{Bcolors.ENDC} {reaction.user_id} под ником {reaction.member.display_name} ({reaction.member.name})\n'
        f'{Bcolors.BOLD}Ссылка на сообщение:{Bcolors.ENDC}\n'
        f'https://discord.com/channels/{reaction.guild_id}/{reaction.channel_id}/{reaction.message_id}\n'
        f'{Bcolors.BOLD}Тело сообщения:{Bcolors.ENDC}\n{Bcolors.OKCYAN}{message_bdy}{Bcolors.ENDC}\n'
        f'{Bcolors.BOLD}Автор сообщения: {Bcolors.ENDC}{message_id.author.display_name} ({message_id.author.global_name})')

    # say_goodbye = get_phrase(reaction.member.display_name)
    # print(f'**{say_goodbye}**')
    # print(KickedTotal.get_value())

    for x in reaction.member.roles:
        if x.name == "Criminals":
            print(f"Обнаружен ставящий реакции {x}!")
            if reaction.message_id == 1072806217824600074 and reaction.emoji.id == emoji_to_work_with_id:
                print('Пока-пока!\n')
                guild_obj = await bot.fetch_guild(reaction.guild_id)
                channel_obj_farewall = await bot.fetch_channel(channel_id_to_farewall)

                if not FarewallManager.in_list(reaction.member.id):  # проверяем есть ли ИД в списке класса-менеджера
                    FarewallManager.add_to_list(reaction.member.id)  # добавляем если отсутствует

                await channel_obj_farewall.send(f'{FarewallManager.get_formated_phrase(reaction.member.mention)}')
                await channel_obj_farewall.send(f'- `подстрелено негодников: {KickedTotal.get_value()}`')
                await guild_obj.kick(reaction.member)

    print(f'\n\n')


@bot.event
async def on_member_remove(user_gone):
    # если в списке - убрать из списка и отменить дальнейшую процедуру
    # отмена нужна чтобы при повторном заходе выходе в пределах одной сессии бота он не помнил предыдущий случай
    print('Пользователь покинул сервер. Был ли обработан в другом событии: ')
    if FarewallManager.in_list(user_gone.id):
        print(f'Список ID до: {FarewallManager.userid_list}')
        FarewallManager.remove_from_list(user_gone.id)
        print(f'Да, под ID {user_gone.id} его кикнул РИК-Бот. Теперь пользователь удалён из списка.')
        print(f'Список ID после: {FarewallManager.userid_list}')
        return
    print('Нет, он вышел сам или был кикнут вручную.')

    # получение канала куда постить
    channel_obj_farewall = await bot.fetch_channel(channel_id_to_farewall)
    # отправка сообщения, делая запрос в класс, который в свою очередь запрашивает рандом из другой функции
    # и возвращает форматированный и готовый к отправке вариант
    await channel_obj_farewall.send(f'{FarewallManager.get_formated_phrase(user_gone.mention)}')
    print('Done')


# EXECUTES THE BOT WITH THE SPECIFIED TOKEN. TOKEN HAS BEEN REMOVED AND USED JUST AS AN EXAMPLE.

if __name__ == '__main__':
    bot.run(DISCORD_TOKEN)
