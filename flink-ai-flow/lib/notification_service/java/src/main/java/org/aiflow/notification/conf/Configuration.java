package org.aiflow.notification.conf;

import java.util.Properties;

public class Configuration {

    /**
     * * When set to 'true', the client will ensure that exactly one copy of each message is written
     * in the notification server. Default value: 'false'
     */
    public static final String CLIENT_ENABLE_IDEMPOTENCE_CONFIG_KEY = "enable.idempotence";

    private final Properties properties;

    public Configuration(Properties properties) {
        this.properties = properties;
    }

    public boolean getBoolean(String key) {
        return Boolean.parseBoolean(properties.getProperty(key));
    }
}
