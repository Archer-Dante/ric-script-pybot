import asyncio

import discord
from discord import app_commands, Colour
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
from modules.main_const_and_cls import FarewallManager  # импорт генератора сообщений
from modules.main_const_and_cls import CommandsNames  # импорт названия команд из констант внутри класса
from modules.tools import get_average_color  # получение усреднённого цвета RGB

import requests
from bs4 import BeautifulSoup
from collections import defaultdict

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
    def toggle_settings(cls, s_id, setting_name):
        print("Переключаю...")  # leave_notifications_enabled
        value = cls.data[str(s_id)]["settings"]
        print(f'Было: {value[setting_name]}, сервер {s_id}')
        if value[setting_name] == "True":
            value[setting_name] = "False"
        else:
            value[setting_name] = "True"
        print(f'Стало: {value[setting_name]}, сервер {s_id}')
        print(json.dumps(cls.data[str(s_id)]["settings"], indent=8))
        cls.save_cfgs(s_id)
        pass

    # возможно следует сделать из этого "def toggle_dict", т.к. одним автокиком не обойтись, а структура данных
    # может использоваться для разных опций
    # либо нужен полный обработчик, который будет определять, если ли в паре КЛЮЧ-ЗНАЧЕНИЕ что-то глубже и сложнее
    # чем просто значение, а именно: словарь, список или кортеж.
    # если ничего из этого нет - простая обработка, если есть - сложнее.
    @classmethod
    def autokick_toggle(cls, s_id):
        value = cls.data[str(s_id)]["settings"]["autokick"]
        print(f'Было: {value[0]}, сервер {s_id}')
        if int(value[0]) == 1:
            value[0] = "0"
        else:
            value[0] = "1"
        print(f'Было: {value[0]}, сервер {s_id}')
        cls.save_cfgs(s_id)
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

    @classmethod
    def get_total_yt_checks(cls):
        value = 0
        for server in cls.data:
            for link in cls.data[server]["settings"]["streams"]["streaming_channels"]:
                if "youtube" in link:
                    value = value + 1
        return int(value)

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
        print(cls.yt_cache)


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
                print(f'Уже кешировано: {x}')
                cached = True
        return cached


SDI = ServerDataInterface  # сокращённый вариант


async def hybrid_cmd_router(ctx_or_msg, reply):
    if type(ctx_or_msg) is discord.ext.commands.context.Context:
        await ctx_or_msg.send(reply)
    elif type(ctx_or_msg) is discord.message.Message:
        await ctx_or_msg.channel.send(reply)


# sys.exit()

# сообщение которое нужно заблочить
message_id_to_ban = 1072806217824600074
# канал где это сообщение для блока
channel_id_with_message = 925204884054229033
# какой смайл будет прокать работу кода
emoji_to_work_with = "<a:z_bye:1229599440352968725>"
emoji_to_work_with_id = 1229599440352968725
# кана куда писать прощальные сообщения
channel_id_to_farewall = 735409258904027166  # 735409258904027166 - тестовый # 790367801532612619 - используемый


@bot.event
async def on_ready():
    guild_count = 0

    for guild in bot.guilds:
        print(f"- {guild.id} (name: {guild.name})")
        guild_count = guild_count + 1
        FileAction.server_files_check(guild.id)
        ServerDataInterface(guild.id)

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
    #   try:
    #       commands_list = await bot.tree.sync()
    #       print(f'Синхронизировано команд: {len(commands_list)} - {commands_list}')
    #   except Exception as e:
    #       print(e)

    total_yt_checks_awaits = SDI.get_total_yt_checks()
    print(f'Всего каналов YT на обработке: {total_yt_checks_awaits}')

    while True:
        await check_live_streams()
        await asyncio.sleep(30 * total_yt_checks_awaits)  # по 30 сек на каждый канал до полного перезапуска


@bot.hybrid_command(name="daily", descripion="Получить ежедневный бонус")
async def cmd_daily(ctx):
    print("test")
    await ctx.send("Daily yet not implemented! Stay tuned!!")


# @bot.tree.command(name="www")
# async def test2(interaction: discord.Interaction):
#     # noinspection PyUnresolvedReferences
#     await interaction.response.send_message(f" 234 ")


@bot.hybrid_command(name=CommandsNames.TOGGLE,
                    description="Переключить настройку в указанное или противоположное значение")
@commands.cooldown(1, 4, BucketType.user)
@discord.ext.commands.guild_only()
@discord.ext.commands.has_permissions(administrator=True)
async def cmd_toggle_setting(ctx, setting):
    if setting == "leave_notifications_enabled":
        SDI.toggle_settings(ctx.guild.id, setting)

        after = f'Теперь настройка {setting} переключена в положение **{SDI.get_settings(ctx.guild.id, setting)}**'
        await hybrid_cmd_router(ctx, after)
        pass
    pass


@bot.hybrid_command(name=CommandsNames.BOTS_KICKED,
                    description="Показать количество автоматически кикнутых ботов")
@commands.cooldown(1, 10, BucketType.user)
@discord.ext.commands.guild_only()
async def cmd_bots_kicked(ctx):
    reply = f'`Всего ботов наказано: {ServerDataInterface.get_stats(ctx.guild.id, 'autokick_count')}`'
    await hybrid_cmd_router(ctx, reply)


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

    if SDI.get_settings(user_gone.guild.id, "leave_notifications_enabled") != "True":
        print('Сообщения о выходах отключены')
        return

    channel_obj_farewall = await bot.fetch_channel(channel_id_to_farewall)  # получение канала куда постить
    # отправка сообщения, делая запрос в класс, который в свою очередь запрашивает рандом из другой функции
    # и возвращает форматированный и готовый к отправке вариант
    await channel_obj_farewall.send(f'{FarewallManager.get_formated_phrase(user_gone.mention)}')
    print('Done')


@bot.hybrid_command(name=CommandsNames.CHECK_STREAM,
                    description="Проверить стримы на онлайн")
@commands.cooldown(1, 3, BucketType.user)
@discord.ext.commands.guild_only()
@discord.ext.commands.has_permissions(administrator=True)
async def cmd_toggle_setting(ctx):
    await check_live_streams()
    pass


async def check_live_streams():
    for server_id in SDI.data:
        stream_settings = SDI.get_settings(server_id, "notify", "options", "stream_starts")
        # print(f'Для сервера {ServerID} настройка равна: {stream_settings}')
        if stream_settings == "True":
            notify_stream_channels = SDI.get_settings(server_id, "streams", "streaming_channels")
            if len(notify_stream_channels) > 0:
                print(f'Список каналов на проверку для сервера {server_id}: {notify_stream_channels}')
                post_to_channel = SDI.get_settings(server_id, "streams", "options", "post_chid")
                await run_check_for_list(notify_stream_channels, post_to_channel)
            else:
                print(
                    f'Список каналов для проверки стримов на сервере {server_id} пуст, хотя функция проверки включена')


async def run_check_for_list(url_list_of_channels, post_to_channel, yt_type=None, twitch_type=None):
    for channel_url in url_list_of_channels:
        print(f'Строка из цикла на проверку: {channel_url}')
        if "youtube" not in channel_url: continue
        try:
            stream_url = channel_url + "/streams"  # overlay-style="LIVE"
            print(f'Проверяю канал: {stream_url}')
            response = requests.get(stream_url, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')

            script_tag = soup.select_one('script:-soup-contains("ytInitialData")')
            script_content = script_tag.string
            json_start = script_content.find('{')
            json_end = script_content.rfind('}') + 1
            json_data = script_content[json_start:json_end]
            ytInitialData = json.loads(json_data)

            with open("html_file.txt", 'w', encoding='utf-8') as file:
                file.write(json.dumps(ytInitialData, indent=4))

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
                if SDI.check_yt_cache(post_to_channel, basic_tag_path["videoId"]) == True:
                    print("Такое видео уже постили раньше на том же сервере")
                    return
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

        except Exception as e:
            if 'runs' in str(e):  # если ошибка содержит не найденный аргумент - значит его нет, как и трансляции
                print(f'На канале "{channel_url}" нет активных трансляций')
            else:
                print(f'Ошибка при проверке канала: {e}')
        print('Ожидаю тайм-аут.')
        await asyncio.sleep(30)


if __name__ == '__main__':
    bot.run(DISCORD_TOKEN)

# TODO
# изменить везде обработку "leave_notifications_enabled" на новую структуру данных
