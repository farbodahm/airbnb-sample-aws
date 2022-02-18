'''
This files contains main functionality for analyzing rooms related data.
'''
from pyspark.sql import (
    SparkSession,
    DataFrame,
    functions as F,
)


def create_listings_dataframe(spark: SparkSession,
                              dataset_path: str) -> DataFrame:
    ''' Create and return listings data, data frame '''
    listings_df = spark.read.csv(
        header=True,
        inferSchema=True,
        path=dataset_path,
    ).withColumnRenamed(
        'price', 'listings_price'
    )

    return listings_df


def create_calendars_dataframe(spark: SparkSession,
                               dataset_path: str) -> DataFrame:
    ''' Create and return listings data, data frame '''
    calendars_df = spark.read.csv(
        header=True,
        inferSchema=True,
        path=dataset_path,
    )

    # Rename price column and remove '$' sign
    calendars_df = calendars_df.withColumnRenamed(
        'price', 'calendars_price'
    ).withColumn(
        'calendars_price', F.expr("substring(calendars_price, 2, length(calendars_price))")
    )
    # Cast calendars_price from str to int
    calendars_df = calendars_df.withColumn(
        'calendars_price',
        calendars_df[
            'calendars_price'
        ].cast('int').alias('calendars_price'),
    )

    return calendars_df


def main() -> None:
    '''Starting point of analyzing rooms data '''
    spark = SparkSession.builder.appName(
        'Rooms data'
    ).getOrCreate()

    # TODO: Get path as an argument
    listings_df = create_listings_dataframe(
        spark,
        'S3_PATH_TO_LISTINGS_CSV_DATASET',
    )

    # TODO: Get path as an argument
    calendars_df = create_calendars_dataframe(
        spark,
        'S3_PATH_TO_CALENDARS_CSV_DATASET',
    )


main()
