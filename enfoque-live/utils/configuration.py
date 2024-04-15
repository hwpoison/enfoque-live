import configparser
import logging
import os

config_filename = "config.ini"
section = "DEFAULT"

"""
A simple way to share variables between Gunicorn workers. 
"""

config = configparser.ConfigParser()
config.read(config_filename)

last_modification = os.path.getmtime(config_filename)

def was_modified():
    global last_modification;
    if (current:=os.path.getmtime(config_filename)) > last_modification:
        last_modification = current
        config.read(config_filename)
        print("[+] Reloading configuration file")

def get(key):
    was_modified()
    if section in config and key in config[section]:
        return config[section][key]
    else:
        return None

def set(key, value):
    was_modified()
    if section not in config:
        config[section] = {}
    config[section][key] = value
    with open(config_filename, 'w') as configfile:
        config.write(configfile)


def get_vars():
    config.read(config_filename)
    config_dict = {}
    for key in config["DEFAULT"]:
        key = key.upper()
        config_dict[key] = config["DEFAULT"][key]

    return config_dict


if __name__ == "__main__":
    for a, b in get_vars().items():
        print(a, b)
