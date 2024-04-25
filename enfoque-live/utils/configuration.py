import json
import os

config_filename = "config.json"
section = "DEFAULT"

"""
A simple way to share variables between Gunicorn workers. 
"""

config = {}

last_modification = os.path.getmtime(config_filename)


def load():
    with open(config_filename, 'r') as f:
        global config
        config = json.load(f)
    print(f"[+] Configuration loaded from {config_filename}")

def save():
    with open(config_filename, 'w') as f:
        json.dump(config, f, indent=4)

def delete(key):
    del config[section][key]
    save()

# if configuration file was modified, reload it
def was_modified():
    global last_modification;
    if (current:=os.path.getmtime(config_filename)) > last_modification:
        last_modification = current
        with open(config_filename, 'r') as f:
            global config
            config = json.load(f)
        print("[+] Reloading configuration file")

def get(key):
    was_modified()
    if key in config.get(section, {}):
        return config.get(section, {}).get(key)
    else:
        return None

def set(key, value):
    was_modified()
    if section not in config:
        config[section] = {}
    config[section][key] = value
    save()


def get_vars():
    was_modified()
    return config

if __name__ == "__main__":
    load()
    set("test_var", True)
    assert get("test_var") == True
    delete("test_var")
    assert get("test_var") == None
    print("ok")
else:
    try:
        load()
    except:
        print(f"Problem reading the configuration file {config_filename}!!! Please check it!!")
        os.sys.exit(1)