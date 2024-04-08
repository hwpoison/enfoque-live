import configparser


filename = "config.ini"
section = "DEFAULT"

"""
A simple way to share variables between Gunicorn workers. 
TODO: Solve the intensive IO activity over the conf file every each get/set
"""

config = configparser.ConfigParser()


def get(key):
    config.read(filename)
    if section in config and key in config[section]:
        return config[section][key]
    else:
        return None


def set(key, value):
    config.read(filename)
    if section not in config:
        config[section] = {}
    config[section][key] = value
    with open(filename, 'w') as configfile:
        config.write(configfile)


def get_vars():
    config.read(filename)
    config_dict = {}
    for key in config["DEFAULT"]:
        key = key.upper()
        config_dict[key] = config["DEFAULT"][key]

    return config_dict


if __name__ == "__main__":
    for a, b in get_vars().items():
        print(a, b)
