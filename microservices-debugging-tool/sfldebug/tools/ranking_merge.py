from enum import Enum
from statistics import fmean, median


class RankMergeOperator(Enum):
    """Enum for the ranking merge operators

    Operators:
        AVG: calculates the average/mean of the rankings
        MEDIAN: calculates the median of the rankings
    """
    AVG = 'AVG'
    MEDIAN = 'MEDIAN'

    __MERGE_OPS__ = {
        'AVG': fmean,
        'MEDIAN': median
    }

    def __call__(self, *args):
        return self.__MERGE_OPS__[self.value](*args)
