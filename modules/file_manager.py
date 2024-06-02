import os
import shutil


class FileAction:
    def __init__(self, filename, openmethod, encoding=None):
        self.filename = filename
        self.openmethod = openmethod
        self.file_object = None
        self.encoding = 'utf-8'
        if not os.path.exists(filename) and os.path.isfile(filename):
            raise Exception("Файла не существует. Нужно сначала его создать!")

    def __enter__(self):
        self.file_object = open(self.filename, self.openmethod, encoding=self.encoding)
        return self.file_object

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file_object:
            self.file_object.close()


    @classmethod
    def server_files_check(cls, id_as_folder_name: int):

        from modules.load_config import config  # lazy

        template_dir = os.path.join(config["server_data_path"], config["templates_subpath"])
        server_dir = os.path.join(config["server_data_path"], str(id_as_folder_name))

        def copy_from_template(source, target):
            shutil.copytree(source, target)
            pass

        if os.path.isdir(server_dir):
            print("Папка гильдии уже существует.")
        else:
            try:
                copy_from_template(template_dir, server_dir)
            except Exception as e:
                print(f'Ошибка: {e}')
            finally:
                print("Процедура создания конфига из шаблона завершена.")

        for root, dirs, files in os.walk(template_dir):
            for file in files:
                file_path_on_templates = os.path.join(root, file)
                file_path_on_server = file_path_on_templates.replace(config["templates_subpath"],str(id_as_folder_name))
                if os.path.exists(file_path_on_server):
                    # print(f'{file} существует')
                    pass
                else:
                    print(f'файл {file} не найден, пересоздание...')
                    try:
                        shutil.copy2(file_path_on_templates, file_path_on_server)
                        print(f'Файл успешно пересоздан из шаблона')
                    except Exception as e:
                        print(f'Ошибка пересоздания файла / копирования шаблона: {e}')
                        try:
                            print(f'Попытка пересозания папки...')
                            folders_only = file_path_on_server[0 : file_path_on_server.find(file)]
                            os.makedirs(folders_only)
                            print(f'Папка успешно пересоздана. Пробуем пересоздать файл снова...')
                            shutil.copy2(file_path_on_templates, file_path_on_server)
                            print(f'Файл успешно пересоздан из шаблона')
                        except Exception as ex:
                            print(f'Ошибка в пересоздании папки: {ex}')
                    print("\n")
