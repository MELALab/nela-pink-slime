import socket
from urllib.parse import urlparse, urljoin
from pathlib import Path
import json
import time

import logging
from utils.config import init_workspace
from utils.data import load_source_list


logger = logging.getLogger(__name__)


def get_url_domain(url):
    """
    Returns the domain of a given `url`

    Args:
        url (str) : Input url
    
    Returns:
        domain_url (str) : Domain URL
    """
    parsed_url = urlparse(url)
    return urljoin(parsed_url.scheme, parsed_url.netloc)

if __name__ == "__main__":
    config = init_workspace(config_path='config/config.yaml', do_chdir=True)
    logger.info(f"Starting pings")

    sources_path = Path(config.path.data).joinpath("ps_sources.txt")
    sources = load_source_list(sources_path)

    output_file = Path("ipaddrs").joinpath("source_IPs.jsonl")
    output_file.parent.mkdir(exist_ok=True, parents=True)

    with open(f"{output_file}", "w") as fout:
        for src, url in sources:
            domain = get_url_domain(url)
            logger.info(f"Pinging: {domain=}")
            try:
                time.sleep(0.5)  # Sleep before next ping to avoid exceedin rate limits
                hostname, aliaslist, ipaddrlist = socket.gethostbyname_ex(domain)
                obj = {"source": src, "hostname": hostname, "aliaslist": aliaslist, "ipaddrlist": ipaddrlist}
                logger.info(f"Response: {obj=}")
                fout.write(f"{json.dumps(obj)}\n")
            except Exception as e:
                logger.error(f"Failed to get host {src=}, {domain=}")