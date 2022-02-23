import org.apache.spark.sql.{SparkSession, DataFrame}
import org.apache.spark.sql.functions.{desc, avg, col, expr}

/** Used for building dataframes with needed transformations */
object DataFrameBuilder {

  /** Creates listings DataFrame with needed transformations
   *
   *  @param spark created Spark session
   *  @param datasetPath path where the dataset is in it
   */
  def createListingsDataFrame(
    spark: SparkSession,
    datasetPath: String
  ): DataFrame = {
    val listingsDf = spark.read
      .format("csv")
      .option("header", "true")
      .option("inferSchema", "true")
      .load(datasetPath)
      .withColumnRenamed("price", "listings_price") // To avoid conflict with `price` column in 
    
    return listingsDf
  }

  /** Creates calendars DataFrame with needed transformations
   *
   *  @param spark created Spark session
   *  @param datasetPath path where the dataset is in it
   */
  def createCalendarsDataFrame(
    spark: SparkSession,
    datasetPath: String
  ): DataFrame = {
    var calendarsDf = spark.read
      .format("csv")
      .option("header", "true")
      .option("inferSchema", "true")
      .load(datasetPath)
      .withColumnRenamed("price", "calendars_price")
      .withColumn("calendars_price", expr("substring(calendars_price, 2, length(calendars_price))"))
    
    calendarsDf = calendarsDf.withColumn("calendars_price", calendarsDf("calendars_price").cast("int").alias("calendars_price"))

    return calendarsDf
  }
}
