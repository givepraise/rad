from importlib.metadata import distribution
from ..distribution.standard_praise import PraiseDistribution
import plotly.express as px
import numpy as np
import pandas as pd
from IPython.display import Markdown, display
import json


# header = "# Histogram"
# description = f"This is a histogram of the { self.objectName} object. It's stored in /reward_systems/straight_distribution as a regular python module. Apart from perfoming the analysis, it can also output a visual representation with a specific header (above) and description text. "
author = "Nuggan"
Last_updated = "2022."
version = ""


def run(praise_distribution_data, _config={}):
    """
    Runs the main module function: a histogram of the reward distribution among users of the reward system

    Args:
        praise_distribution_data: The object with the reward distribuiton system
    Raises:
        [TODO]: Check for errors and raise them
    Returns:
        res: a DataFrame with the requested results. Contains two columns, "ID" and "AMOUNT TO RECEIVE"

    """

    praisedata = pd.DataFrame(praise_distribution_data.praiseInstance.dataTable)

    quantratingdf = praise_distribution_data.praiseInstance.get_data_by_quantifier()
    quantlist = _get_valid_quantifier(praisedata, quantratingdf)
    metrics_df = _get_participant_metrics(praisedata, quantratingdf, quantlist)

    return metrics_df


def printDescription(praise_distribution_data, _config={}):
    """
    Prints the description of the analysis module to be displayed above the graph

    Args:
        praise_distribution_data: The object with the reward distribuiton system
    Raises:
        [TODO]: Check for errors and raise them
    Returns:
        nothing, it prints the texts

    """
    # name = praise_distribution_data["name"]
    name = praise_distribution_data.name
    # header = f'# "{name}" Histogram'
    description = f"TODO Quant scoring text"

    # display(Markdown(header))
    display(Markdown(description))


def printGraph(praise_distribution_data, _config={"mode": "correlation"}):
    """
    Prints a visualization of the histogram generated by run(). This function is itended to be called from inside the jupyter notebook

    Args:
        praise_distribution_data: The object with the reward distribuiton system
    Raises:
        [TODO]: Check for errors and raise them
    Returns:
        nothing, it prints the figure

    """

    quantifier_metrics_df = pd.DataFrame(run(praise_distribution_data, _config))

    if _config["mode"] == "correlation":
        fig = px.scatter(
            quantifier_metrics_df.sort_values(by="pearson_coef"),
            y="pearson_coef",
            title="How similiar is one's score with the other quantifiers?",
        )
    if _config["mode"] == "displacement":
        fig = px.bar(
            quantifier_metrics_df.sort_values(by="av_score_displacement"),
            y="av_score_displacement",
            title="Do one tends to give higher or lower scores than the other quantifiers?",
        )
    fig.show()


def _get_valid_quantifier(_df, _quantifier_rating_table):

    quant_cols = _df.filter(like="USERNAME", axis=1)
    quantlist = np.unique(quant_cols.values)
    valid_qt = np.ones_like(quantlist, dtype=bool) * True
    for kq, quantid in enumerate(quantlist):
        quantdf = _quantifier_rating_table.loc[
            _quantifier_rating_table["QUANT_ID"] == quantid
        ]
        # exclude invalid IDs
        if len(quantdf) == 0:
            valid_qt[kq] = False
        if set(quantdf["QUANT_VALUE"].values) == {0}:
            valid_qt[kq] = False
        if quantid == "None":
            valid_qt[kq] = False
    quantlist = quantlist[valid_qt]
    return quantlist


def _get_participant_metrics(_df, _quantifier_rating_table, _quantlist):
    # TODO: make this more modularized so the user can easily choose what analysis to include
    quantifier_coef = []
    quantifier_score_displace = []

    for QUANT_ID in _quantlist:
        quantdf = _quantifier_rating_table.loc[
            _quantifier_rating_table["QUANT_ID"] == QUANT_ID
        ]
        av_scores_others = []
        score_quant = []
        scoredist = []
        scoredisplace = []
        for kr, row in quantdf.iterrows():
            quantifier_score = row["QUANT_VALUE"]
            if np.isnan(quantifier_score):
                continue
            praise_id = row["PRAISE_ID"]
            praise_row = _df.loc[_df["ID"] == praise_id]

            otherscores = praise_row.filter(like="SCORE ").values.tolist()[0]
            otherscores.remove(quantifier_score)

            otherscores = np.array(otherscores)
            otherscores = otherscores[~np.isnan(otherscores)]

            if len(otherscores) < 2:
                continue
            av_scores_others.append(np.mean(otherscores))
            score_quant.append(quantifier_score)
            # like "standar deviation" from this score
            scoredist.append(
                np.sqrt(sum((quantifier_score - otherscores) ** 2)) / (len(otherscores))
            )
            scoredisplace.append(np.mean(quantifier_score - otherscores))

        coef = np.corrcoef(score_quant, av_scores_others)[1, 0]
        quantifier_coef.append(coef)
        quantifier_score_displace.append(np.mean(scoredisplace))
    quantifier_metrics_df = pd.DataFrame(
        index=_quantlist,
        data={
            "pearson_coef": quantifier_coef,
            "av_score_displacement": quantifier_score_displace,
        },
    )
    return quantifier_metrics_df
