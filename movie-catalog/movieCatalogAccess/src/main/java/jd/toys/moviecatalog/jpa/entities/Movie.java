package jd.toys.moviecatalog.jpa.entities;

import java.util.List;

import javax.persistence.CascadeType;
import javax.persistence.Column;
import javax.persistence.ElementCollection;
import javax.persistence.Entity;
import javax.persistence.GeneratedValue;
import javax.persistence.GenerationType;
import javax.persistence.Id;
import javax.persistence.OneToOne;
import javax.persistence.Table;

@Entity
@Table(name = "movie")
public class Movie {

  @Id
  @GeneratedValue(strategy = GenerationType.AUTO)
  private long id;

  @Column(length = 1024)
  private String absPath;

  private String dirBasename;
  private String ext;
  private String filename;
  private String humanSize;

  @OneToOne(cascade = CascadeType.PERSIST)
  private Imdb imdb;

  private String name;
  private Number size;

  @ElementCollection
  private List<String> tags;

  @Column(name = "release_year")
  private Number year;

  public long getId() {
    return this.id;
  }

  public void setId(final long id) {
    this.id = id;
  }

  public String getAbsPath() {
    return this.absPath;
  }

  public void setAbsPath(final String absPath) {
    this.absPath = absPath;
  }

  public String getDirBasename() {
    return this.dirBasename;
  }

  public void setDirBasename(final String dirBasename) {
    this.dirBasename = dirBasename;
  }

  public String getExt() {
    return this.ext;
  }

  public void setExt(final String ext) {
    this.ext = ext;
  }

  public String getFilename() {
    return this.filename;
  }

  public void setFilename(final String filename) {
    this.filename = filename;
  }

  public String getHumanSize() {
    return this.humanSize;
  }

  public void setHumanSize(final String humanSize) {
    this.humanSize = humanSize;
  }

  public Imdb getImdb() {
    return this.imdb;
  }

  public void setImdb(final Imdb imdb) {
    this.imdb = imdb;
  }

  public String getName() {
    return this.name;
  }

  public void setName(final String name) {
    this.name = name;
  }

  public Number getSize() {
    return this.size;
  }

  public void setSize(final Number size) {
    this.size = size;
  }

  public List<String> getTags() {
    return this.tags;
  }

  public void setTags(final List<String> tags) {
    this.tags = tags;
  }

  public Number getYear() {
    return this.year;
  }

  public void setYear(final Number year) {
    this.year = year;
  }
}
