import discord
from discord import app_commands
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
    def get_settings(cls, s_id, search_for_key):
        cfg_branch = cls.data[str(s_id)]["settings"]
        # print(cfg_branch)
        value = cfg_branch.get(search_for_key, None)
        if value is None:
            return f'<Ошибка: значение не найдено>'
        else:
            return value

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
        print("Переключаю...") # leave_notifications_enabled
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
channel_id_to_farewall = 735409258904027166 # 735409258904027166 - тестовый # 790367801532612619 - используемый


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
    try:
        commands_list = await bot.tree.sync()
        print(f'Синхронизировано команд: {len(commands_list)} - {commands_list}')
    except Exception as e:
        print(e)


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


if __name__ == '__main__':
    bot.run(DISCORD_TOKEN)
