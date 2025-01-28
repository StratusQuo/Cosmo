# ==================================
#          Cosmo v0.13 
#  Created By: Christopher Chappell      
# =================================

import os
import datetime
import argparse
import pandas as pd

from   selenium import webdriver
from   selenium.webdriver.common.by   import By
from   selenium.common.exceptions     import NoSuchElementException
from   selenium.webdriver.common.keys import Keys

from   rich             import print
from   rich.panel       import Panel
from   rich.console     import Console
from   rich.progress    import Progress
from   .history         import History
from   .modules.logger  import CosmoLogger
from   .version_control import VersionControl


# =======================
#       Fill Class
# =======================
class CosmoFiller:

    def __init__(self):
        self.console = Console()
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        self.browser = webdriver.Chrome(options=self.chrome_options)
        self.change_logger = History() # Change database for History operations
        self.logger = CosmoLogger() # Fill Logs

    def get_modal_title(self):
        try:
            modal_title_element = self.browser.find_element(By.CSS_SELECTOR, ".MuiTypography-h6")
            return modal_title_element.text
        except NoSuchElementException:
            return ""
    
    def backup_data(self, field_names: pd.DataFrame) -> pd.DataFrame:
        field_data = []
        for _, row in field_names.iterrows():
            field_name = row.iloc[0]  # Grab field name from the *first* column 
            try:
                input_element = self.browser.find_element(By.NAME, field_name)
                current_value = input_element.get_attribute('value')
                field_data.append([field_name, current_value])
            except NoSuchElementException:
                field_data.append([field_name, None])

        return pd.DataFrame(field_data, columns=["field_name", "value"])


    def autofill(self, filename: str = None, backup: bool = False):

        log_entries = []

        if not filename:
            vc = VersionControl()
            filename = vc.filename
            if not filename:
                self.console.print("[red]No staged file found. Please stage a file using 'cosmo stage -f <excel file>' or provide a file directly.[/red]")
                return
        
        file_ext = filename.split('.')[-1]
        if file_ext == 'xlsx':
            dataFrame = pd.read_excel(filename)
        elif file_ext == 'csv':
            dataFrame = pd.read_csv(filename)
        else:
            self.console.print("[red]Unsupported file format. Please provide an Excel or CSV file.[/red]")
            return

        # Connect to Chrome debugging session
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        browser = webdriver.Chrome(options=chrome_options)

        # ====================================================
        # Backup files (if a backup is specified in the CLI)
        # ====================================================
        if backup:
            self.backup_data(dataFrame)


        # Logging setup
        log_entry = [
            {
                "action": "Modified",
                "field_name": "Field1",
                "prev_value": "old_value",
                "new_value": "new_value"
            }
        ]

        apply_to_all_choice = None  # Store the 'apply to all' choice in a variable


        # ==================================
        #   Main data processing block
        # ==================================
        with Progress(console=self.console, auto_refresh=False) as progress:
            task = progress.add_task("[cyan]Filling form...[/cyan]", total=dataFrame.shape[0])

            for index, row in dataFrame.iterrows():
                choice = ""
                field_name = row.iloc[0]
                value = row.iloc[1]
                #timestamp = datetime.datetime.now().isoformat() # TODO: Remove

                # Initialize log_entry with default values
                log_entry = {
                    "action": "Unknown",
                    "field_name": field_name,
                    "prev_value": None,
                    "new_value": None
                }

                try:
                    input_element = browser.find_element(By.XPATH, f"//*[@name='{field_name}']")
                    current_value = input_element.get_attribute('value')
                    log_entry["prev_value"] = current_value  # Update the previous value


                    if current_value == value:
                        self.console.print(f"Field [yellow]{field_name}[/yellow] already has the same value. Skipping...")
                    
                    # ==================================================
                    #     Handling options for data that doesn't 
                    #              match our excel sheet.
                    # =================================================

                    elif current_value is not None and current_value.strip() != "":

                        if not apply_to_all_choice: # or apply_to_all_choice == "o":
                            progress.stop()
                            self.console.print("\n")
                            self.console.print(Panel(f"""[reverse red] WARNING: Mismatch in field {field_name} [/reverse red]\n\n[red]Webpage value: {current_value}[/red]\n[yellow]Spreadsheet value: {value}[/yellow]\n\nChoose an action:\n - [blue]s[/blue] = skip\n - [yellow]a[/yellow] = append\n - [magenta]o[/magenta] = overwrite\n - Add [light_slate_blue]all[/light_slate_blue] to any option to apply to all (ex: "[magenta]o[/magenta] [light_slate_blue]all[/light_slate_blue]" to overwrite all.)                                            
                                        """, expand=True))
                            choice = input()
                            choice = choice.strip().lower()

                            if choice.endswith(" all"):
                                apply_to_all_choice = choice[0]
                            else:
                                apply_to_all_choice = None
                        
                        choice = apply_to_all_choice if apply_to_all_choice else choice

                        
                        # ================================
                        # Handle each option at the prompt
                        # ================================
                        if choice == "s":
                            log_entry["action"] = "Skipped"
                            self.console.print(f"[green]Skipped {field_name}.[/green]")
                            self.change_logger.add(field_name, "skip", current_value, value) # Database Entry



                        elif choice == "a":
                            self.console.print(f"[gold1]Appending [magenta]{value}[/magenta] to [navajo_white1]'{current_value}'[/navajo_white1]...[/gold1]")
                            newValue = current_value + value
                            input_element.send_keys(value)  # Directly append the value without clearing the field.
                            self.console.print(f"[gold1]Appended [magenta]{value}[/magenta] to the [navajo_white1]'{field_name}'[/navajo_white1] field.[/gold1] -- new value is {newValue}")
                            log_entry["action"] = "Appended"
                            log_entry["new_value"] = newValue 
                            self.change_logger.add(field_name, "append", current_value, newValue) # Database Entry


                        elif choice == "o":
                            input_element.send_keys(Keys.COMMAND, 'a')
                            input_element.send_keys(value)
                            self.console.print(f"[green]Successfully overwrote the [yellow]'{field_name}'[/yellow] field.[/green]")                            
                            log_entry["action"] = "Overwrote"
                            log_entry["new_value"] = value
                            self.change_logger.add(field_name, "overwrite", current_value, value)

                    
                    # =============================================
                    # Populate field if no mismatches are detected.
                    # =============================================

                    else:
                        input_element.send_keys(value)
                        log_entry["action"] = "Filled"
                        log_entry["new_value"] = value
                        self.console.print(f"[green]Filled the [yellow]'{field_name}'[/yellow] field with value [cyan]{value}[/cyan].[/green]")

                    # ===========================================
                    # Start Progress after Handling Current Field
                    # ===========================================
                    
                    progress.start()

                except NoSuchElementException:
                    log_entry["action"] = "Field Not Found"
                    log_entry["new_value"] = value
                    self.console.print(f"[red]Field with name [/red][yellow]{field_name}[/yellow] [red]not found on the page![/red]")
                
                # Append to logs at the end of each iteration:
                log_entries.append(log_entry)

                # Update the progress bar at the end of each iteration
                progress.update(task, advance=1)
                progress.refresh()

        # ==================================
        #       Write output to logs
        # ==================================

        self.logger.write_log(log_entries)

        # ==============================================================
        # Print the below message when the form is finished completing.
        # ==============================================================
        
        self.console.print("Form filling completed!")


    # ===============
    #     Revert
    # ===============



    def revert_file(self, file_name: str) -> bool:
        
        console = Console()        
        with console.status("[bold blue]Reverting, please wait...", spinner="dots2"):
            # Revert logic

            if not file_name:
                print("Error: File name not provided.")
                return False

            # Check if the backup file exists
            if not os.path.exists(file_name):
                return False

            # Load the backup data
            backup_df = pd.read_excel(file_name).fillna("")  # Replace NaN with blank strings

            # Connect to the web browser session
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
            browser = webdriver.Chrome(options=chrome_options)

            # Revert fields based on backup data
            for index, row in backup_df.iterrows():
                field_name = row["field_name"]
                previous_value = row["value"]

                try:
                    input_element = browser.find_element(By.XPATH, f"//*[@name='{field_name}']")
                    input_element.send_keys(Keys.COMMAND, 'a')  # Clear the current value
                    input_element.send_keys(previous_value)  # Populate with backup value
                except NoSuchElementException:
                    # Handle the situation when the field is not found. This could be a print or log statement.
                    pass

            # Close the browser session or keep it open based on your requirement
            # browser.quit()

        return True
    
    # ==============================
    #   Fill page based on a diff
    # ==============================

    def diff_fill(self, filename: str):
        from .diff import display_differences
        # Fetching the mismatches using display_differences
        mismatches = display_differences(filename)
        
        # Loop through the mismatches
        for field_name, values in mismatches.items():
            excel_value = values["excel_value"]
            
            try:
                # Find the input element
                input_element = self.browser.find_element(By.XPATH, f"//*[@name='{field_name}']")
                
                # Clear the current value and populate with the excel_value
                input_element.send_keys(Keys.COMMAND, 'a')
                input_element.send_keys(excel_value)
                
            except NoSuchElementException:
                # Handle the situation when the field is not found.
                pass


    # =======================================
    # Logic for cosmo fill 'overwrite' option
    # =======================================

    def overwrite_fill(self, filename: str):
        file_ext = filename.split('.')[-1]
        if file_ext == 'xlsx':
            dataFrame = pd.read_excel(filename)
        elif file_ext == 'csv':
            dataFrame = pd.read_csv(filename)
        else:
            self.console.print("[red]Unsupported file format. Please provide an Excel or CSV file.[/red]")
            return

        with Progress(console=self.console, auto_refresh=False) as progress:
            task = progress.add_task("[cyan]Overwriting form...", total=dataFrame.shape[0])

            for index, row in dataFrame.iterrows():
                field_name = row.iloc[0]
                value = row.iloc[1]
                timestamp = datetime.datetime.now().isoformat()

                try:
                    input_element = self.browser.find_element(By.XPATH, f"//*[@name='{field_name}']")
                    input_element.send_keys(Keys.COMMAND, 'a')  # Clear the current value
                    input_element.send_keys(value)  # Populate with the value from the file

                    self.console.print(f"[green]Overwrote the [yellow]'{field_name}'[/yellow] field with value [cyan]{value}[/cyan].[/green]")
                except NoSuchElementException:
                    self.console.print(f"[red]Field with name [/red][yellow]{field_name}[/yellow] [red]not found on the page![/red]")

                # Update the progress bar at the end of each iteration
                progress.update(task, advance=1)
                progress.refresh()

        self.console.print("Form overwriting completed!")
    
    def backup_browser_data(self): 
        # TODO: Remove
        # Get the data from the browser
        data_frame = self.fetch_data_from_browser()
        
        # Call backup_data with the DataFrame
        self.backup_data(data_frame)



# ===========================================
#            The __main__ block.
#   Note: This will be removed in the future
#    Currently this is mostly for Debugging 
# ===========================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Autofill forms using Excel data.')
    parser.add_argument('-f', '--file', required=True, help='Path to the Excel file with data.')
    parser.add_argument('--backup', action='store_true', help='Backup existing values to backup.xlsx')
    args = parser.parse_args()
    cosmo = CosmoFiller()

    if args.mode == "diff":
        cosmo.diff_fill(args.file)
    elif args.mode == "overwrite":
        cosmo.overwrite_fill(args.file)
    if args.revert:
        revert_file(args.file)  # Make sure revert_file is designed to take in necessary arguments
    else:
        autofill(args.file, args.backup)