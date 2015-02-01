package jd.toys.moviecatalog;

import java.io.File;
import java.io.IOException;
import java.util.List;

import jd.toys.moviecatalog.hibernate.MovieManager;
import jd.toys.moviecatalog.hibernate.entities.Movie;

import org.codehaus.jackson.JsonParseException;
import org.codehaus.jackson.map.JsonMappingException;
import org.codehaus.jackson.map.ObjectMapper;
import org.codehaus.jackson.type.TypeReference;

public class CatalogBrowser {

  private static void dbRW(final List<Movie> movies)
    throws Exception {
    try (MovieManager movieManager = new MovieManager()) {
      movieManager.save(movies);

      final List<Movie> movies_back = movieManager.list();
      for (final Movie m : movies_back) {
        System.out.print("Id: " + m.getId());
        System.out.print(" Name: " + m.getName());
        System.out.print(" Year: " + m.getYear());
        System.out.println(" Path: " + m.getAbsPath());
      }
    }
  }

  public static void jsonReadingTest(final ObjectMapper mapper)
    throws JsonParseException, JsonMappingException, IOException {
    final List<Movie> movies =
      mapper.readValue(
        new File("data/movies.json"), new TypeReference<List<Movie>>() {
        });
    for (final Movie movie : movies) {
      System.out.println(movie.getName() + " : " + movie.getYear());
      if (movie.getImdb() != null) {
        System.out.println(">>>IMDB::" + movie.getImdb().getImdbRating());
      }
    }
  }

  public static void main(final String[] args)
    throws Exception {

    final ObjectMapper mapper = new ObjectMapper();

    // jsonReadingTest(mapper);

    final List<Movie> movies =
      mapper.readValue(new File("data/movies.json"),
        new TypeReference<List<Movie>>() {
        });
    dbRW(movies);
  }
}
