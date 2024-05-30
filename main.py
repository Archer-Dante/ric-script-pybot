import asyncio
import typing

import discord
from discord import app_commands, Colour
from discord.app_commands import Argument, Choice
from discord.ext import commands
import pathlib
import os
import json
from discord.ext.commands import BucketType
from dotenv import load_dotenv
from datetime import datetime
from modules.file_manager import FileAction  # импорт своего класса по работе с файлами
from modules.load_config import config  # импорт результата отдельной загрузки для главного конфига
from modules.main_const_and_cls import Bcolors  # импорт кодов цветов и форматирования для консоли
from modules.main_const_and_cls import CachedBans  # импорт генератора сообщений
from modules.main_const_and_cls import CommandsNames  # импорт названия команд из констант внутри класса
from modules.tools import get_average_color  # получение усреднённого цвета RGB

import requests
from bs4 import BeautifulSoup
from collections import defaultdict
from twitchAPI.twitch import Twitch

# import configparser
# from modules.web_manager import progress_bar

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# юзерагент для запросов
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

bot = commands.Bot(command_prefix="рик", intents=discord.Intents.all())

print(f'Выбранная локализация: {config["current_locale"]}')


class ServerDataInterface:
    data: dict[str] = {}
    yt_cache = defaultdict(list)
    tw_cache = defaultdict(list)

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
                    except Exception:
                        print(f'{Bcolors.WARNING}Не удалось спарсить {file.name}: '
                              f'- возможно файл не соответствует стандарту или пустой{Bcolors.ENDC}')

        print("")

    # путь до корня текущего сервера
    def root_sid(self, s_id) -> object:
        return self.data[s_id]
        pass

    # переработать в get_что-то с вызовом одной и той же функции, где достаётся значение согласно опции
    @classmethod
    def get_stats(cls, s_id, search_for_key):
        """
        Возвращает значение указанного параметра из файла stats.json
        Загружает значение из текущей памяти.
        :param s_id: id сервера-гильдии discord
        :param search_for_key: значение, которое нужно найти
        :return:
        """
        cfg_branch = cls.data[str(s_id)]["stats"]
        # print(cfg_branch)
        value = cfg_branch.get(search_for_key, None)
        if value is None:
            return f'<Ошибка: значение не найдено>'
        else:
            return value

    @classmethod
    def get_settings(cls, s_id, *args):
        cfg_branch = cls.data[str(s_id)]["settings"]
        for value in args:
            if value in cfg_branch:
                # print(cfg_branch[str(value)])
                cfg_branch = cfg_branch[value]
            else:
                # print(f'Значение {value} не найдено в {cfg_branch}')
                pass
        # print(cfg_branch)
        return cfg_branch

    @classmethod
    def set_settings(cls, s_id, changing_value, *args):
        cfg_branch = cls.data[str(s_id)]["settings"]
        for subbranch in args:
            if subbranch == args[-1]:  # последний элемент
                cfg_branch[subbranch] = changing_value
                # print(cfg_branch[subbranch])
            else:  # просто расширяем путь дальше и вглубь вложений
                cfg_branch = cfg_branch[subbranch]
                # print(cfg_branch)
        cls.save_cfgs(s_id)

    @classmethod
    def manage_list(cls, s_id, action, value_to_act_with, *args):
        """ Управление списками внутри указанного пути
        :param s_id: ID сервера
        :param action: add || remove
        :param value_to_act_with: с чем взаимодействовать
        :param args: путь до ключа-значения, где значение - список
        :return:
        """
        reply: str = ""
        cfg_branch = cls.data[str(s_id)]["settings"]
        for subbranch in args:
            if subbranch != args[-1]:
                cfg_branch = cfg_branch[subbranch]

        temp_list: list = cfg_branch[args[-1]]
        if action == "add":
            if not value_to_act_with in temp_list:
                temp_list.append(value_to_act_with)
                reply = "Канал успешно добавлен!"
            else:
                reply = "Такой канал уже есть в списке этого сервера"
        if action == "remove":
            if value_to_act_with in temp_list:
                temp_list.remove(value_to_act_with)
                reply = "Канал успешно удалён!"
            else:
                reply = f"Такого канала не было. Вы что-то путаете?\n\n Вот добавленные каналы на сервере:"
                for x in temp_list:
                    reply = reply + f"\n{x}"

        cls.save_cfgs(s_id)
        return reply

    @classmethod
    def get_stream_channels(cls, s_id):
        channels_list: str = ""
        cfg_branch = cls.data[str(s_id)]["settings"]["streams"]["streaming_channels"]
        for x in cfg_branch:
            channels_list = channels_list + f'\n{x}'
        return channels_list

    @classmethod
    def save_cfgs(cls, s_id):
        # print(str(s_id))
        # print(cls.data)
        for cfg in cls.data[str(s_id)]:
            save_path = os.path.join(config["server_data_path"], str(s_id), cfg)
            with FileAction(f'{save_path}.json', "w") as json_file:
                try:
                    # cls.autokick_toggle(cls, s_id)
                    json.dump(cls.data[str(s_id)][cfg], json_file, indent=8)
                except Exception as e:
                    print(f"Ошибка: {e}")
                    json.dump(cls.data[str(s_id)][cfg], json_file, indent=8)
        pass

    @classmethod
    def toggle_settings(cls, s_id, *args):
        """
        Переключает значение по указанному в *args пути в противоположное значение
        :param s_id: ID сервера
        :param args: аргументы, где каждый аргумент - вложение внутри настроек
        """
        cfg_branch = cls.data[str(s_id)]["settings"]
        for subbranch in args:
            if subbranch == args[-1]:  # последний элемент
                pass
            else:  # просто расширяем путь дальше и вглубь вложений
                cfg_branch = cfg_branch[subbranch]

        print(f'Было: {cfg_branch[args[-1]]}, сервер {s_id}')
        if cfg_branch[args[-1]] == "True":
            cfg_branch[args[-1]] = "False"
        else:
            cfg_branch[args[-1]] = "True"
        print(f'Стало: {cfg_branch[args[-1]]}, сервер {s_id}')
        print(json.dumps(cls.data[str(s_id)]["settings"], indent=8))
        cls.save_cfgs(s_id)
        pass

    # возможно следует сделать из этого "def toggle_dict", т.к. одним автокиком не обойтись, а структура данных
    # может использоваться для разных опций
    # либо нужен полный обработчик, который будет определять, если ли в паре КЛЮЧ-ЗНАЧЕНИЕ что-то глубже и сложнее
    # чем просто значение, а именно: словарь, список или кортеж.
    # если ничего из этого нет - простая обработка, если есть - сложнее.

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

    @classmethod
    def get_total_stream_checks(cls):
        youtube_channels = 0
        twitch_channels = 0
        for server in cls.data:
            if cls.data[server]["settings"]["notify"]["options"]["stream_starts"] == "True":
                for link in cls.data[server]["settings"]["streams"]["streaming_channels"]:
                    if "youtube" in link:
                        # print(f'Youtube канал {link} добавлен в отслеживание для сервера {server}')
                        youtube_channels = youtube_channels + 1
                    elif "twitch" in link:
                        twitch_channels = twitch_channels + 1
        return int(youtube_channels), int(twitch_channels)

    @classmethod
    def update_yt_cache(cls, ch_id, video):
        """
        Кэширует стримы, которые уже были опубликованы, чтобы не публиковаться повторно.
        Сбрасывается при перезапуске бота.
        :param ch_id: id канала, где был пост
        :param video: ссылка на видео или код видео
        """
        # cls.yt_cache.append(video)
        cls.yt_cache[ch_id].append(video)
        # print(cls.yt_cache)

    @classmethod
    def check_yt_cache(cls, ch_id, video):
        """
        Проверяет есть ли такое видео в кэше уже ранее опубликованных видео.
        Используется для проверки, чтобы избежать повторных постов.
        :param ch_id:
        :param video: ссылка на видео или код видео
        :return: Bool
        """
        cached = False
        for x in cls.yt_cache[ch_id]:
            if x == video:
                # print(f'Уже кешировано: {x}')
                cached = True
        return cached

    @classmethod
    def update_tw_cache(cls, ch_id, streamer):
        """
        Кэширует стримы, которые уже были опубликованы, чтобы не публиковаться повторно.
        Сбрасывается при перезапуске бота.
        :param ch_id: id канала, где был пост
        :param streamer: стример / логин стримера
        """
        cls.tw_cache[ch_id].append(streamer)

    @classmethod
    def check_tw_cache(cls, ch_id, streamer):
        """
        Проверяет есть ли такое видео в кэше уже ранее опубликованных видео.
        Используется для проверки, чтобы избежать повторных постов.
        :param ch_id:
        :param streamer: стример / логин стримера
        :return: Bool
        """
        cached = False
        for x in cls.tw_cache[ch_id]:
            if x == streamer:
                cached = True
        return cached

    @staticmethod
    async def get_channel_from_message_id(s_id, message_id):
        # channel = await SDI.get_channel_from_message_id(ctx.guild.id, int(msg_id))
        # if channel:
        #     print(f"Сообщение найдено в канале {channel.name}")
        # else:
        #     print("Сообщение не найдено")
        guild = bot.get_guild(s_id)
        if guild:
            for channel in guild.text_channels:
                try:
                    message = await channel.fetch_message(message_id)
                    if message:
                        return channel
                except discord.NotFound:
                    pass
                except discord.Forbidden:
                    pass
                except discord.HTTPException:
                    pass
        return None


SDI = ServerDataInterface  # сокращённый вариант


async def hybrid_cmd_router(ctx_or_msg, reply):
    embed = discord.Embed(
        description=reply,
        color=0xAC0000
    )
    # print(type(ctx_or_msg), ctx_or_msg)
    # print(type(reply), reply)
    try:
        if type(ctx_or_msg) is discord.ext.commands.context.Context:
            await ctx_or_msg.send(embed=embed)
        elif type(ctx_or_msg) is discord.message.Message:
            await ctx_or_msg.channel.send(embed=embed)
        elif type(ctx_or_msg) is discord.interactions.Interaction:
            await ctx_or_msg.response.send_message(embed=embed)
        elif type(ctx_or_msg) is discord.channel.TextChannel:
            await ctx_or_msg.send(embed=embed)
        else:
            raise Exception
    except Exception as e:
        print(f'Ошибка гибридной обёртки: {e}')


# sys.exit()

@bot.event
async def on_ready():
    activity = discord.Game(name="Thinking of next RIC tournament..?")
    await bot.change_presence(activity=activity)

    guild_count = 0

    for guild in bot.guilds:
        print(f"- {guild.id} (name: {guild.name})")
        guild_count = guild_count + 1
        FileAction.server_files_check(guild.id)
        ServerDataInterface(guild.id)

        # SDI.manage_list(guild.id,1,2, "streams", "streaming_channels")

    print("Бот находится в " + str(guild_count) + " гильдиях.\n")

    # т.к. нельзя получить сообщение без канала, а канал или сообщение без события, то зная ID канала
    # получаем сначала объект канала, потом объект сообщения, а потом ставим на него смайл указав ID смайла

    # channel_obj = bot.get_channel(channel_id_with_message)
    # message_obj = await channel_obj.fetch_message(message_id_to_ban)
    # await message_obj.clear_reaction(emoji_to_work_with)
    # try:
    #     await message_obj.add_reaction(emoji_to_work_with)
    # except Exception as f:
    #     print("Ошибка: ", str(f))
    # finally:
    #     pass

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

    try:
        commands_list = await bot.tree.sync()
        print(f'Синхронизировано команд: {len(commands_list)} - {commands_list}')
        # for x in commands_list: BotInterface.commands_list.append(x)
    except Exception as e:
        print(e)

    while True:
        total_stream_checks_awaits = SDI.get_total_stream_checks()
        print(sum(total_stream_checks_awaits))
        print(f'Всего стрим-каналов на обработке: {total_stream_checks_awaits}')
        global_cd = int(config["global_stream_check_cd"]) * sum(total_stream_checks_awaits)
        if global_cd == 0:
            print(f'Ни на одном сервере не включен постинг стримов. Отдыхаю.')
            await asyncio.sleep(120)
        else:
            await check_live_streams()
            # print(f'Ожидание глобального кулдауна {global_cd} с.')
            # await asyncio.sleep(global_cd)
            # print("=========== Запускаю следующий цикл проверок стримов ==================")


@bot.tree.command(name="help", description="Справка по командам")
@discord.ext.commands.guild_only()
async def cmd_helpinfo(ctx):
    reply = CommandsNames.COMMANDS
    await hybrid_cmd_router(ctx, reply)


@bot.hybrid_command(name=CommandsNames.DAILY, description="Получить ежедневный бонус")
@discord.ext.commands.guild_only()
async def cmd_daily(ctx):
    print("test")
    await ctx.send("Daily yet not implemented! Stay tuned!!")


@bot.hybrid_command(name=CommandsNames.AUTOKICK, description="Настроить систему автоматических киков")
@discord.ext.commands.guild_only()
@discord.ext.commands.has_permissions(administrator=True)
async def cmd_autokick(ctx, action: typing.Literal[
    "setup-trap", "remove-trap", "for-role", "ban-kicked", "notify-here", "clear-all"],
                       arg1: str = None, arg2: str = None
                       ):
    if action == "setup-trap":
        if arg1 is None or arg2 is None:
            await hybrid_cmd_router(ctx,
                                    f'Используя `{action}` нужно указывать оба аргумента: ссылку на сообщение и эмодзи!')
        else:
            print("Прошло")
            all_traps: list = SDI.get_settings(ctx.guild.id, "autokick", "trap_channels")
            msg = arg1
            react = arg2
            try:
                guild_id: str = msg.split("/")[4]
                channel_id: str = msg.split("/")[5]
                msg_id: str = msg.split("/")[6]
                react_id: str = (react.split(":")[2])[0:-1]

                if guild_id != str(ctx.guild.id):
                    raise ValueError(f"Нельзя ставить ловушки на другом сервере! Фу таким быть!")

                # for trap_data in all_traps:
                #   print(f'ID канала: {trap_data[0]}\nID сообщения: {trap_data[1]}\nID эмодзи: {trap_data[2]}\n')
                new_data = [channel_id, msg_id, react_id]
                all_traps.append(new_data)
                SDI.set_settings(ctx.guild.id, all_traps, "autokick", "trap_channels")

            except ValueError as e:
                await hybrid_cmd_router(ctx, str(e))


@bot.hybrid_command(name=CommandsNames.TOGGLE,
                    description="Переключить настройку в указанное или противоположное значение")
@commands.cooldown(1, 4, BucketType.user)
@discord.ext.commands.guild_only()
@discord.ext.commands.has_permissions(administrator=True)
async def cmd_toggle(ctx, setting: typing.Literal["notify-leave", "notify-stream"]):
    if setting == "notify-leave":
        SDI.toggle_settings(ctx.guild.id, "notify", "options", "member_quits")
        reply = f'Теперь настройка {setting} переключена в положение **{SDI.get_settings(ctx.guild.id, "notify", "options", "member_quits")}**'
        await hybrid_cmd_router(ctx, reply)
    elif setting == "notify-stream":
        SDI.toggle_settings(ctx.guild.id, "notify", "options", "stream_starts")
        reply = f'Теперь настройка {setting} переключена в положение **{SDI.get_settings(ctx.guild.id, "notify", "options", "stream_starts")}**'
        await hybrid_cmd_router(ctx, reply)
        pass
    else:
        await hybrid_cmd_router(ctx, "Такого параметра не существует")
    pass


@bot.hybrid_command(name=CommandsNames.BOTS_KICKED, description="Показать количество автоматически кикнутых ботов")
@commands.cooldown(1, 10, BucketType.user)
@discord.ext.commands.guild_only()
async def cmd_bots_kicked(ctx):
    reply = f'Всего ботов наказано: {SDI.get_stats(ctx.guild.id, 'autokick_count')}'
    await hybrid_cmd_router(ctx, reply)


@bot.hybrid_command(name=CommandsNames.STREAM, description="Управление оповещениями о стримах")
@discord.ext.commands.guild_only()
@discord.ext.commands.has_permissions(administrator=True)
async def cmd_manage_streams(ctx, command: typing.Literal["add", "remove", "channel", "list"], param: str):
    if command == "add":
        if param.find("youtube") < 0 and param.find("twitch") < 0:
            await hybrid_cmd_router(ctx, "Не указан URL канала")
            return
        reply = SDI.manage_list(ctx.guild.id, "add", param, "streams", "streaming_channels")
        await hybrid_cmd_router(ctx, reply)
    elif command == "remove":
        if param.find("youtube") < 0 and param.find("twitch") < 0:
            await hybrid_cmd_router(ctx, "Не указан URL канала")
            return
        reply = SDI.manage_list(ctx.guild.id, "remove", param, "streams", "streaming_channels")
        await hybrid_cmd_router(ctx, reply)
    elif command == "list":
        if param != "all":
            await hybrid_cmd_router(ctx, "Указан неверный параметр")
            return
        reply = SDI.get_stream_channels(ctx.guild.id)
        await hybrid_cmd_router(ctx, f'Список отслеживаемых каналов: \n{reply}')
    elif command == "channel":
        try:
            ch_id: int = int(param)
            SDI.set_settings(ctx.guild.id, ch_id, "streams", "options", "post_chid")
            reply = SDI.get_settings(ctx.guild.id, "streams", "options", "post_chid")
            await hybrid_cmd_router(ctx, f'Теперь сообщения от стримов будут публиковаться здесь: <#{reply}>')
        except Exception:
            await hybrid_cmd_router(ctx, "ID канала должен быть числом")


@bot.event
async def on_message(message):
    if message.author.bot: return
    prefix = SDI.get_settings(message.guild.id, "prefix")
    if message.content.startswith(f'{prefix}{CommandsNames.BOTS_KICKED}'): await cmd_bots_kicked(message)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        if ctx.command.name == 'bots-kicked':
            if str(error).find("in ") != -1:
                await ctx.send(f'`Вы слишком часто используете команду, попробуйте снова через '
                               f'{str(error)[str(error).find("in ") + 6:]}`')
            else:
                await ctx.send(f'`Вы слишком часто используете команду, попробуйте позже')
        else:
            await ctx.send('`Ошибка кулдауна`')


@bot.event
async def on_raw_reaction_add(reaction):  # должно работать даже на тех, что не в кэше
    if reaction.member.bot: return
    channel_id = bot.get_channel(reaction.channel_id)
    message_id = await channel_id.fetch_message(reaction.message_id)
    message_bdy = message_id.content
    time_string = f'{datetime.now().date().strftime("%d-%m-%Y")} - {datetime.now().time().strftime("%H:%M:%S")}'

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

    required_role_id: int = SDI.get_settings(reaction.guild_id, "autokick", "options", "required_role_id")
    trap_channels: list = SDI.get_settings(reaction.guild_id, "autokick", "trap_channels")

    for x in reaction.member.roles:

        found_trap = False
        # проверяем соответствие роли
        # если требуемая роль совпадает - продолжить, если не выставлена - тоже
        if x.id == required_role_id or required_role_id == 0:
            # проверяем все сообщения, на случай если на одном сообщении несколько ловушек
            for trap_setted_up in trap_channels:
                print(f'{trap_setted_up[1]} == {reaction.message_id}')
                # 0 - id канала
                # 1 - id сообщения
                # 2 - id эмодзи
                if int(trap_setted_up[1]) == reaction.message_id and int(trap_setted_up[2]) == reaction.emoji.id:

                    ch_id = SDI.get_settings(reaction.guild_id, "autokick", "options", "channel_to_farewell")
                    channel_abc_farewell = await bot.fetch_channel(int(ch_id))

                    guild_abc = await bot.fetch_guild(reaction.guild_id)
                    reason: str = SDI.get_settings(reaction.guild_id, "autokick", "options", "kick_ban_reason")
                    kicked_total = ServerDataInterface.get_stats(reaction.guild_id, "autokick_count")

                    if not CachedBans.in_list(reaction.member.id):  # проверяем есть ли ИД в списке класса-менеджера
                        CachedBans.add_to_list(reaction.member.id)  # добавляем если отсутствует

                    SDI.autokick_increase(reaction.guild_id)
                    if ch_id != 0:
                        await channel_abc_farewell.send(f'{CachedBans.get_formated_phrase(reaction.member.mention)}')
                        await hybrid_cmd_router(channel_abc_farewell, f'- подстрелено негодников: {kicked_total}')

                    try:
                        if SDI.get_settings(reaction.guild_id, "autokick", "options", "ban_instead") != "True":
                            await guild_abc.kick(reaction.member, reason=reason)
                        else:
                            await guild_abc.ban(reaction.member, reason=reason)
                    except Exception as e:
                        print(f'Ошибка воздействия на бот-аккаунт: {e}')

                    channel_abc_reacted = await bot.fetch_channel(reaction.channel_id)
                    message_abc = await channel_abc_reacted.fetch_message(reaction.message_id)
                    # удаляем поставленную реакцию
                    await message_abc.remove_reaction(reaction.emoji, reaction.member)

                    found_trap = True
                    break

        if found_trap:
            break
    print(f'\n')


@bot.event
async def on_member_remove(user_gone):
    # если в списке - убрать из списка и отменить дальнейшую процедуру
    # отмена нужна чтобы при повторном заходе выходе в пределах одной сессии бота он не помнил предыдущий случай
    print('Пользователь покинул сервер. Был ли обработан в другом событии: ')
    if CachedBans.in_list(user_gone.id):
        print(f'Список ID до: {CachedBans.userid_list}')
        CachedBans.remove_from_list(user_gone.id)
        print(f'Да, под ID {user_gone.id} его кикнул РИК-Бот. Теперь пользователь удалён из списка.')
        print(f'Список ID после: {CachedBans.userid_list}')
        return
    print('Нет, он вышел сам или был кикнут вручную.')

    if SDI.get_settings(user_gone.guild.id, "notify", "options", "member_quits") != "True":
        print('Сообщения о выходах отключены')
        return

    channel_id = SDI.get_settings(user_gone.guild.id, "autokick", "options", "channel_to_farewall")
    channel_abc = await bot.fetch_channel(channel_id)  # получение канала куда постить

    # отправка сообщения, делая запрос в класс, который в свою очередь запрашивает рандом из другой функции
    # и возвращает форматированный и готовый к отправке вариант
    await channel_abc.send(f'{CachedBans.get_formated_phrase(user_gone.mention)}')
    print('Done')


async def check_live_streams():
    for server_id in SDI.data:
        stream_settings = SDI.get_settings(server_id, "notify", "options", "stream_starts")
        # print(f'Для сервера {ServerID} настройка равна: {stream_settings}')
        if stream_settings == "True":
            url_list_of_channels = SDI.get_settings(server_id, "streams", "streaming_channels")
            if len(url_list_of_channels) > 0:
                # print(f'Список каналов на проверку для сервера {server_id}: {notify_stream_channels}')
                post_to_channel = SDI.get_settings(server_id, "streams", "options", "post_chid")
                await run_check_for_list(url_list_of_channels, post_to_channel)
            else:
                # print(f'Список каналов для проверки стримов на сервере {server_id} пуст, хотя функция проверки включена')
                pass


async def run_check_for_list(url_list_of_channels, post_to_channel, yt_type=None, twitch_type=None):
    for channel_url in url_list_of_channels:
        # print(f'Канал на проверку: {channel_url}')

        if "youtube" in channel_url:
            try:
                stream_url = channel_url + "/streams"  # overlay-style="LIVE"
                # print(f'Проверяю онлайн на канале: {stream_url}')
                response = requests.get(stream_url, headers=headers)
                soup = BeautifulSoup(response.content, 'html.parser')

                script_tag = soup.select_one('script:-soup-contains("ytInitialData")')
                script_content = script_tag.string
                json_start = script_content.find('{')
                json_end = script_content.rfind('}') + 1
                json_data = script_content[json_start:json_end]
                ytInitialData = json.loads(json_data)

                # with open("html_file.txt", 'w', encoding='utf-8') as file:
                #    file.write(json.dumps(ytInitialData, indent=4))

                # 0 - Главная
                # 1 - Видео
                # 2 - Shorts
                # 3 - Трансляции
                # 4 - Плейлисты
                basic_tag_path = (ytInitialData["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][3]["tabRenderer"]
                ["content"]["richGridRenderer"]["contents"][0]["richItemRenderer"]["content"]["videoRenderer"])
                current_stream_status = (basic_tag_path["thumbnailOverlays"][0]["thumbnailOverlayTimeStatusRenderer"]
                ["text"]["runs"][0]["text"])

                if len(str(current_stream_status)) >= 1:
                    if SDI.check_yt_cache(post_to_channel, basic_tag_path["videoId"]) != True:
                        print("Обнаружен активный стрим!")
                        stream_url = f'https://www.youtube.com/watch?v={basic_tag_path["videoId"]}'

                        # кэширование ютуб-канала, который уже получил оповещение о своём стриме
                        SDI.update_yt_cache(post_to_channel, basic_tag_path["videoId"])

                        # print(f'Полный путь до стрима: {stream_url}')
                        discord_channel = bot.get_channel(int(post_to_channel))
                        channel_name = ytInitialData["metadata"]["channelMetadataRenderer"]["title"]
                        stream_title = basic_tag_path["title"]["runs"][0]["text"]
                        thumbnail = basic_tag_path["thumbnail"]["thumbnails"][3]["url"]
                        thumbnail_url = thumbnail[0: thumbnail.find("?")]
                        avatar_url = (
                            ytInitialData["metadata"]["channelMetadataRenderer"]["avatar"]["thumbnails"][0]["url"])
                        # print(avatar_url)

                        embed = discord.Embed(
                            title=f"{channel_name} начинает трансляцию!",
                            description=f'**{stream_title}**',
                            url=stream_url,
                            color=Colour.from_rgb(*get_average_color(avatar_url))
                        )
                        embed.set_thumbnail(url=avatar_url)
                        embed.set_image(url=thumbnail_url)
                        embed.set_author(name=channel_name, icon_url=avatar_url)
                        embed.set_footer(text="Mister RIC approves!")
                        await discord_channel.send(embed=embed)
                    else:
                        print(f'Такой стрим {basic_tag_path["videoId"]} уже постили на канале: {post_to_channel}')

            except Exception as e:
                if 'runs' in str(e) or 'content' in str(e):
                    # если ошибка содержит не найденный аргумент - значит его нет, как и трансляции
                    # print(f'Нет активных трансляций')
                    pass
                else:
                    print(f'Ошибка при проверке канала: {e}')

        elif "twitch" in channel_url:
            user_login = channel_url[channel_url.rfind("/") + 1:]

            twitch = await Twitch('2fqly3pgkfd6jbd3cmxdybpyhvkekb', 'fm75x5f7i51jx0389ob1jlyoemjjzm')
            # 0 - логин \ юзернейм
            # 1 - заголовок стрима
            # 2 - название игры
            # 3 - ссылка на превью
            # 4 - ссылка на аватар
            stream_data = []
            async for x in twitch.get_streams(user_login=[user_login]):
                stream_data.append(x.user_name)
                stream_data.append(x.title)
                stream_data.append(x.game_name)
                stream_data.append(x.thumbnail_url.replace("{width}", "720").replace("{height}", "480"))
            async for x in twitch.get_users(logins=[user_login]):
                stream_data.append(x.profile_image_url)

            if len(stream_data) > 1:
                if SDI.check_yt_cache(post_to_channel, user_login) != True:
                    print("Обнаружен активный стрим!")
                    SDI.update_yt_cache(post_to_channel, user_login)
                    discord_channel = bot.get_channel(int(post_to_channel))

                    embed = discord.Embed(
                        title=f"{stream_data[0]} начинает трансляцию!",
                        description=f'**{stream_data[1]}**',
                        url=channel_url,
                        color=Colour.from_rgb(*get_average_color(stream_data[4]))
                    )
                    embed.set_thumbnail(url=stream_data[4])
                    embed.set_image(url=stream_data[3])
                    embed.set_author(name=stream_data[0], icon_url=stream_data[4])
                    embed.set_footer(text="Mister RIC approves!")
                    await discord_channel.send(embed=embed)
                else:
                    print(f'Такой стрим {stream_data[0]} уже постили на канале: {post_to_channel}')

        # print(f'Ожидаю тайм-аут: {int(config["global_stream_check_cd"])} с.')
        await asyncio.sleep(int(config["global_stream_check_cd"]))


if __name__ == '__main__':
    bot.run(DISCORD_TOKEN)
