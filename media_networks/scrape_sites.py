import requests
from bs4 import BeautifulSoup
from pathlib import Path
import logging

from utils.config import init_workspace

logger = logging.getLogger(__name__)

def get_metric_media():
    """
    Fetch the list of sites from Metric Media News

    Returns:
        sources (list[str]) : The list of source names.
    """
    url = "https://metricmedianews.com/"

    r = requests.get(url)
    soup = BeautifulSoup(r.content, features="html.parser")

    sources = list()
    links = soup.find_all("a")
    for item in links:
        sources.append(item.text)

    return sources


def get_franklin_archer():
    url = "https://web.archive.org/web/20200501201541/https://franklinarcher.com/our_publications"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, features="html.parser")

    sources = list()
    links = soup.find_all("a")
    for item in links:
        sources.append(item.text)

    return sources


def get_lgis():
    url = "https://lgis.co/our_publications"
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(r.content, features="html.parser")
    print(soup)
    sources = list()
    links = soup.find_all("a")
    for item in links:
        if len(item.text.strip()) > 0:
            sources.append(item.text.strip())

    return sources


if __name__ == "__main__":
    config = init_workspace(config_path="config/config.yaml")
    mm_sources = get_metric_media() 
    logger.info(f"Got {len(mm_sources)} sources from Metric Media News")

    path_mm = Path("media_network_lists").joinpath("metric_media.txt")
    path_mm.parent.mkdir(exist_ok=True, parents=True)

    with open(path_mm, "w") as fout:
        for s in mm_sources:
            fout.write(f"{s}\n")

    fa_sources = get_franklin_archer()
    path_fa = Path("media_network_lists").joinpath("franklin_archer.txt")
    with open(path_fa, "w") as fout:
        for s in fa_sources:
            fout.write(f"{s}\n")
    lgis_sources = get_lgis()
    logger.info(f"Got {len(lgis_sources)} sources from LGIS")
    path_fa = Path("media_network_lists").joinpath("lgis.txt")
    with open(path_fa, "w") as fout:
        for s in lgis_sources:
            fout.write(f"{s}\n")

    


