from pathlib import Path


def load_source_list(path):
    """
    Loads the text file containing the list of sources and feeds.

    Args:
        path (str or Path) : Path to input file.

    Returns:
        sources (list[tuple(str,str)]) : List of tuples containing (source_name, feed_url).
    """

    with open(path) as fin:
        lines = list(map(lambda s: s.strip(), fin.readlines()))
    sources = list(map(lambda s: tuple(s.split(',', 1)), lines))
    return sources