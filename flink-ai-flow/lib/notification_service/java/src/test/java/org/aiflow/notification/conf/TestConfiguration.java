package org.aiflow.notification.conf;

import org.junit.Test;

import java.util.Properties;

import static org.junit.Assert.assertEquals;
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
        assertTrue(conf.getBoolean("a", false));
        assertFalse(conf.getBoolean("b", false));
        assertFalse(conf.getBoolean("c", false));
        assertTrue(conf.getBoolean("d", true));
    }

    @Test
    public void testGetInt() {
        Properties props = new Properties();
        props.put("a", "1");
        Configuration conf = new Configuration(props);
        assertEquals(1, conf.getInt("a", 0));
        assertEquals(1, conf.getLong("a", 0));
    }
}
