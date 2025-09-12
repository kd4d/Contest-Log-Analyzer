import os
from pathlib import Path

def create_desktop_files_safely(folder_name, file_name, file_content):
    """
    Safely creates a new folder and a file within it on the user's Desktop,
    handling standard and OneDrive-relocated Desktop paths.
    """
    try:
        # Step 1: Find the correct Desktop path
        home_dir = Path.home()
        onedrive_desktop = home_dir / 'OneDrive' / 'Desktop'
        if onedrive_desktop.exists():
            desktop_path = onedrive_desktop
        else:
            desktop_path = home_dir / 'Desktop'
        
        print(f"Using Desktop path: {desktop_path}")

        # Step 2: Define and create the new directory
        new_dir_path = desktop_path / folder_name
        new_dir_path.mkdir(parents=True, exist_ok=True)
        print(f"Directory created or already exists: {new_dir_path}")
        
        # Step 3: Define and create the new file
        file_path = new_dir_path / file_name
        with file_path.open(mode='w', encoding='utf-8') as f:
            f.write(file_content)
        print(f"File created successfully: {file_path}")

    except OSError as e:
        print(f"An OS error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Example usage
create_desktop_files_safely(
    folder_name="My_Python_Output",
    file_name="report.txt",
    file_content="This report was generated automatically by a Python script."
)