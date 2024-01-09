"""
Perform the cross-referencing of news sources from each network with the sources in our dataset.
"""
import logging
import re

from pathlib import Path

import pandas as pd


logger = logging.getLogger(__name__)

from utils.config import init_workspace


if __name__ == "__main__":
    config = init_workspace(config_path="config/config.yaml")
    
    # Read NELA PS sources
    with open(config.path.data.joinpath("ps_sources.txt")) as fin:
        ps_sources = list()
        for line in fin:
            src, feed = line.strip().split(',', 1)
            ps_sources.append((src, feed))
    
    # Read media networks sources
    media_network_dir = Path("media_network_lists")
    network_sources = dict()
    sources_network = dict()

    for file in media_network_dir.iterdir():
        network = file.stem
        logger.info(f"{network}")
        with open(file) as fin:
            n_sources = [line.strip().lower() for line in fin.readlines() if len(line) > 0]
        n_sources = list(map(lambda s: re.sub('(\.com|\W+)', '', s), n_sources))
        network_sources[network] = set(n_sources)
        for s in n_sources:
            logger.info(f"{s=} {network=}")
            sources_network[s] = network
    

    cross_data = list()
    for src, feed in ps_sources:
        if src in sources_network:
            cross_data.append((src, sources_network[src]))
        else:
            cross_data.append((src, 'UNKNOWN'))
    
    df = pd.DataFrame(cross_data, columns=['source', 'network'])
    df.to_csv("source_network.csv", index=None)
