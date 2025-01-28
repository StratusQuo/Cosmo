import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from rich.console import Console
from rich.text import Text

# Set up console messages from the Rich library
console = Console()

def generate_diff(original: str, modified: str) -> Text:
    diff_text = Text()
    
    for o, m in zip(original, modified):
        if o == m:
            diff_text.append(o)
        else:
            diff_text.append(o, "red")
            diff_text.append(m, "green")

    # Append any remaining characters
    if len(original) < len(modified):
        diff_text.append(modified[len(original):], "green")
    elif len(original) > len(modified):
        diff_text.append(original[len(modified):], "red")
    
    return diff_text

def display_differences(filename: str) -> dict:
    # Read data from an Excel or CSV file
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

    mismatches = {}

    for index, row in dataFrame.iterrows():
        field_name = row.iloc[0]
        value = row.iloc[1]

        try:
            input_element = browser.find_element(By.XPATH, f"//*[@name='{field_name}']")
            current_value = input_element.get_attribute('value')

            if current_value != value:
                mismatches[field_name] = {
                    "excel_value": value,
                    "web_value": current_value
                }
                diff_content = generate_diff(value, current_value)
                console.print(f"[yellow]Diff for field {field_name}:[/yellow]")
                console.print(diff_content)

        except NoSuchElementException:
            console.print(f"[red]Field with name {field_name} not found on the page![/red]")

    return mismatches

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Display differences between data on the webpage and the Excel or CSV file.')
    parser.add_argument('-f', '--file', required=True, help='Path to the Excel or CSV file with data.')
    args = parser.parse_args()
    display_differences(args.file)