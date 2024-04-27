import os


class FileAction:

    def __init__(self, filename, openmethod, content_to_save=None):
        if not os.path.exists(filename) and os.path.isfile(filename):
        # if not os.path.exists(os.path.dirname(filename)) and os.path.isfile(filename):
            raise Exception("File does not exist! Make one first!")
        # .file_object - даёт название тому, как мы будем обращаться
        self.file_object = open(filename, openmethod)
        if openmethod.find("r") >= 0 and content_to_save is not None:
            self.file_object.write(content_to_save)

    def __enter__(self):
        return self.file_object

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file_object.close()

    @classmethod
    def server_dir_check(cls, id_as_folder_name: int):
        # ленивая загрузка
        from modules.load_config import config
        if os.path.isdir(f'{config["server_data_path"]}/{str(id_as_folder_name)}'):
            print("Гильдия уже существует")
        else:
            os.mkdir(f'{config["server_data_path"]}/{str(id_as_folder_name)}')
            print("Папка гильдии создана")

    @classmethod
    def load_json(cls, file_path: str):
        pass
