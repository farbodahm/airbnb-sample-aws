import org.apache.spark.sql.{SaveMode, SparkSession, DataFrame}
import org.apache.spark.sql.functions.{desc, avg, col, expr}

/** Helper functions needed by driver app */
object Helper {

  /** Returns top n rooms in given dataframe
   *
   *  @param listingsDf listings data DataFrame
   *  @param n maximum number of rooms to return
   */
  def getTopNRooms(listingsDf: DataFrame, n: Int): DataFrame = {
    val topNTypesDf = listingsDf
    .groupBy("room_type")
    .count()
    .orderBy(desc("count"))
    .limit(n)
    
    return topNTypesDf
  } 

  /** Returns average price of given room in given dataframes
   *
   *  @param listingsDf listings data DataFrame
   *  @param calendarsDF calendars data DataFrame
   *  @param roomType room type to get the average
   */
  def getPriceAveragePerRoomtype(
    listingsDf: DataFrame,
    calendarsDF: DataFrame,
    roomType: String
  ): DataFrame = {
    val df = listingsDf.join(calendarsDF, listingsDf("id") === calendarsDF("listing_id"))
    val res = df.filter(df("room_type") === roomType)
      .agg(avg(col("calendars_price")))
      .na
      .fill(0)

    return res
  }
}
