import yaml


def read_config(path):
    with open(path, 'r') as file:
        return yaml.safe_load(file)
