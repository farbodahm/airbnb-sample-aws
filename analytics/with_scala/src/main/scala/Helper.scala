import org.apache.spark.sql.{SaveMode, SparkSession, DataFrame}
import org.apache.spark.sql.functions.{desc, avg, col, expr}

/** Helper functions needed by driver app */
object Helper {

  /** Returns top n rooms in given dataframe
   *
   *  @param listingsDf listings data DataFrame
   *  @param n maximum number of rooms to return
   */
  def getTopNRooms(n: Int): DataFrame => DataFrame = { listingsDf =>
    listingsDf
      .groupBy("room_type")
      .count()
      .orderBy(desc("count"))
      .limit(n)
  } 

  /** Returns average price of given room in given dataframes
   *
   *  @param listingsDf listings data DataFrame
   *  @param calendarsDF calendars data DataFrame
   *  @param roomType room type to get the average
   */
  def getPriceAveragePerRoomtype(
    calendarsDF: DataFrame,
    roomType: String
  ): DataFrame => DataFrame = { listingsDf =>
    val df = listingsDf.join(calendarsDF, listingsDf("id") === calendarsDF("listing_id"))
    df.filter(df("room_type") === roomType)
      .agg(avg(col("calendars_price")))
      .na
      .fill(0)
  }
}
