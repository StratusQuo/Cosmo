import shutil
import os
import datetime
import toml
from rich import print
from rich.console import Console

home_directory = os.path.expanduser("~")

CONFIG_PATH = os.path.join(home_directory, '.config', 'cosmo', 'config.toml')
VERSIONS_DIR = os.path.join(home_directory, '.config', 'cosmo', 'versions')
STAGING_PATH = os.path.join(home_directory, '.config', 'cosmo', 'staging')
BACKUP_DIR = os.path.join(home_directory, '.config', 'cosmo', 'backups')

class VersionControl:


    def __init__(self, filename=None):
        
        self.console = Console()

        # Ensure backup directory exists
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)
        
        if filename:
            self.filename = os.path.abspath(filename)  # Store the absolute path
        else:
            config = toml.load(CONFIG_PATH)
            self.filename = config.get('VCS', {}).get('staged_file', None)


    def stage(self):
        #check for staging dir, and if it's not there, make one
        staging_dir = os.path.join(home_directory, '.config', 'cosmo', 'staging')
        if not os.path.exists(staging_dir):
            os.makedirs(staging_dir)

        # Extract the original filename from the given path
        original_filename = os.path.basename(self.filename)
        
        # Construct the staging path using the original filename
        staging_file_path = os.path.join(home_directory, '.config', 'cosmo', 'staging', original_filename)
        
        # Copy the given Excel file to the staging area with its original filename
        shutil.copyfile(self.filename, staging_file_path)
        
        # Update config.toml
        config = toml.load(CONFIG_PATH)
        if 'VCS' not in config:
            config['VCS'] = {}
        config['VCS']['staged_file'] = staging_file_path
        with open(CONFIG_PATH, 'w') as config_file:
            toml.dump(config, config_file)
    
    def unstage(self):
        """Unstage the currently staged file."""
        # Remove the staged file if it exists
        staged_file = self.staged_file()
        if staged_file != "No file currently staged.":
            os.remove(staged_file)
            
            # Update config.toml
            config = toml.load(CONFIG_PATH)
            config['VCS']['staged_file'] = "none"
            with open(CONFIG_PATH, 'w') as config_file:
                toml.dump(config, config_file)
        else:
            print("No file currently staged.")

    def commit(self, commit_message):
        # Create a versioned filename
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        versioned_filename = f"{timestamp}_{commit_message}.xlsx"
        versioned_filepath = os.path.join(VERSIONS_DIR, versioned_filename)
        
        # Move staged file to versions directory
        shutil.move(STAGING_PATH, versioned_filepath)
        
        # Update config.toml
        config = toml.load(CONFIG_PATH)
        config['VCS']['current_version'] = versioned_filename
        config['VCS']['staged_file'] = "none"
        with open(CONFIG_PATH, 'w') as config_file:
            toml.dump(config, config_file)

    def rollback(self, version):
        versioned_filepath = os.path.join(VERSIONS_DIR, version)
        # Replace the current Excel file with the versioned file
        shutil.copyfile(versioned_filepath, STAGING_PATH)
        # Update config.toml
        config = toml.load(CONFIG_PATH)
        config['VCS']['current_version'] = version
        with open(CONFIG_PATH, 'w') as config_file:
            toml.dump(config, config_file)

    def backup(self, data):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        backup_path = os.path.join(BACKUP_DIR, f"backup_{timestamp}.xlsx")
        data.to_excel(backup_path, index=False)
        return backup_path


    def staged_file(self):
        config = toml.load(CONFIG_PATH)
        return config.get('VCS', {}).get('staged_file', "No file currently staged.")