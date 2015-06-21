package jd.toys.moviecatalog.jpa.entities;

import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.GeneratedValue;
import javax.persistence.GenerationType;
import javax.persistence.Id;
import javax.persistence.Table;

@Entity
@Table(name = "simpleMovie")
public class SimpleMovie {

  @Id
  @GeneratedValue(strategy = GenerationType.AUTO)
  private long id;

  @Column(name = "release_year")
  private int year;

  @Column(length = 1024)
  private String path;
  private String name;

  public long getId() {
    return this.id;
  }

  public void setId(final long id) {
    this.id = id;
  }

  public String getPath() {
    return this.path;
  }

  public void setPath(final String path) {
    this.path = path;
  }

  public String getName() {
    return this.name;
  }

  public void setName(final String name) {
    this.name = name;
  }

  public void setYear(final int year) {
    this.year = year;
  }

  public int getYear() {
    return this.year;
  }
}
