/*
 * Copyright 2022 Deep Learning on Flink Authors
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package org.flinkextended.flink.ml.util;

import com.google.common.annotations.VisibleForTesting;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.net.Inet4Address;
import java.net.Inet6Address;
import java.net.InetAddress;
import java.net.NetworkInterface;
import java.net.ServerSocket;
import java.util.Enumeration;
import java.util.Random;

/** machine ip address and port helper function. */
public class IpHostUtil {
    public static final String TF_ON_FLINK_IP = "TF_ON_FLINK_IP";
    private static final Logger LOG = LoggerFactory.getLogger(IpHostUtil.class);

    @VisibleForTesting
    static InetAddress getLocalHostLANAddress() throws Exception {
        try {
            InetAddress candidateIpv4 = null;
            InetAddress candidateIpv6 = null;
            for (Enumeration ifaces = NetworkInterface.getNetworkInterfaces();
                    ifaces.hasMoreElements(); ) {
                NetworkInterface iface = (NetworkInterface) ifaces.nextElement();
                for (Enumeration inetAddrs = iface.getInetAddresses();
                        inetAddrs.hasMoreElements(); ) {
                    InetAddress inetAddr = (InetAddress) inetAddrs.nextElement();
                    if (!inetAddr.isLoopbackAddress()) {
                        if (inetAddr.isSiteLocalAddress()) {
                            return inetAddr;
                        }
                        if (inetAddr instanceof Inet4Address && candidateIpv4 == null) {
                            // ip v4
                            candidateIpv4 = inetAddr;
                        } else if (inetAddr instanceof Inet6Address && candidateIpv6 == null) {
                            // ip v6
                            candidateIpv6 = inetAddr;
                        }
                    }
                }
            }
            if (candidateIpv4 != null) {
                return candidateIpv4;
            }
            if (candidateIpv6 != null) {
                return candidateIpv6;
            }
        } catch (Exception e) {
            LOG.error("Fail to get local ip. ", e);
        }

        try {
            InetAddress jdkSuppliedAddress = InetAddress.getLocalHost();
            return jdkSuppliedAddress;
        } catch (Exception e) {
            LOG.error("Fail to get local ip from jdk. ", e);
        }
        return null;
    }

    private static String getLocalIp() throws Exception {
        String localIp = System.getenv(TF_ON_FLINK_IP);
        if (localIp != null) {
            LOG.info("Got local ip from environment variable {} {}", TF_ON_FLINK_IP, localIp);
            return localIp;
        }
        InetAddress address = InetAddress.getLocalHost();
        localIp = address.getHostAddress();
        LOG.info("Got local Hostname: {}, local ip: {}", address.getHostName(), localIp);
        return localIp;
    }

    /**
     * @return local ip address.
     * @throws Exception
     */
    public static String getIpAddress() throws Exception {
        try {
            return getLocalIp();
        } catch (Exception e) {
            InetAddress inetAddress = getLocalHostLANAddress();
            if (null == inetAddress) {
                return null;
            } else {
                return inetAddress.getHostAddress();
            }
        }
    }

    /** @return Gets a free port and create a ServerSocket bound to this port. */
    public static ServerSocket getFreeSocket() {
        final int minPort = 20000;
        final int maxPort = 65535;
        Random rand = new Random();
        int i = 0;
        while (true) {
            try {
                i = rand.nextInt(maxPort - minPort) + minPort;
                return new ServerSocket(i);
            } catch (Exception e) {
                System.out.println("port:" + i + " in use");
            }
        }
    }

    /**
     * @return a free port.
     * @throws IOException
     */
    public static int getFreePort() throws IOException {
        try (ServerSocket socket = getFreeSocket()) {
            return socket.getLocalPort();
        }
    }
}
