'''
This files contains main functionality for analyzing rooms related data.
'''
from pyspark.sql import (
    SparkSession,
    DataFrame,
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


def main() -> None:
    '''Starting point of analyzing rooms data '''
    spark = SparkSession.builder.appName(
        'Rooms data'
    ).getOrCreate()

    listings_df = create_listings_dataframe(
        spark,
        'S3_PATH_TO_LISTINGS_CSV_DATASET',
    )


main()
