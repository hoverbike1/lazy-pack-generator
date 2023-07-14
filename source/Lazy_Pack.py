import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
import sys

def get_yuzu_folder_from_appdata():
    yuzu_folder_path = Path(os.getenv('APPDATA'))
    if yuzu_folder_path.exists():
        return str(yuzu_folder_path)
    return None

def open_folder_dialog():
    folder_path = filedialog.askdirectory(title="Select Yuzu Roaming/User Folder (Typically C:/Users/<Your Username>/AppData/Roaming/yuzu/) unless you use portable yuzu")
    if folder_path:
        yuzu_folder_path.set(folder_path)
        yuzu_folder_label.config(fg="green")
        yuzu_folder_entry.delete(0, tk.END)
        yuzu_folder_entry.insert(0, folder_path)  # Insert the path in the entry widget
        yuzu_folder_button.config(fg="green")
    else:
        yuzu_folder_path.set("")
        yuzu_folder_label.config(fg="red")
        yuzu_folder_entry.delete(0, tk.END)
        yuzu_folder_button.config(fg="red")

def copy_blackscreen_fix(romfs_folder):
    blackscreen_fix_option = blackscreen_var.get()

    if blackscreen_fix_option == 'Add Black-screen fix (Nintendo UI)':
        blackscreen_fix_folder = os.path.join(script_directory, 'data', 'blackscreenfix', 'UI')
        shutil.copytree(blackscreen_fix_folder, os.path.join(romfs_folder, 'UI'))
    elif blackscreen_fix_option == 'Add Black-screen fix (Playstation UI)':
        playstation_fix_folder = os.path.join(script_directory, 'data', 'Playstation UI Mod v12.2 - Normal - White', 'romfs', 'UI')
        shutil.copytree(playstation_fix_folder, os.path.join(romfs_folder, 'UI'))
        playstation_font_folder = os.path.join(script_directory, 'data', 'Playstation UI Mod v12.2 - Normal - White', 'romfs', 'Font')
        shutil.copytree(playstation_font_folder, os.path.join(romfs_folder, 'Font'))
    elif blackscreen_fix_option == 'Add Black-screen fix (Xbox UI)':
        xbox_fix_folder = os.path.join(script_directory, 'data', 'Xbox UI Mod v9 - Normal - White', 'romfs', 'UI')
        shutil.copytree(xbox_fix_folder, os.path.join(romfs_folder, 'UI'))
        xbox_font_folder = os.path.join(script_directory, 'data', 'Xbox UI Mod v9 - Normal - White', 'romfs', 'Font')
        shutil.copytree(xbox_font_folder, os.path.join(romfs_folder, 'Font'))
    elif blackscreen_fix_option == 'Remove Black-screen fix (UI Compatible)':
        romfs_ui_folder = os.path.join(romfs_folder, 'UI')
        shutil.rmtree(romfs_ui_folder, ignore_errors=True)
        romfs_font_folder = os.path.join(romfs_folder, 'Font')
        shutil.rmtree(romfs_font_folder, ignore_errors=True)

def generate_config():
    resolution = resolution_var.get().split(' (')[0]
    framerate = framerate_var.get().split(' ')[0]
    blackscreen_fix = blackscreen_var.get()

    yuzu_folder_path_value = yuzu_folder_path.get()

    if not yuzu_folder_path_value:
        appdata_path = get_yuzu_folder_from_appdata()
        if appdata_path:
            yuzu_folder_path.set(appdata_path)
            yuzu_folder_label.config(fg="green")
            yuzu_folder_entry.delete(0, tk.END)
            yuzu_folder_entry.insert(0, appdata_path)
            yuzu_folder_button.config(fg="green")
            yuzu_folder_path_value = appdata_path
        else:
            messagebox.showinfo("Yuzu Folder", "Yuzu folder not selected. Please select it manually.")
            yuzu_folder_label.config(fg="red")
            return

    script_directory = Path(__file__).resolve().parent

    source_folder = os.path.join(script_directory, 'data', 'source')
    result_folder = os.path.join(os.getcwd(), 'result')

    if os.path.exists(result_folder):
        confirm = messagebox.askyesno("Confirmation", "The 'result' folder already exists. Do you want to delete it and continue?")
        if confirm:
            shutil.rmtree(result_folder)
        else:
            return

    shutil.copytree(source_folder, result_folder)

    romfs_folder = os.path.join(result_folder, 'romfs')
    dfps_folder = os.path.join(romfs_folder, 'dfps')
    os.makedirs(dfps_folder, exist_ok=True)

    resolution_ini_path = os.path.join(dfps_folder, 'resolution.ini')
    with open(resolution_ini_path, 'w') as f:
        f.write('[Graphics]\n')
        f.write('ResolutionWidth = {}\n'.format(resolution.split('x')[0]))
        f.write('ResolutionHeight = {}\n'.format(resolution.split('x')[1]))

    framerate_ini_path = os.path.join(dfps_folder, 'framerate.ini')
    with open(framerate_ini_path, 'w') as f:
        f.write('[dFPS]\n')
        f.write('MaxFramerate = {}\n'.format(framerate))
        f.write('EnableCameraQualityImprovement = false\n')

    copy_blackscreen_fix(romfs_folder)

    config_folder_paths = [
        os.path.join(yuzu_folder_path_value, 'config', 'custom'),
        os.path.join(yuzu_folder_path_value, 'user', 'config', 'custom')
    ]

    for config_folder_path in config_folder_paths:
        ini_file_path = os.path.join(config_folder_path, '0100F2C0115B6000.ini')

        if os.path.exists(ini_file_path):
            with open(ini_file_path, 'r') as f:
                lines = f.readlines()

            with open(ini_file_path, 'w') as f:
                for line in lines:
                    if line.startswith('use_unsafe_extended_memory_layout'):
                        if resolution in ['960x540', '1280x720', '1366x768', '1600x900', '1920x1080']:
                            f.write('use_unsafe_extended_memory_layout\\use_global=true\n')
                        else:
                            f.write('use_unsafe_extended_memory_layout\\use_global=false\n')
                            f.write('use_unsafe_extended_memory_layout\\default=false\n')
                            f.write('use_unsafe_extended_memory_layout=true\n')
                    elif line.startswith('resolution_setup'):
                        f.write('resolution_setup\\use_global=false\n')
                        f.write('resolution_setup\\default=true\n')
                        f.write('resolution_setup=2\n')
                    else:
                        f.write(line)

    folder_name = f"Custom Lazy Pack - {resolution} - {framerate} FPS - {blackscreen_fix}"
    lazy_pack_folder = os.path.join(yuzu_folder_path_value, 'load', '0100F2C0115B6000', folder_name)
    shutil.rmtree(lazy_pack_folder, ignore_errors=True)
    shutil.copytree(result_folder, lazy_pack_folder)

    # Clean up the result folder
    shutil.rmtree(result_folder)

    messagebox.showinfo("Success", "Lazy Pack generated successfully.")
    yuzu_folder_label.config(fg="green")

# Create the main window
window = tk.Tk()
window.title("Lazy Pack Generator")
window.geometry("480x480")
window.resizable(False, False)

# Add padding to the top and left side
window['padx'] = 10
window['pady'] = 10

# Determine the script directory
script_directory = Path(__file__).resolve().parent

# Set the background image path
background_image_path = script_directory / 'data' / 'background' / 'background.png'

# Create the background label
background_image = tk.PhotoImage(file=background_image_path)
background_label = tk.Label(window, image=background_image)
background_label.place(relwidth=1, relheight=1)

# Create the dropdown menus
resolutions = ['960x540 (qHD)', '1280x720 (HD)', '1366x768 (HD)', '1600x900 (HD+)', '1920x1080 (FHD)', '2560x1440 (QHD)', '3840x2160 (4K)', '5120x2880 (QQHD)', '5760x3240(3xFHD)', '7680x4320 (8K)']
framerates = ['20 FPS', '30 FPS', '35 FPS', '36 FPS', '40 FPS', '45 FPS', '60 FPS', '72 FPS', '75 FPS', '80 FPS', '90 FPS', '120 FPS']
blackscreen_options = ['Add Black-screen fix (Nintendo UI)', 'Add Black-screen fix (Playstation UI)', 'Add Black-screen fix (Xbox UI)', 'Remove Black-screen fix (UI Compatible)']

resolution_var = tk.StringVar(window)
resolution_var.set(resolutions[0])
resolution_label = tk.Label(window, text="Resolution:")
resolution_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
resolution_dropdown = tk.OptionMenu(window, resolution_var, *resolutions)
resolution_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

framerate_var = tk.StringVar(window)
framerate_var.set(framerates[0])
framerate_label = tk.Label(window, text="Framerate:")
framerate_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
framerate_dropdown = tk.OptionMenu(window, framerate_var, *framerates)
framerate_dropdown.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

blackscreen_var = tk.StringVar(window)
blackscreen_var.set(blackscreen_options[0])
blackscreen_label = tk.Label(window, text="Blackscreen Fix:")
blackscreen_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
blackscreen_dropdown = tk.OptionMenu(window, blackscreen_var, *blackscreen_options)
blackscreen_dropdown.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

# Create the 'Yuzu Folder' selection button
yuzu_folder_path = tk.StringVar(window)
yuzu_folder_label = tk.Label(window, text="Yuzu Folder:", fg="red")
yuzu_folder_label.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
yuzu_folder_button = tk.Button(window, text="Select Folder", command=open_folder_dialog, fg="red")
yuzu_folder_button.grid(row=3, column=2, padx=5, pady=5, sticky=tk.W)

# Autofill Yuzu folder path
appdata_path = get_yuzu_folder_from_appdata()
if appdata_path:
    yuzu_folder_path.set(appdata_path)
    yuzu_folder_label.config(fg="green")
    yuzu_folder_path_value = tk.StringVar(window, value=appdata_path)  # Define yuzu_folder_path_value
    yuzu_folder_entry = tk.Entry(window, textvariable=yuzu_folder_path_value, width=30)
    yuzu_folder_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
    yuzu_folder_button.config(fg="green")
    yuzu_folder_entry.insert(0, appdata_path)  # Insert the path in the entry widget

# Create the 'Generate' button
generate_button = tk.Button(window, text="Generate!", command=generate_config)
generate_button.grid(row=4, column=0, columnspan=3, padx=5, pady=10)

# Hide the command line window
window.iconify()
window.update_idletasks()
window.deiconify()

# Start the main event loop
window.mainloop()

# Compile using "pyinstaller --onefile --add-data "data;data" lazy_pack.py"