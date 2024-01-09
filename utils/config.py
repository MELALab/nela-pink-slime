from omegaconf import OmegaConf
from os import chdir
from pathlib import Path
import logging
import json

from utils.logging import get_logging_config, set_logging_conf

logger = logging.getLogger(__name__)


def load_conf_and_merge(path=None, args=None):
    """
    Load config file and merge it with current args (if any)

    Args:
        path (str) : Path to config file
        args (Namespace) : argparse arguments to marge with config

    Returns:
        conf (omegaconf.Config) : Merged config
    """

    if path is None and args is None:
        raise ValueError("Cannot pass both `path` and `args` as None.")

    if path is not None:
        with open(path) as fin:
            conf = OmegaConf.load(fin)
        
        # Merge `args` and loaded `conf`
        # NOTE: Duplicate parameters in `conf` will override those in `args`
        if args is not None:
            conf = OmegaConf.merge(vars(args), conf)
    elif args is not None:
        conf = OmegaConf.create(vars(args))  # Otherwise, just initialize OmegaConf
    
    return conf


def init_workspace(config=None, config_path=None, 
                   dump_config=False,
                   do_chdir=True,
                   load_logging_conf=True
                   ):
    """
    Initialize workspace given a `config` object or a `config_path`.
    Will perform tasks such as verifying paths, changing working directory, and loading logging configs.

    Note: config and config_path cannot be simultaneously `None`.
    If both are passed, the config from `config_path` will override `config`.
    Args:
        config (dict, omegaconf.dictConfig) : The config object.
        config_path (str, Path) : The path to the config file.
        dump_config (bool) : If true, save a copy of the config to the target workspace.
        do_chdir (bool) : If `True`, perform chdir to the working directory in config.
        load_logging_conf (bool) : Load logging configs.
    """

    try:
        if config is None and config_path is None:
            logger.critical(f"Neither parameters `config` nor `config_path` were provided.")
            exit(1)
        if config_path:
            config = load_conf_and_merge(config_path)
        # Set up output dir
        config.path.output_dir = Path(config.path.output_dir)
        config.path.data = Path(config.path.data)
        if do_chdir:
            config.path.logging_conf = Path(config.path.logging_conf).absolute()
            config.path.output_dir.mkdir(exist_ok=True, parents=True)
            chdir(config.path.output_dir)
        if load_logging_conf:
            loggingConf = get_logging_config(config.path.logging_conf)
            set_logging_conf(loggingConf)
            
    except Exception as e:
        logger.critical(f"Failed to initialize configs! {e}")

    if dump_config:   # dump config to output dir
        # make config dir and save files
        config_dir = Path("config/")
        config_dir.mkdir(exist_ok=True, parents=True)
        save_config(config, config_dir.joinpath("config.yaml"))
        if load_logging_conf:
            with open(config_dir.joinpath("logging_conf.yaml"), "w") as fout:
                json.dump(loggingConf, fout)

    return config


def save_config(conf, path):
    """
    Save config to path
    """
    with open(path, "w") as fout:
        OmegaConf.save(config=conf, f=fout)