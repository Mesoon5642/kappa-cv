import json

class ConfigManager:
    """
    Loads JSON config file and provides per-class config blocks.
    """

    def __init__(self, config_path="config.json"):
        with open(config_path, "r") as f:
            self.config = json.load(f)

    def get_class_config(self, class_name):
        if class_name not in self.config:
            raise ValueError(f"No config found for class '{class_name}'")
        return self.config[class_name]