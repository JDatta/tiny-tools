package jd.toys.moviecatalog.jackson.extend;

import java.io.IOException;

import org.codehaus.jackson.map.BeanDescription;
import org.codehaus.jackson.map.BeanProperty;
import org.codehaus.jackson.map.DeserializationConfig;
import org.codehaus.jackson.map.DeserializationContext;
import org.codehaus.jackson.map.JsonMappingException;
import org.codehaus.jackson.map.KeyDeserializer;
import org.codehaus.jackson.map.KeyDeserializers;
import org.codehaus.jackson.type.JavaType;

public class CaseInsensitiveKeyDeserializers
  implements KeyDeserializers {
  public static final CaseInsensitiveKeyDeserializer DESERIALIZER =
    new CaseInsensitiveKeyDeserializer();

  @Override
  public KeyDeserializer findKeyDeserializer(
    final JavaType type, final DeserializationConfig config,
    final BeanDescription beanDesc,
    final BeanProperty property)
    throws JsonMappingException {
    return DESERIALIZER;
  }

  private static class CaseInsensitiveKeyDeserializer
      extends KeyDeserializer {
    @Override
    public Object deserializeKey(
      final String key, final DeserializationContext ctxt)
      throws IOException {
      return key.toLowerCase();
    }
  }
}
