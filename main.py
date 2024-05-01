# IMPORT DISCORD.PY. ALLOWS ACCESS TO DISCORD'S API.
import pathlib
import sys
import urllib.request

import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
from datetime import datetime
import json
import configparser

from modules.web_manager import progress_bar

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

# юзерагент для запросов на скачку
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# intents = discord.Intents.default()
# intents.members = True
# bot = discord.Client(intents=intents)
bot = commands.Bot(command_prefix=".", intents=discord.Intents.all())

print(f'Выбранная локализация: {config["current_locale"]}')

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

class ServerDataInterface:
    data: dict[str] = {}

    def __init__(self, server_id):

        server_id = str(server_id)
        self.data[server_id]: dict = {}  # print(self.data)
        self.config_dir = pathlib.Path(os.path.join(config["server_data_path"], server_id))  # print(self.config_dir)
        # self.data[str(server_id)]["server_path"] = str(self.config_dir)
        # self.data[str(server_id)]["config_files"]: dict = {}
        # self.data[str(server_id)]["config_files"]["settings.json"] = {"path_to_file":{}}
        # self.data[str(server_id)]["config_files"]["settings.json"]["path_to_file"] = {}

        for file_path in self.config_dir.glob('*'):
            # выборка чтобы только json и только не пустые файлы
            if str(file_path).find(".json") >= 0 and os.path.getsize(file_path) >= 0:
                print(file_path)
                section = file_path.stem
                with FileAction(file_path, "r") as file:
                    try:
                        cfg = json.loads(file.read())
                        self.root_sid(server_id)[section] = cfg
                    except Exception as e:
                        print(f'{Bcolors.WARNING}Не удалось спарсить {file.name} '
                              f'- возможно файл не соответствует стандарту или пустой{Bcolors.ENDC}')

        print("")

    # путь до корня текущего сервера
    def root_sid(self, s_id) -> object:
        return self.data[s_id]
        pass

    # переработать в get_что-то с вызовом одной и той же функции, где достаётся значение согласно опции
    @classmethod
    def get_stats(cls, s_id, search_for_key):
        cfg_branch = cls.data[str(s_id)]["stats"]
        # print(cfg_branch)
        value = cfg_branch.get(search_for_key, None)
        if value is None:
            return f'<Ошибка: значение не найдено>'
        else:
            return value

    @classmethod
    def save_cfgs(cls, s_id):
        print(str(s_id))
        print(cls.data)
        for cfg in cls.data[str(s_id)]:
            # if cfg == "settings":
            save_path = os.path.join(config["server_data_path"], str(s_id), cfg)
            with FileAction(f'{save_path}.json', "w") as json_file:
                try:
                    # cls.autokick_toggle(cls, s_id)
                    json.dump(cls.data[str(s_id)][cfg], json_file, indent=8)
                except Exception as e:
                    print(f"Ошибка: {e}")
                    json.dump(cls.data[str(s_id)][cfg], json_file, indent=8)
                    # Здесь вы можете добавить логику для обработки ошибки, например, не перезаписывать файл
        pass

    @staticmethod
    def autokick_toggle(cls, s_id):
        value = cls.data[str(s_id)]["settings"]["autokick"]
        print(f'Было: {value[0]}, сервер {s_id}')
        if int(value[0]) == 1:
            value[0] = "0"
        else:
            value[0] = "1"
        print(f'Было: {value[0]}, сервер {s_id}')
        pass

    @classmethod
    def autokick_increase(cls, s_id):
        cfg_branch = cls.data[str(s_id)]["stats"]
        value = cfg_branch["autokick_count"]
        print("Было: ", value[0])
        cfg_branch["autokick_count"] = str(int(value) + 1)
        print("Стало после нового кика: ", value[0])
        print("Секция конфига: \n", cls.data[str(s_id)]["stats"])
        cls.save_cfgs(s_id)
        pass


# ServerDataInterface(364527877716443148)
# ServerDataInterface(846356735487770627)
# print(json.dumps(ServerDataInterface.data, indent=4))
# ServerDataInterface.save_cfgs(364527877716443148)
# ServerDataInterface.autokick_increase(364527877716443148)
# print(ServerDataInterface.get_stats(364527877716443148, "autokick_count") )

# sys.exit()


@bot.event
async def on_ready():
    guild_count = 0

    # перебор всех гильдий где находится бот, и создание для них папок в случае их отсутствия
    for guild in bot.guilds:
        # PRINT THE SERVER'S ID AND NAME.
        print(f"- {guild.id} (name: {guild.name})")

        # INCREMENTS THE GUILD COUNTER.
        guild_count = guild_count + 1

        FileAction.server_files_check(guild.id)
        ServerDataInterface(guild.id)
        # SavedServerData.get_autokicked_total_value(os.path.join(config["server_data_path"],str(guild.id),"stats","stats.json"))

    # Всего гильдий
    print("Бот находится в " + str(guild_count) + " гильдиях.\n")

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

    # import urllib.request as web
    # current_avatar = bot.user.avatar
    # print(f'{current_avatar.key}\n{current_avatar.url}')
    # file_url = current_avatar.url[0:current_avatar.url.find("?")]
    # print(f'{file_url}')
    # web.urlretrieve(file_url, current_avatar.key + ".png", progress_bar)

    # import requests
    # response = requests.get(file_url, headers=headers)
    # if response.status_code == 200:
    #     FileAction(f'{current_avatar.key}.png', "wb", response.content)
    #     print(f"Аватар сохранен как {current_avatar.key}.png")
    # else:
    #     print(f"Ошибка при загрузке аватара: {response.status_code}")

    # выгрузка аватара
    # with open("cat.gif", "rb") as f:
    #     new_avatar = f.read()
    # await bot.user.edit(avatar=new_avatar)

    # добавление команд в обработку дисом
    try:
        commands_list = await bot.tree.sync()
        print(f'Синхронизировано команд: {len(commands_list)} - {commands_list}')
    except Exception as e:
        print(e)


@bot.hybrid_command(name="daily")
async def test(ctx):
    await ctx.send("Daily yet not implemented! Stay tuned!!")


# @bot.hybrid_group(fallback="get")
# async def tag(ctx, name):
#     await ctx.send(f"Showing tag: {name}")
#
# @tag.command()
# async def create(ctx, name):
#     await ctx.send(f"Created tag: {name}")

@bot.hybrid_command(name="bots-kicked")
async def test(ctx):
    # await ctx.send("Daily yet not implemented! Stay tuned!!")
    # print(ctx.guild_id)
    try:
        await ctx.send(f"`Всего ботов наказано: {ServerDataInterface.get_stats(ctx.guild.id,'autokick_count')}`")
    except Exception as e:
        print(e)


# @bot.hybrid_group(fallback="get")
# async def tag(ctx, name):
#     await ctx.send(f"Showing tag: {name}")
#
# @tag.command()
# async def create(ctx, name):
#     await ctx.send(f"Created tag: {name}")


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
                ServerDataInterface.autokick_increase(reaction.guild_id)
                kicked_total = ServerDataInterface.get_stats(reaction.guild_id, "autokick_count")
                await channel_obj_farewall.send(f'- `подстрелено негодников: {kicked_total}`')
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


if __name__ == '__main__':
    bot.run(DISCORD_TOKEN)
