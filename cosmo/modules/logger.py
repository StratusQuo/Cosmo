import os
import json
import toml
from datetime import datetime
from rich import print

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # Gets the directory of the current file.
CONFIG_PATH = os.path.expanduser("~/.config/cosmo/config.toml")

class CosmoLogger:

    def __init__(self):
        try:
            config = toml.load(CONFIG_PATH)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found at {CONFIG_PATH}. Please ensure it exists.")
        
        self.timestamp_format = config['Logger']['timestamp_format']
        self.log_directory = os.path.expanduser(config['Logger']['logs_directory'])

        if not os.path.exists(self.log_directory):
            os.makedirs(self.log_directory)
    
    def _get_current_timestamp(self):
        return datetime.now().strftime(self.timestamp_format)

    def format_log_entry_md(self, action, field_name, prev_value, new_value):
        timestamp = self._get_current_timestamp()
        return f"- **Timestamp**: {timestamp}\n  - **Field Name**: {field_name}\n  - **Action**: {action}\n  - **Previous Value**: {prev_value}\n  - **New Value**: {new_value}\n\n"

    def format_log_entry_txt(self, action, field_name, prev_value, new_value):
        timestamp = self._get_current_timestamp()
        return f"Timestamp: {timestamp}, Field Name: {field_name}, Action: {action}, Previous Value: {prev_value}, New Value: {new_value}\n"

    def write_log(self, log_entries):
        base_filename = f"log_{self._get_current_timestamp()}"
        
        # Markdown
        md_filepath = os.path.join(self.log_directory, base_filename + ".md")
        with open(md_filepath, 'w') as log_file:
            for entry in log_entries:
                if isinstance(entry, dict) and all(key in entry for key in ['action', 'field_name', 'prev_value', 'new_value']):
                    log_file.write(self.format_log_entry_md(**entry))
                else:
                    print(f"Skipped invalid log entry: {entry}")

        # JSON
        json_filepath = os.path.join(self.log_directory, base_filename + ".json")
        with open(json_filepath, 'w') as log_file:
            json.dump(log_entries, log_file, indent=4)

        # Plain Text
        txt_filepath = os.path.join(self.log_directory, base_filename + ".txt")
        with open(txt_filepath, 'w') as log_file:
            for entry in log_entries:
                log_file.write(self.format_log_entry_txt(**entry))
        
        print(f"Logs saved in Markdown, JSON, and TXT formats to {self.log_directory}")
