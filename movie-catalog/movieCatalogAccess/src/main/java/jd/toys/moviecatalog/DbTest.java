package jd.toys.moviecatalog;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.List;
import java.util.Map;

public class DbTest {

  public static void go(final List<Map<String, Object>> movies) {

    try (
      Connection conn = DriverManager.getConnection(
        "jdbc:derby:memory:myDB;create=true");
      Statement s = conn.createStatement();) {

      conn.setAutoCommit(false);

      // We create a table...
      s.execute("create table movies(name varchar(250), rel_year int)");
      System.out.println("Created table movies");

      try (
        PreparedStatement psInsert = conn.prepareStatement(
          "insert into movies values (?, ?)");) {
        for (final Map<String, Object> map : movies) {
          psInsert.setString(1, (String) map.get("name"));

          final Object yr = map.get("year");
          final int year = yr == null ? 0 : (int) yr;

          psInsert.setInt(2, year);
          psInsert.executeUpdate();
        }
        System.out.println("Done inserting");
      }

      conn.commit();
      System.out.println("Committed the transaction");

      try (
        ResultSet rs = s.executeQuery(
          "SELECT name, rel_year FROM movies where rel_year < 1965 " +
            "and rel_year > 0 ORDER BY rel_year");
      // "SELECT rel_year, count(*) FROM movies group by rel_year ORDER BY rel_year");
      ) {

        while (rs.next()) {
          System.out.println(rs.getString(1) + " : " + rs.getString(2));

        }
      }

      // // delete the table
      // s.execute("drop table movies");
      // System.out.println("Dropped table location");

      shutdownDb();
    } catch (final SQLException sqle) {
      throw new RuntimeException(sqle);
    }
  }

  private static void shutdownDb() throws SQLException {
    try {
      DriverManager.getConnection("jdbc:derby:;shutdown=true");
    } catch (final SQLException se) {
      if (((se.getErrorCode() == 50000)
      && ("XJ015".equals(se.getSQLState())))) {
        System.out.println("Derby shut down normally");
      } else {
        System.err.println("Derby did not shut down normally");
        throw se;
      }
    }
  }
}
