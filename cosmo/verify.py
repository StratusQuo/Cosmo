import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from rich import console
from rich.table import Table
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.box import HEAVY_EDGE, SIMPLE_HEAD

# Set up console messages from the Rich library
console = Console()

# ==============================
#  Verification Function
# ==============================
def verify(filename: str = None):
    if not filename:
        vc = VersionControl()
        filename = vc.filename
        if not filename:
            self.console.print("[red]No staged file found. Please stage a file using 'cosmo stage -f <excel file>' or provide a file directly.[/red]")
            return
    # Read data from an Excel file using pandas
    file_ext = filename.split('.')[-1]
    if file_ext == 'xlsx':
        dataFrame = pd.read_excel(filename)
    elif file_ext == 'csv':
        dataFrame = pd.read_csv(filename)
    else:
        console.print("[red]Unsupported file format. Please provide an Excel or CSV file.[/red]")
        return

    # Connect to existing Chrome session
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    browser = webdriver.Chrome(options=chrome_options)

    matches = 0
    mismatches = []
    missing_fields = []

    for index, row in dataFrame.iterrows():
        field_name = row.iloc[0]
        value = row.iloc[1]

        try:
            input_element = browser.find_element(By.XPATH, f"//*[@name='{field_name}']")
            current_value = input_element.get_attribute('value')

            if current_value == value:
                console.print(f"[green]Match for field {field_name}.")
                matches += 1
            else:
                mismatches.append({
                    "field_name": field_name,
                    "excel_value": value,
                    "web_value": current_value
                })

        except NoSuchElementException:
            missing_fields.append(field_name)
            console.print(f"[red]Field with name {field_name} not found on the page![/red]")

    # Summary
    
    console.print(Markdown(f"# Summary"))
    console.print(f"[yellow] • [/yellow][italic green]Matching Lines:[/italic green] {matches}")
    console.print(f"[yellow] • [/yellow][italic yellow]Missing Fields:[/italic yellow] {len(missing_fields)}")
    console.print(f"[yellow] • [/yellow][italic red][blink]Mismatched Lines:[/blink][/italic red] {len(mismatches)}")
    console.print("\n")

    # Mismatched Lines
    if mismatches:
        
        table = Table(show_header=True, box=SIMPLE_HEAD)
        #table.add_column("Field")
        #table.add_column("Spreadsheet Value")
        #table.add_column("Dashboard Value")

        column_widths = [80, 40, 60]
    
        table.add_column("Field", width=column_widths[0], justify="left")
        table.add_column("Spreadsheet Value", width=column_widths[1], justify="left")
        table.add_column("Dashboard Value", width=column_widths[2], justify="left")

        for mismatch in mismatches:
            table.add_row(mismatch['field_name'], f"{mismatch['excel_value']}", f"{mismatch['web_value']}")

        console.print(Panel(f"Mismatched Lines", box=HEAVY_EDGE))
        console.print(table)

    # Missing Fields
    if missing_fields:
        missing_md = Markdown("\n".join(f"- {field}" for field in missing_fields))
        console.print(Panel(f"Missing Fields", box=HEAVY_EDGE))
        console.print(missing_md)

# ====================================
#          __main__ block
# ====================================

#if __name__ == "__main__":
#    import argparse
#    parser = argparse.ArgumentParser(description='Verify data on the webpage against the Excel or CSV file.')
#    parser.add_argument('-f', '--file', required=True, help='Path to the Excel or CSV file with data.')
#    args = parser.parse_args()
#    verify(args)
