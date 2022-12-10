from .straight_distribution.distribution.straightDistribution import (
    StraightDistribution,
)

from .praise.distribution.standard_praise import PraiseDistribution




import pandas as pd


# [TODO] reasses if there is a better way to do this


def build_distribution_object(_name, _type, _params, _sources):
    """
    Creates a distribution system object of a specfic type

    Args:
        _name: String specifying the name of the reward system
        _params: the parameters with which to instantiate it
    Raises:
        [TODO]: Check for errors and raise them
    Returns:
        cls: An instance of the distributions system

    """
    if _type == "standard_praise":
        return create_praise_distribution(_name, _params, _sources)
    if _type == "straight":
        return create_straight_distribution(_name, _params, _sources)
    if _type == "sourcecred":
        print("sourcecred not implemented")
        pass


def create_straight_distribution(_name, _params, _sources):
    """
    Creates a straight distribution object

    Args:
        _params: the parameters with which to instantiate it
    Raises:
        [TODO]: Check for errors and raise them
    Returns:
        cls: An instance of a straight distribution
    """
    return StraightDistribution.generate_from_params(_name, _params, _sources)


def create_praise_distribution(_name, _params, _sources):
    """
    Creates a Praise object

    Args:
        _params: the parameters with which to instantiate it
    Raises:
        [TODO]: Check for errors and raise them
    Returns:
        cls: An instance of a praise distribution
    """
    return PraiseDistribution.generate_from_params(_name, _params, _sources)
