import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox

CONFIG_FILE = "config.json"
MOD_EXTENSIONS = ['.pak', '.ucas', '.utoc']
DISABLED_SUFFIX = '.disabled'

BG_COLOR = "#1e1e1e"
FG_COLOR = "#ffffff"
BTN_COLOR = "#2e2e2e"
BTN_HOVER = "#3e3e3e"
DISABLED_COLOR = "#cc6666"
ENABLED_COLOR = "#66cc99"

def save_config(folder_path):
    with open(CONFIG_FILE, 'w') as f:
        json.dump({'mod_folder': folder_path}, f)

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            try:
                config = json.load(f)
                return config.get('mod_folder')
            except json.JSONDecodeError:
                return None
    return None

def find_mods(folder):
    mods = {}
    for filename in os.listdir(folder):
        for ext in MOD_EXTENSIONS:
            if filename.endswith(ext) or filename.endswith(ext + DISABLED_SUFFIX):
                base = filename.split(ext)[0]
                if base.endswith(DISABLED_SUFFIX):
                    base = base.replace(DISABLED_SUFFIX, '')
                mods.setdefault(base, []).append(filename)
    return mods

def is_disabled(filename):
    return filename.endswith(DISABLED_SUFFIX)

def toggle_mod(folder, modname, status_label):
    files = [f"{modname}{ext}" for ext in MOD_EXTENSIONS]
    disabled_files = [f + DISABLED_SUFFIX for f in files]
    
    enabled = all(os.path.exists(os.path.join(folder, f)) for f in files)
    disabled = all(os.path.exists(os.path.join(folder, f)) for f in disabled_files)
    
    if enabled:
        for f in files:
            os.rename(os.path.join(folder, f), os.path.join(folder, f + DISABLED_SUFFIX))
        status_label.config(text="Disabled", fg=DISABLED_COLOR)
    elif disabled:
        for f in disabled_files:
            new_name = f.replace(DISABLED_SUFFIX, '')
            os.rename(os.path.join(folder, f), os.path.join(folder, new_name))
        status_label.config(text="Enabled", fg=ENABLED_COLOR)
    else:
        messagebox.showerror("Error", f"Mod {modname} is in a broken or mixed state.")

def on_hover(event, widget):
    widget.config(bg=BTN_HOVER)

def on_leave(event, widget):
    widget.config(bg=BTN_COLOR)

def build_gui(mod_folder):
    root = tk.Tk()
    root.title("Mod Manager")
    root.geometry("500x600")
    root.configure(bg=BG_COLOR)

    top_frame = tk.Frame(root, bg=BG_COLOR)
    top_frame.pack(fill=tk.X, pady=10)

    change_btn = tk.Button(
        top_frame, text="Change Folder", command=lambda: choose_folder(root),
        bg=BTN_COLOR, fg=FG_COLOR, activebackground=BTN_HOVER, relief=tk.FLAT
    )
    change_btn.pack(pady=5)
    change_btn.bind("<Enter>", lambda e: on_hover(e, change_btn))
    change_btn.bind("<Leave>", lambda e: on_leave(e, change_btn))

    mods_frame = tk.Frame(root, bg=BG_COLOR)
    mods_frame.pack(fill=tk.BOTH, expand=True)

    mods = find_mods(mod_folder)
    if not mods:
        tk.Label(mods_frame, text="No mods found in folder.", fg=FG_COLOR, bg=BG_COLOR).pack()
    else:
        for mod, files in mods.items():
            row = tk.Frame(mods_frame, bg=BG_COLOR)
            row.pack(fill=tk.X, pady=5, padx=10)

            mod_label = tk.Label(row, text=mod, fg=FG_COLOR, bg=BG_COLOR, anchor="w")
            mod_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

            status = "Disabled" if any(is_disabled(f) for f in files) else "Enabled"
            color = DISABLED_COLOR if status == "Disabled" else ENABLED_COLOR
            status_label = tk.Label(row, text=status, fg=color, bg=BG_COLOR, width=10)
            status_label.pack(side=tk.LEFT)

            toggle_button = tk.Button(
                row, text="Toggle", bg=BTN_COLOR, fg=FG_COLOR,
                command=lambda m=mod, l=status_label: toggle_mod(mod_folder, m, l),
                activebackground=BTN_HOVER, relief=tk.FLAT
            )
            toggle_button.pack(side=tk.RIGHT, padx=5)
            toggle_button.bind("<Enter>", lambda e, b=toggle_button: on_hover(e, b))
            toggle_button.bind("<Leave>", lambda e, b=toggle_button: on_leave(e, b))

    root.mainloop()

def choose_folder(parent=None):
    folder = filedialog.askdirectory(title="Select Mod Folder")
    if folder:
        save_config(folder)
        if parent:
            parent.destroy()
        build_gui(folder)

def start_app():
    saved_folder = load_config()
    if saved_folder and os.path.isdir(saved_folder):
        build_gui(saved_folder)
    else:
        choose_folder()

if __name__ == "__main__":
    start_app()
