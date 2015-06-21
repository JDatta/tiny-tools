package jd.toys.moviecatalog.jpa.entities;

import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.GeneratedValue;
import javax.persistence.GenerationType;
import javax.persistence.Id;
import javax.persistence.Table;

@Entity
@Table(name = "imdb")
public class Imdb {

  @Id
  @GeneratedValue(strategy = GenerationType.AUTO)
  private long id;

  // @Id
  private String imdbID;

  @Column(length = 1024)
  private String actors;

  private String awards;
  private String country;

  @Column(length = 1024)
  private String director;

  private String genre;
  private String language;
  private String metascore;

  @Column(length = 1024)
  private String plot;
  private String poster;
  private String rated;
  private String released;
  private String response;
  private String runtime;
  private String title;
  private String type;

  @Column(length = 1024)
  private String writer;

  @Column(name = "imdb_year")
  private String year;

  private String imdbRating;
  private String imdbVotes;

  public String getActors() {
    return this.actors;
  }

  public void setActors(final String actors) {
    this.actors = actors;
  }

  public String getAwards() {
    return this.awards;
  }

  public void setAwards(final String awards) {
    this.awards = awards;
  }

  public String getCountry() {
    return this.country;
  }

  public void setCountry(final String country) {
    this.country = country;
  }

  public String getDirector() {
    return this.director;
  }

  public void setDirector(final String director) {
    this.director = director;
  }

  public String getGenre() {
    return this.genre;
  }

  public void setGenre(final String genre) {
    this.genre = genre;
  }

  public String getLanguage() {
    return this.language;
  }

  public void setLanguage(final String language) {
    this.language = language;
  }

  public String getMetascore() {
    return this.metascore;
  }

  public void setMetascore(final String metascore) {
    this.metascore = metascore;
  }

  public String getPlot() {
    return this.plot;
  }

  public void setPlot(final String plot) {
    this.plot = plot;
  }

  public String getPoster() {
    return this.poster;
  }

  public void setPoster(final String poster) {
    this.poster = poster;
  }

  public String getRated() {
    return this.rated;
  }

  public void setRated(final String rated) {
    this.rated = rated;
  }

  public String getReleased() {
    return this.released;
  }

  public void setReleased(final String released) {
    this.released = released;
  }

  public String getResponse() {
    return this.response;
  }

  public void setResponse(final String response) {
    this.response = response;
  }

  public String getRuntime() {
    return this.runtime;
  }

  public void setRuntime(final String runtime) {
    this.runtime = runtime;
  }

  public String getTitle() {
    return this.title;
  }

  public void setTitle(final String title) {
    this.title = title;
  }

  public String getType() {
    return this.type;
  }

  public void setType(final String type) {
    this.type = type;
  }

  public String getWriter() {
    return this.writer;
  }

  public void setWriter(final String writer) {
    this.writer = writer;
  }

  public String getYear() {
    return this.year;
  }

  public void setYear(final String year) {
    this.year = year;
  }

  public String getImdbID() {
    return this.imdbID;
  }

  public void setImdbID(final String imdbID) {
    this.imdbID = imdbID;
  }

  public String getImdbRating() {
    return this.imdbRating;
  }

  public void setImdbRating(final String imdbRating) {
    this.imdbRating = imdbRating;
  }

  public String getImdbVotes() {
    return this.imdbVotes;
  }

  public void setImdbVotes(final String imdbVotes) {
    this.imdbVotes = imdbVotes;
  }
}
