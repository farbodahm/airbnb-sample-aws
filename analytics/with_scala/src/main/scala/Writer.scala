import org.apache.spark.sql.{DataFrame}

/** For writing result */
object Writer {

  /** Writes the given dataframe to the given path with given options
   *
   *  @param df dataframe that will be written in file
   *  @param path path to write the given dataframe
   *  @param format format used to write file (Default: csv)
   *  @param mode how to write to file (Default: OVERWRITE)
   */
  def writeDataFrameToFile(
    df: DataFrame,
    path: String,
    format: String = "csv",
    mode: String = "OVERWRITE"
  ): Unit = {
    df.write
      .format(format)
      .mode(mode)
      .save(path)
  }
}
