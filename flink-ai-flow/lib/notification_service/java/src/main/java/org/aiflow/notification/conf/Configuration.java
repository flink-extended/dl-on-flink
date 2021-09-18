package org.aiflow.notification.conf;

import org.apache.commons.lang3.StringUtils;

import java.util.Properties;

public class Configuration {

    /**
     * * When set to 'true', the client will ensure that exactly one copy of each message is written
     * in the notification server. Default value: 'false'
     */
    public static final String CLIENT_ENABLE_IDEMPOTENCE_CONFIG_KEY = "enable.idempotence";

    public static final boolean CLIENT_ENABLE_IDEMPOTENCE_CONFIG_DEFAULT_VALUE = false;

    /**
     * The id of notification client. You can assign a client id which is registered before, so that
     * you can recover a disconnected client along with 'initial.sequence.number'. This config would
     * be ignored if CLIENT_ENABLE_IDEMPOTENCE_CONFIG_KEY is false.
     */
    public static final String CLIENT_ID_CONFIG_KEY = "client.id";

    public static final long CLIENT_ID_CONFIG_DEFAULT_VALUE = -1L;

    /**
     * * The initial sequence number of notification client. This config would be ignored if
     * CLIENT_ENABLE_IDEMPOTENCE_CONFIG_KEY is false.
     */
    public static final String CLIENT_INITIAL_SEQUENCE_NUMBER_CONFIG_KEY =
            "initial.sequence.number";

    public static final int CLIENT_INITIAL_SEQUENCE_NUMBER_CONFIG_DEFAULT_VALUE = 0;

    private final Properties properties;

    public Configuration(Properties properties) {
        this.properties = properties;
    }

    public boolean getBoolean(String name, boolean defaultValue) {
        String valueString = getTrimmed(name);
        if (null == valueString || valueString.isEmpty()) {
            return defaultValue;
        }

        if (StringUtils.equalsIgnoreCase("true", valueString)) return true;
        else if (StringUtils.equalsIgnoreCase("false", valueString)) return false;
        else return defaultValue;
    }

    public int getInt(String name, int defaultValue) {
        String valueString = getTrimmed(name);
        if (valueString == null) return defaultValue;
        return Integer.parseInt(valueString);
    }

    public long getLong(String name, long defaultValue) {
        String valueString = getTrimmed(name);
        if (valueString == null) return defaultValue;
        return Long.parseLong(valueString);
    }

    public String getTrimmed(String name) {
        String value = properties.getProperty(name);

        if (null == value) {
            return null;
        } else {
            return value.trim();
        }
    }
}
