import os
import random

# from main import current_locale


class File:

    def __init__(self, filename, openmethod):
        # .file_object - даёт название тому, как мы будем обращаться
        if not os.path.exists(filename) and os.path.isfile(filename):
            raise Exception("File does not exist! Make one first!")
        self.file_object = open(filename, openmethod)

    def __enter__(self):
        return self.file_object

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file_object.close()


phrases_list: list
# отключено во избежание циркулярной ошибки импорта
# phrases_filepath: str = "kick_phrases/" + current_locale

with File("kick_phrases/ru.txt", "r") as current_file:
    # print(current_file.read())
    phrases_list = current_file.read().splitlines(keepends=False)


def get_phrase(nickname) -> str:
    # print(Phrases_list[random.randint(0, len(Phrases_list) - 1)])
    final_phrase = "~ *" + phrases_list[random.randint(0, len(phrases_list) - 1)] + "*"
    # print(final_phrase)
    return final_phrase.replace("_", nickname)


if __name__ == '__main__':
    print("done hiding!")

