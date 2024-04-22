import random
# импорт своего класса по работе с файлами
from modules.file_manager import FileAction
from modules.load_config import config

phrases_list: list

phrase_path_build = config["localization_path"] + "kick_phrases/" + config["current_locale"] + ".txt"

with FileAction(phrase_path_build, "r") as current_file:
    phrases_list = current_file.read().splitlines(keepends=False)


def get_phrase(nickname) -> str:
    # print(Phrases_list[random.randint(0, len(Phrases_list) - 1)])
    final_phrase = "~ *" + phrases_list[random.randint(0, len(phrases_list) - 1)] + "*"
    # print(final_phrase)
    return final_phrase.replace("_", nickname)
