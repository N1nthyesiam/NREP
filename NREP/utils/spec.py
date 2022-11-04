import json

class adict(dict):
    __slots__ = ()
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__

class Config:
    def __init__(self, config_path):
        with open(config_path) as file:
            self.config = adict(json.load(file))

    def __getattr__(self, attr):
        return getattr(self.config, attr)