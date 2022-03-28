from enum import Enum
from statistics import fmean, median


class RankMergeOperator(Enum):
    """Enum for the ranking merge operators

    Operators:
        AVG: calculates the average/mean of the rankings
        MEDIAN: calculates the median of the rankings
    """
    AVG = fmean
    MEDIAN = median
