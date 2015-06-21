package jd.toys.moviecatalog;

import java.util.List;

import jd.toys.moviecatalog.jpa.entities.Movie;

public interface MovieManager extends AutoCloseable {

  void save(List<Movie> movies);

  List<Movie> list();

  @Override
  void close() throws Exception;

}
