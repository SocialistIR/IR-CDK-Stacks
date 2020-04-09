import os
from configparser import ConfigParser


class Config:
    CONFIG_FILE = "config.ini"

    @classmethod
    def get_config(cls):
        config = ConfigParser()
        if os.path.isfile(cls.CONFIG_FILE):
            config.read(cls.CONFIG_FILE)
        else:
            cls.save_config(config)
        return config

    @classmethod
    def save_config(cls, config):
        with open(cls.CONFIG_FILE, "w") as f:
            config.write(f)
