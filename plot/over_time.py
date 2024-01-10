import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import seaborn as sns
from pathlib import Path
import logging
import pandas as pd
import sqlite3
import numpy as np


from utils.config import init_workspace


logger = logging.getLogger(__name__)


# colors = [
#             "#003f5c",
#             "#2f4b7c",
#             "#665191",
#             "#a05195",
#             "#d45087",
#             "#f95d6a",
#             "#ff7c43",
#             "#ffa600",
#             "#BBBBBB"
#             ]

colors = [
            "#003f5c",
            "#2f4b7c",
            "#665191",
            "#ffa600",
            "#a05195",
            "#d45087",
            "#f95d6a",
            "#ff7c43",
            "#BBBBBB"
            ]


# Get articles per source as multiple time series
def get_article_timeseries(con, days=7, group_by="source"):
    """
    Run a query to select number of articles published by each source.
    Creating multiple time series (one per source) containing that information.
    :param con: Connection to NELA database.
    :param days: (int) Size of the bucket (in days).
    :param group_by: (str) Aggregate results by this column. If None, results are not aggregated. Default: 'source'.
    :return: (DataFrame) r.
    """
    # Select everything while grouping by the closes multiple of minutes
    # This is an easy way of grouping results into time slices since we have
    # the created_utc timestamp to work with
    # Multiply days by seconds*minutes*hours to get seconds
    seconds = 60*60*24*days
    query = f"SELECT published_utc/{seconds} as published_utc, date(published_utc, 'unixepoch') as date, count(id) as articles, \
           {group_by} FROM newsdata " \
            f"GROUP BY published_utc/({seconds})"
    if group_by is not None:
        query += f", {group_by}"
    r = pd.read_sql_query(query, con)
    return r


def generate_stack_plot(path, t, category_column, categories, colors,
                        fontsize=22,
                        x_label="Month",
                        y_label="Articles",
                        x_interpolate=[],
                        col_interpolate=None,
                        hatch="//",
                        baseline="zero"):
    """
    Create a stacked plot. Saves image to `path` and creates the legend separately, saving it to legend_`path`.
    :param path: Path to save figure (PDF) to.
    :param t: Dataframe with time series.
    :param category_group: The name of the column to group by.
    :param colors: List of colors for each category.
    :param labels_to_sources: dict{label, source}.
    :param fontsize: int, fontsize of the plotted image.
    :param x_label: Label for the x axis.
    :param y_label: Label for the y axis.
    :param x_interpolate: List of points (a,b) to interpolate. Area in (a,b) is filled with the average y in (a,b).
    :param col_interpolate: Color of interpolated area as color name or RGB hex string (str).
    :param hatch: (str) Hatch pattern.
    :return:
    """
    x_indices = np.array(list(range(0,len(t["published_utc"].unique()))))
    x_dates = np.array(list(t['date'].unique()))
    path = Path(path)
    stacks = np.zeros((len(categories),
                       len(x_indices)))
    labels = list()
    fig, ax = plt.subplots(figsize=(14, 8))
    fig.set_tight_layout(True)
    for i, category in enumerate(categories):
        print(category)
        t_cat = t[t[category_column] == category]

        for j, row in enumerate(t_cat.itertuples()):
            stacks[i][j] = row.articles

        # spl = make_interp_spline(x_indices, x_cat, k=3)
        # x_smooth = spl(x_indices)
        labels.append(category)

    i_stack = np.zeros(stacks[0].shape)
    for a, b in x_interpolate:
        for j in range(a, b + 1):
            y_interpolated = 0
            for i in range(len(stacks)):
                y_interpolated += (stacks[i][b] + stacks[i][a] + stacks[i][j]) / 3
            i_stack[j] = y_interpolated
        st = ax.stackplot(x_indices, i_stack, baseline=baseline, color=col_interpolate, alpha=0.60, labels=["Missing data"])
        st[0].set_hatch(hatch)
    plots = ax.stackplot(x_indices, stacks, baseline=baseline, alpha=0.9,
                         colors=colors[:len(stacks)])

    #  TICKS AND GRID
    # major_ticks = np.arange(0, len(x_indices)+1, 4)
    # minor_ticks = np.arange(0, len(x_indices), 2)
    major_ticks = np.arange(0, len(x_dates)+1, 3)
    minor_ticks = np.arange(0, len(x_indices)+1, 1.5)

    ax.set_xticks(major_ticks)
    ax.set_xticks(minor_ticks, minor=True)
    ax.set_xticklabels(x_dates[major_ticks], rotation=30, ha="right")
    # ax.set_yscale('log')
    plt.xticks(fontsize=fontsize)
    plt.yticks(fontsize=fontsize)

    ax.xaxis.grid(which="major")
    ax.xaxis.grid(which="minor", alpha=0.5, linestyle="--")

    plt.xlabel(x_label, fontsize=fontsize)
    plt.ylabel(y_label, fontsize=fontsize)
    fig.savefig(path, format="pdf")

    # Manually make legend
    figleg, axleg = plt.subplots(figsize=(10, 0.5))
    legend_elem = list()
    for i, c in enumerate(categories):
        p = Patch(facecolor=colors[i], label=categories[i])
        legend_elem.append(p)

    if len(x_interpolate) > 0:
        p = Patch(facecolor=col_interpolate, edgecolor="black", hatch=hatch, label="Missing data", alpha=0.6)
        # p = Patch(fill=False, hatch=hatch, label="Missing data")
        p.set_hatch(hatch)
        legend_elem.append(p)

    axleg.legend(ncol=3, handles=legend_elem, loc="center",
                 fontsize=fontsize)
    axleg.axis("off")
    # plt.tight_layout()
    figleg.savefig(path.parent.joinpath(f"{path.stem}_legend{path.suffix}"), format="pdf", bbox_inches="tight")


if __name__ == "__main__":
    config = init_workspace(config_path='config/config.yaml')
    output_dir = Path("plots")
    output_dir.mkdir(exist_ok=True, parents=True)

    if not Path("articles_over_time.csv").exists():
        con = sqlite3.connect(config.path.data.joinpath("nela_ps_final.db"))
        # Get article timeseries
        a_ts = get_article_timeseries(con, days=30, group_by='network')
        # Shift timestamps to 0 (in weeks)
        shift = a_ts["published_utc"].min()
        a_ts["published_utc"] = a_ts["published_utc"] - a_ts["published_utc"].min() + 1
        a_ts.to_csv("articles_over_time.csv", index=None)

    a_ts = pd.read_csv("articles_over_time.csv")
    print(a_ts)

    network_labels = {
        'metric_media': 'Metric Media News',
        'franklin_archer': 'Franklin Archer',
        'metro_business': 'Metro Business',
        'the_record': 'The Record',
        'lgis': "LGIS",
        "local_labs": "Local Labs"
    }
    for n in network_labels:
        a_ts['network'] = a_ts['network'].str.replace(n, network_labels[n])
    a_ts['date'] = a_ts['date'].apply(lambda s: s.rsplit('-', 1)[0])

    print(a_ts)
    category_column = 'network'
    category_groups = ['Metric Media', 
                       'Franklin Archer',  
                       'Record', 
                       'Metro Business Network (Franklin Archer)',
                       'LGIS', 
                       'American Catholic Tribune Media Network', 
                       'Locality Labs']
    generate_stack_plot('plots/stack_plot.pdf', a_ts, category_column, category_groups, colors)
