package org.aiflow.notification.conf;

import org.junit.Test;

import java.util.Properties;

import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

public class TestConfiguration {
    @Test
    public void testGetBoolean() {
        Properties props = new Properties();
        props.put("a", "true");
        props.put("b", "FALse");
        props.put("c", "123");
        Configuration conf = new Configuration(props);
        assertTrue(conf.getBoolean("a"));
        assertFalse(conf.getBoolean("b"));
        assertFalse(conf.getBoolean("c"));
        assertFalse(conf.getBoolean("d"));
    }
}
