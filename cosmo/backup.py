import toml
import pandas as pd
import datetime
import os

class BackupControl:

    def __init__(self, config_file_path='~/.config/cosmo/config.toml'):
        self.config_file_path = os.path.expanduser(config_file_path)
        self.load_config()

    def load_config(self):
        try:
            with open(self.config_file_path, 'r') as config_file:
                self.config = toml.load(config_file)
        except FileNotFoundError:
            raise Exception(f"Config file not found at {self.config_file_path}")

    @staticmethod
    def read_fields_from_excel(file_path) -> pd.DataFrame:
        df = pd.read_excel(file_path)
        return df.fillna("")

    def save_to_backup(self, df: pd.DataFrame, uuid: str) -> str:
        # Load the timestamp format from the [Backup] section of the config
        timestamp_format = self.config.get('Backup', {}).get('timestamp_format', "%Y%m%d_%H%M%S")
        backup_directory = os.path.expanduser(self.config.get('Backup', {}).get('backup_directory', '~/.config/cosmo/backups'))
        timestamp = datetime.datetime.now().strftime(timestamp_format)
        backup_filename = f"{backup_directory}/{uuid}_{timestamp}.xlsx"
        if not os.path.exists(backup_directory):
            os.makedirs(backup_directory)
        df.to_excel(backup_filename, index=False)
        return backup_filename

