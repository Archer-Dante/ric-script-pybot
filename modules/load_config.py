import json
from modules.file_manager import FileAction

config_file_path: str = "config.json"

with FileAction(config_file_path, "r") as file:
    config = json.loads(file.read())

# current_locale = config["current_locale"]
# server_data_path = config["server_data_path"]
# localization_path = config["localization_path"]

if __name__ == '__main__':
    print(config["current_locale"])