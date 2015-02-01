package jd.toys.moviecatalog.hibernate;

import java.util.List;

import jd.toys.moviecatalog.hibernate.entities.Movie;

import org.hibernate.HibernateException;
import org.hibernate.Session;
import org.hibernate.SessionFactory;
import org.hibernate.Transaction;
import org.hibernate.boot.registry.StandardServiceRegistryBuilder;
import org.hibernate.cfg.Configuration;
import org.hibernate.service.ServiceRegistry;

public class MovieManager implements AutoCloseable {

  private final SessionFactory sessionFactory;

  public MovieManager() {
    this.sessionFactory = createSessionFactory();
  }

  private static SessionFactory createSessionFactory() {
    final Configuration configuration = new Configuration();
    configuration.configure();
    final ServiceRegistry serviceRegistry =
      new StandardServiceRegistryBuilder()
        .applySettings(configuration.getProperties()).build();
    final SessionFactory sessionFactory =
      configuration.buildSessionFactory(serviceRegistry);
    return sessionFactory;
  }

  public void save(final List<Movie> movies) {

    Session session = null;
    Transaction t = null;
    try {
      session = this.sessionFactory.openSession();
      t = session.beginTransaction();

      for (final Movie m : movies) {
        session.persist(m);
      }

      t.commit();
    } catch (final HibernateException e) {
      if (t != null) {
        t.rollback();
      }
      throw e;
    } finally {
      if (session != null) {
        session.close();
      }
    }
    System.out.println("successfully saved");
  }

  @SuppressWarnings("unchecked")
  public List<Movie> list() {
    Session session = null;
    Transaction tx = null;
    try {
      session = this.sessionFactory.openSession();
      tx = session.beginTransaction();
      final List<Movie> movies = session
        .createCriteria(Movie.class)
        .list();
      tx.commit();
      return movies;
    } catch (final HibernateException e) {
      if (tx != null) {
        tx.rollback();
      }
      throw e;
    } finally {
      if (session != null) {
        session.close();
      }
    }
  }

  @Override
  public void close() throws Exception {
    this.sessionFactory.close();
  }
}
