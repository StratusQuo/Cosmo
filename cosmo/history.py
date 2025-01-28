import datetime
import sqlite3
import os
from rich.console import Console
from rich.table import Table

# Find the user's home directory
HOME_DIR = os.path.expanduser("~")

# Construct the path for the database directory
DB_DIR = os.path.join(HOME_DIR, '.config', 'cosmo', 'database')

# Check if the directory exists, if not, create it
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

# Now, set the DATABASE variable to point to the correct path
DATABASE = os.path.join(DB_DIR, 'history.db')

class History:

    def __init__(self):
        self.entries = []
        self.conn = sqlite3.connect(DATABASE)
        self.cursor = self.conn.cursor()
        self.initialize_database()

    def initialize_database(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS history_entries (
                timestamp TEXT,
                field_name TEXT,
                action TEXT,
                old_value TEXT,
                new_value TEXT
            )
        ''')
        self.conn.commit()

    def add(self, field_name, action, old_value, new_value):
        timestamp = datetime.datetime.now().isoformat()
        entry = (timestamp, field_name, action, old_value, new_value)
        self.entries.append(entry)
        self.cursor.execute('''
            INSERT INTO history_entries (timestamp, field_name, action, old_value, new_value)
            VALUES (?, ?, ?, ?, ?)
        ''', entry)
        self.conn.commit()

    def get_all(self):
        self.cursor.execute('SELECT * FROM history_entries')
        return self.cursor.fetchall()


#def display_history():
#    for entry in history.get_all():
#        content = f"{entry[2]} '{entry[1]}' from '{entry[3]}' to '{entry[4]}' at {entry[0]}"
#        print(content)

def display_history():
    # Create a rich Console object
    console = Console()
    
    # Create a Table object
    table = Table(show_header=True, header_style="bold magenta")
    
    # Add headers to the table
    table.add_column("Timestamp", style="dim", width=25)
    table.add_column("Field Name", width=25)
    table.add_column("Action", style="bold", width=10)
    table.add_column("Old Value", width=30)
    table.add_column("New Value", width=30)
    
    # Populate the table with history data
    for entry in history.get_all():
        timestamp, field_name, action, old_value, new_value = entry
        if action == "append":
            action_style = "yellow"
        elif action == "overwrite":
            action_style = "green"
        elif action == "skip":
            action_style = "red"
        else:
            action_style = "white"
        
        table.add_row(timestamp, field_name, f"[{action_style}]{action}", old_value, new_value)
    
    # Display the table on the console
    console.print(table)

history = History()

def add_to_history(field_name, action, old_value, new_value):
    history.add(field_name, action, old_value, new_value)

if __name__ == '__main__':
    display_history()