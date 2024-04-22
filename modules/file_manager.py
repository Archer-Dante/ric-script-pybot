import os


class FileAction:

    def __init__(self, filename, openmethod):
        # .file_object - даёт название тому, как мы будем обращаться
        if not os.path.exists(filename) and os.path.isfile(filename):
            raise Exception("File does not exist! Make one first!")
        self.file_object = open(filename, openmethod)

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
