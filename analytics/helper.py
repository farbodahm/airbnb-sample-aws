from typing import Tuple, List
from pyspark.sql import (
    SparkSession,
    functions as F,
    DataFrame,
)

def get_top_n_room_types(listings_df: DataFrame,
                          n: int,
                          ) -> List[Tuple[str, int]]:
    '''
    Returns top n room types.

    Parameters:
        listings_df (DataFrame): Spark DataFrame containing listings data.
        n (int): Top n room types.

    Returns:
        List[Tuple[str, int]]: An array of tuples in form of (room_type: str, count: int)
    '''
    top_n_types_collection = listings_df.groupBy(
        'room_type'
        ).count().orderBy(
            'count', ascending=False
        ).limit(
            n
        ).collect()
    
    return [(room[0], room[1]) for room in top_n_types_collection]