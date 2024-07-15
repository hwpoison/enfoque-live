import json
import os
import time

config_filename = "config.json"
default_section = "default"

config = {}
last_modification = 0

def load():
    global config, last_modification
    try:
        with open(config_filename, 'r') as f:
            config = json.load(f)
            last_modification = os.path.getmtime(config_filename)
        print(f"[+] Configuration loaded from {config_filename}")
    except (OSError, json.JSONDecodeError) as e:
        print(f"Error loading config: {e}")
        config = {}

def save():
    try:
        with open(config_filename, 'w') as f:
            json.dump(config, f, indent=4)
    except OSError as e:
        print(f"Error saving config: {e}")

def delete(key):
    if key in config.get(default_section, {}):
        del config[default_section][key]
        save()

def was_modified():
    global last_modification
    try:
        current_modification = os.path.getmtime(config_filename)
        if current_modification > last_modification:
            load()
            print("[+] Configuration reloaded due to modification")
    except OSError as e:
        print(f"Error checking modification time: {e}")

def get(key, sec=default_section):
    was_modified()
    return config.get(sec, {}).get(key)

def set(key, value, sec=default_section):
    was_modified()
    if sec not in config:
        config[sec] = {}
    config[sec][key] = value
    save()

def get_vars():
    was_modified()
    return config

if __name__ == "__main__":
    load()
    print(config.get_vars())
    s = get("secret_key", "default")
    set("nuevo", "dos", "purchase")
    print(s)
else:
    try:
        load()
    except Exception as e:
        print(f"Problem reading the configuration file {config_filename}: {e}")
        os.sys.exit(1)
