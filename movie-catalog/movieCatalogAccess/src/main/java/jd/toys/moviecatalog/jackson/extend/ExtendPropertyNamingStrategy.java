package jd.toys.moviecatalog.jackson.extend;

import org.codehaus.jackson.map.MapperConfig;
import org.codehaus.jackson.map.PropertyNamingStrategy;
import org.codehaus.jackson.map.introspect.AnnotatedField;
import org.codehaus.jackson.map.introspect.AnnotatedMethod;

public class ExtendPropertyNamingStrategy extends PropertyNamingStrategy {

  @Override
  public String nameForField(
    final MapperConfig config, final AnnotatedField field,
    final String defaultName) {
    return this.convert(defaultName);
  }

  @Override
  public String nameForGetterMethod(
    final MapperConfig config, final AnnotatedMethod method,
    final String defaultName) {
    return this.convert(defaultName);
  }

  @Override
  public String nameForSetterMethod(
    final MapperConfig config, final AnnotatedMethod method,
    final String defaultName) {
    return this.convert(defaultName);
  }

  public String convert(final String defaultName)
  {
    System.out.println(defaultName);
    final char[] arr = defaultName.toCharArray();
    if (arr.length != 0)
    {
      if (Character.isLowerCase(arr[0])) {
        final char upper = Character.toUpperCase(arr[0]);
        arr[0] = upper;
      }
    }
    return new StringBuilder().append(arr).toString();
  }

  public static void main(final String[] args) {
    final ExtendPropertyNamingStrategy x = new ExtendPropertyNamingStrategy();
    System.out.println(x.convert("artist"));
  }
}
