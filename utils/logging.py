import yaml
from yaml import Loader
import logging
import logging.config


def get_logging_config(path_conf="config/logging_conf.yaml"):
    # Load logging configs
    with open(path_conf) as fin:
        loggingConf = yaml.load(fin, Loader)
    return loggingConf


def set_logging_conf(conf):
    logging.config.dictConfig(conf)


def configure_logging(conf=None):
    """
    Calls the configuration method from logging.

    Args:
        conf (str) : The logging config file.
    """
    if conf is None:
        conf = get_logging_config()
    else:
        conf = get_logging_config(conf)
    logging.config.dictConfig(conf)

