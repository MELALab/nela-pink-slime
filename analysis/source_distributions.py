import logging
import pandas as pd
from pathlib import Path


from utils.config import init_workspace


logger = logging.getLogger(__name__)


if __name__ == "__main__":
    config = init_workspace(config_path="config/config.yaml", do_chdir=True)
    input_file = config.path.data.joinpath("source_network_ip.csv")
    print(Path.cwd())
    df = pd.read_csv(input_file, header=None)
    df.columns = ['source', 'network', 'ipaddr']

    g = df.groupby(['network'])
    unique_ips = g['ipaddr'].unique()
    n_unique_ips = g['ipaddr'].nunique()
    print(n_unique_ips)