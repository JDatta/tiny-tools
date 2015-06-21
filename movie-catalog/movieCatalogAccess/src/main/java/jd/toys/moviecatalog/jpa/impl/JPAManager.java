package jd.toys.moviecatalog.jpa.impl;

import java.util.List;

import javax.persistence.EntityManager;
import javax.persistence.EntityManagerFactory;
import javax.persistence.Persistence;
import javax.persistence.TypedQuery;
import javax.persistence.criteria.CriteriaBuilder;
import javax.persistence.criteria.CriteriaQuery;
import javax.persistence.criteria.Root;

import jd.toys.moviecatalog.MovieManager;
import jd.toys.moviecatalog.jpa.entities.Movie;

public class JPAManager implements MovieManager {

  private static final String PERSISTENCE_UNIT_NAME = "movies";
  private final EntityManagerFactory factory;
  private final EntityManager em;

  public JPAManager() {
    this.factory = Persistence.createEntityManagerFactory(PERSISTENCE_UNIT_NAME);
    this.factory.createEntityManager();
    this.em = this.factory.createEntityManager();
  }

  @Override
  public void close() {
    if (this.em != null) {
      this.em.close();
    }
    if (this.factory != null) {
      this.factory.close();
    }
  }

  @Override
  public void save(final List<Movie> movies) {

    for (final Movie m : movies) {
      this.em.getTransaction().begin();
      this.em.persist(m);
      this.em.getTransaction().commit();
    }
  }

  @Override
  public List<Movie> list() {
    final CriteriaBuilder cb = this.em.getCriteriaBuilder();
    final CriteriaQuery<Movie> cq = cb.createQuery(Movie.class);
    final Root<Movie> rootEntry = cq.from(Movie.class);
    final CriteriaQuery<Movie> all = cq.select(rootEntry);
    final TypedQuery<Movie> allQuery = this.em.createQuery(all);
    return allQuery.getResultList();
  }
}
