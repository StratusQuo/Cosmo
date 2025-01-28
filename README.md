# 🪄 Cosmo - Web Form Autofiller

Cosmo is a CLI tool that makes filling out repetitive web forms a breeze. It takes data from Excel or CSV files and automatically populates web forms while giving you full control over the process.

## ✨ Features

- Smart Form Filling: Automatically fills web forms using data from Excel/CSV files
- Interactive Mode: Prompts you when there are mismatches between your data and existing form values
- Version Control: Built-in staging and versioning of your Excel/CSV files
- Backup & Restore: Create backups of form states and restore them when needed
- Diff Checking: Compare your Excel/CSV data against form values
- Change History: Track all modifications with detailed logs
- Aliases: Define shortcuts for frequently used paths and files

## Getting Started

### Prerequisites

- Python 3.7+
- Google Chrome
- Chrome Debugging enabled

### Installation

Clone the repository:

```
git clone https://github.com/StratusQuo/cosmo.git
cd cosmo
```

Install required packages:

```
pip install -r requirements.txt
```

Create the config directory:

```
mkdir -p ~/.config/cosmo
```

Copy the example config files:

```
cp data/config.toml ~/.config/cosmo/
cp data/aliases.config ~/.config/cosmo/
```

### Chrome Setup

Cosmo requires Chrome to be running in debug mode. Start Chrome with:

```
google-chrome --remote-debugging-port=9222
```

## 📖 Usage

### Basic Form Filling

First, stage your Excel file:

```
cosmo stage set -f path/to/your/data.xlsx
```

Next, fill the form:

```
cosmo fill
```

### Interactive Options

When Cosmo encounters mismatches between your data and existing form values, it provides several options:

`s` - Skip the field
`a` - Append new value to existing
`o` - Overwrite existing value

For any option, you can add `all` to apply the same action to all remaining fields (e.g., `o all` will overwrite all fields)

### Useful Commands

#### Verify form values against your Excel data

```
cosmo verify
```
#### See differences between form and Excel

```
cosmo diff
```

#### Create a backup of current form state

```
cosmo backup
```

#### View change history

```
cosmo history
```

#### Revert to a previous state

```
cosmo revert -f backup_file.xlsx
```

📁 ## Config Folder Structure
```
~/.config/cosmo/
├── config.toml         # Main configuration for the app
├── aliases.config      # Use this file to define path or file aliases
├── backups/            # Stores all backups of form state made with the "Backup" command
├── logs/               # Action logs
├── database/           # Change history -- can be queried with the "History" command.
└── staging/            # Staged Excel files
```

## 🙏 Acknowledgments

Built with the amazing Rich library for beautiful terminal output.
Uses Selenium for web automation.
