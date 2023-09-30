"""This module contains functions for loading and validating server configuration files."""

import yaml


def read_config(path):
    """Loads yaml config file and returns a dictionary"""
    with open(path, 'r', encoding='UTF-8') as file:
        return yaml.safe_load(file)
