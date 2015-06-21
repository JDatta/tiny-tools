package jd.toys.moviecatalog;

import java.io.File;
import java.util.List;

import jd.toys.moviecatalog.jpa.entities.Movie;
import jd.toys.moviecatalog.jpa.impl.JPAManager;

import org.codehaus.jackson.map.ObjectMapper;
import org.codehaus.jackson.type.TypeReference;

public class CatalogBrowser {

  private static void printMovies(final List<Movie> movies) {
    for (final Movie m : movies) {
      System.out.print("Id: " + m.getId());
      System.out.print(" Name: " + m.getName());

      if (m.getImdb() != null) {
        System.out.print(" Rating: " + m.getImdb().getImdbRating());
      }
      System.out.println(" Year: " + m.getYear());
    }
  }

  public static void main(final String[] args)
    throws Exception {

    final ObjectMapper mapper = new ObjectMapper();
    final List<Movie> movies =
      mapper.readValue(new File("data/movies.json"),
        new TypeReference<List<Movie>>() {
        });
    try (MovieManager movieManager = new JPAManager()) {
      long t0 = System.currentTimeMillis();
      movieManager.save(movies);
      long t1 = System.currentTimeMillis();
      System.out.println("Time to Save: " + (t1 - t0));
      t0 = System.currentTimeMillis();
      final List<Movie> movies4mDB = movieManager.list();
      t1 = System.currentTimeMillis();
      System.out.println("Time to Retrieve: " + (t1 - t0));
      printMovies(movies4mDB);

    }
  }
}
