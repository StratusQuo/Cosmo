import os

class AliasConfigParser:
    def __init__(self, config_file_path):
        self.config = self._load_config(config_file_path)

    def _load_config(self, config_file_path):
        with open(config_file_path, 'r') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]  # Strip whitespace and filter out empty lines

        parsed = {}
        current_folder = None
        for line in lines:
            if line.startswith("PathAlias"):
                current_folder = line.split()[1].strip()
                parsed[current_folder] = {"path": None, "files": {}}
            elif line.startswith("Path"):
                if current_folder is None:
                    raise ValueError("Path defined before PathAlias")
                parsed[current_folder]['path'] = line.split(maxsplit=1)[1].strip()
            elif line.startswith("FileAlias"):
                if current_folder is None:
                    raise ValueError("FileAlias defined before PathAlias")
                current_file = line.split()[1].strip()
                if "files" not in parsed[current_folder]:
                    parsed[current_folder]['files'] = {}
                parsed[current_folder]['files'][current_file] = None
            elif line.startswith("FilePath"):
                if current_folder is None or current_file is None:
                    raise ValueError("FilePath defined before FileAlias or PathAlias")
                parsed[current_folder]['files'][current_file] = line.split(maxsplit=1)[1].strip()

        return parsed


    def get_folder_path(self, folder_alias):
        return self.config.get(folder_alias, {}).get('path')

    def get_file_path(self, folder_alias, file_alias):
        folder = self.config.get(folder_alias, {})
        absolute_file_path = folder.get("files", {}).get(file_alias)

        # Return just the file's name (relative path)
        if absolute_file_path:
            return os.path.basename(absolute_file_path)

