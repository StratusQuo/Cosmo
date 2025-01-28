import typer
from typing import Optional
from .fill import CosmoFiller
from .verify import verify as run_verify
from .diff import display_differences as run_diff
from .version_control import VersionControl
from .backup import BackupControl
from .modules.aliases import AliasConfigParser
from rich import print
import os

app = typer.Typer(
    name="cosmo",
    help="Cosmo: Auto-filler for web forms using Excel or CSV data 🪄",
    add_completion=False,
    add_help_option=True
)

stage_app = typer.Typer(
     help="Stages an excel file for editing",
     invoke_without_command=True
     )

# ===================
#   Cosmo 'Fill'
# ===================

@app.command()
def fill(
    filename: str = typer.Option(None, "--file", "-f", help="Path to a Excel or CSV file with data."),
    cmd: Optional[str] = typer.Option(None, "--cmd", help="Command to run ('diff', 'overwrite', or default autofill)")
    ):
        """Fills the page using data from an .xlsx or .csv file"""
        if not filename:
            vc = VersionControl()
            filename = vc.filename
            if not filename:
                print("[red]No staged file found. Please stage a file using '[green]cosmo[/green] [blue]stage[/blue] [orange]-f[/orange] [yellow]<excel file>[/yellow]' or provide a file directly.[/red]")
                return

        cosmo = CosmoFiller()

        if cmd == "diff":
            cosmo.diff_fill(filename)

        elif cmd == "overwrite":
            cosmo.overwrite_fill(filename)

        else:
            cosmo.autofill(filename)

# ===================
#   Cosmo 'verify'
# ===================

@app.command()
def verify(filename: str = typer.Option(None, "--file", "-f", help="Path to the Excel file to Verify")):
    """Verify data on the webpage against the Excel or CSV file."""
    if filename is None:
        vc = VersionControl()
        filename = vc.staged_file()
        if filename == "No file currently staged.":
            typer.echo("[red]No staged file found. Please stage a file using 'cosmo stage -f <excel file>' or provide a file directly.[/red]")
            raise typer.Exit(code=1)
    run_verify(filename)

# ===================
#   Cosmo 'history'
# ===================

@app.command()
def history():
    """Shows a history of recent changes"""
    from .history import display_history
    display_history()


# ===================
#   Cosmo 'Revert'
# ===================


@app.command()
def revert(filename: str = typer.Option(..., "--file", "-f", help="Path to the file to revert to")
           ):
        """Reverts to a previous state"""
        cosmo = CosmoFiller()
        if cosmo.revert_file(filename):  # Assuming you have the revert function in fill.py
            print("Reverted to the previous state.")
        else:
            print("No backup found to revert to.")

# ===================
#   Cosmo 'Diff'
# ===================

@app.command()
def diff(filename: str = typer.Option(None, "--file", "-f", help="Path to an Excel or CSV to diff vs. the webpage")):
        """Shows a diff of the page vs. the Spreadsheet"""
        if filename is None:
            vc = VersionControl()
            filename = vc.staged_file()
            if filename == "No file currently staged.":
                typer.echo("[red]No staged file found. Please stage a file using 'cosmo stage -f <excel file>' or provide a file directly.[/red]")
                raise typer.Exit(code=1)
        run_diff(filename)

# ===================
#   Cosmo stage 'set'
# ===================

@stage_app.command(name="set")
def set_stage(
    folder_alias: str = typer.Argument(None, help="Folder alias (set in aliases.config) for staging"),
    file_alias: str = typer.Argument(None, help="File alias (set in aliases.config) for staging"),
    force: Optional[str] = typer.Option(None, "--file", "-f", help="Specify a file for staging")
):
    """Stages a Spreadsheet to use against the webpage"""
    
    if force:
        if os.path.exists(force):
            vc = VersionControl(force)
            vc.stage()
            typer.echo(f"File {force} has been staged.")
            return
        else:
            typer.echo(f"Error: File not found at {force}.")
            raise typer.Exit(code=1)
    
    if not folder_alias and not file_alias:
        typer.echo("Error: Please specify either folder_alias or file_alias.")
        raise typer.Exit(code=1)
    
    # Specify the actual config file path
    config_file_path = os.path.expanduser("~/.config/cosmo/aliases.config")

    alias_parser = AliasConfigParser(config_file_path)

    if folder_alias:
        folder_path = alias_parser.get_folder_path(folder_alias)
        folder_path = os.path.expanduser(folder_path)
        
        if not folder_path and not force:
            typer.echo("Error: Folder alias not found. Use --force to stage without specifying aliases.")
            raise typer.Exit(code=1)

        if not folder_path:
            typer.echo("Error: Folder alias not found.")
            raise typer.Exit(code=1)

        if file_alias:
            relative_file_path = alias_parser.get_file_path(folder_alias, file_alias)
            if not relative_file_path:
                typer.echo("Error: File alias not found. Use --force to stage without specifying aliases.")
                raise typer.Exit(code=1)

            absolute_file_path = os.path.join(folder_path, relative_file_path)
            if not os.path.exists(absolute_file_path):
                typer.echo(f"Error: File not found at {absolute_file_path}.")
                raise typer.Exit(code=1)

            vc = VersionControl(absolute_file_path)
            vc.stage()
            typer.echo(f"File {absolute_file_path} has been staged.")
        else:
            # If only a folder is specified without a specific file alias
            vc = VersionControl(folder_path)
            vc.stage()
            typer.echo(f"Folder {folder_path} has been staged.")





# ===================
#   Cosmo stage 'show'
# ===================

@stage_app.command(name="show")
def show_stage():
    """Show the currently staged file."""
    vc = VersionControl()
    staged_file = vc.staged_file()
    if staged_file:
        typer.echo(f"Staged file: {staged_file}")
    else:
        typer.echo("No file currently staged.")

# ===================
#   Cosmo stage 'unset'
# ===================
@stage_app.command(name="unset")
def unset_stage():
    """Unstage the currently staged file."""
    vc = VersionControl()
    vc.unstage()
    typer.echo("Staged file has been unstaged.")

app.add_typer(stage_app, name="stage")

# ==================
#   Cosmo Backup
# ==================

@app.command()
def backup():
    """Backs up the current state of the webpage to a uniquely named .xlsx file"""

    # Set Variables
    FIELDS_FILE_PATH = os.path.join(os.path.expanduser("~"), ".config", "cosmo", "data", "12m_Fields.xlsx")

    # Read predefined fields from the Excel file
    field_names = BackupControl.read_fields_from_excel(FIELDS_FILE_PATH)

    # Instantiate CosmoFiller and get modal title
    cosmo = CosmoFiller()
    title = cosmo.get_modal_title()  # Use the new method here

    uuid = title.split(' ')[2]  # Assuming format "Translations for UUID customerID"

    # Extract desired data from the webpage
    backup_df = cosmo.backup_data(field_names)

    # Create an instance of BackupControl and save the data to a backup file
    backup_controller = BackupControl()
    backup_filename = backup_controller.save_to_backup(backup_df, uuid)
    cosmo.console.print(f"[yellow]Backup saved to {backup_filename}![/yellow]")


if __name__ == "__main__":
    app()