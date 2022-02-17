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


def get_price_average_per_roomtype(listings_df: DataFrame,
                                   calendars_df: DataFrame,
                                   room_type: str,
                                   ) -> float:
    '''
    Returns price average per room type.

    Parameters:
        listings_df (DataFrame): Spark DataFrame containing listings data.
        calendars_df (DataFrame): Spark DataFrame containing calendars data.
        room_type (str): Room type name.

    Returns:
        float: Average price per room type
    '''
    df = listings_df.join(calendars_df, listings_df.id == calendars_df.listing_id)
    df = df.filter(
        df['room_type'] == room_type
    ).agg(F.avg(F.col('calendars_price')))
    df = df.na.fill(value=0) # Replace nulls with 0 
    return df.first()[0]
