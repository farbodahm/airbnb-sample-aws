import org.apache.spark.sql.{SaveMode, SparkSession, DataFrame}
import org.apache.spark.sql.functions.{desc, avg, col, expr}

import Helper.{getPriceAveragePerRoomtype, getTopNRooms}
import DataFrameBuilder.{createListingsDataFrame, createCalendarsDataFrame}
import Writer.{writeDataFrameToFile}

/** Driver code */
object Main {

  // Create Spark session
  val spark = SparkSession.builder
    .appName("Rooms Analytics")
    .master("local[*]")
    .getOrCreate
  
  // Set log level to WARN (Default: INFO)
  spark.sparkContext.setLogLevel("WARN")

  // TODO: Take the paths as an argument
  val listingsDf = createListingsDataFrame(spark, "S3_PATH_TO_LISTINGS_DATA")
  val calendarsDf = createCalendarsDataFrame(spark, "S3_PATH_TO_CALENDARS_DATA")

  // Analytics about room types
  // TODO: Take the paths as an argument
  val topNRooms = listingsDf.transform(getTopNRooms(3))
  writeDataFrameToFile(topNRooms, "S3_PATH_TO_WRITE_DATA")

  // Analytics about room average price
  // TODO: Take the paths as an argument
  for (row <- topNRooms.collect()) {
    val df = listingsDf.transform(getPriceAveragePerRoomtype(calendarsDf, row.get(0).asInstanceOf[String]))
    writeDataFrameToFile(df, "S3_PATH_TO_WRITE_DATA")
  }

}
