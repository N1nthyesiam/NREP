import json

class adict(dict):
    __slots__ = ()
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__

class Config():
    def __init__(self, config_path: str):
        self.config_path = config_path
        with open(self.config_path) as file:
            self.config = adict(json.load(file))

    def __getattr__(self, attr):
        return getattr(self.config, attr)

    def update(self, data: dict):
        self.config.update(data)
        with open(self.config_path, 'w') as file:
            json.dump(self.config, file, indent=1)