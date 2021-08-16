package org.aiflow.notification.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

public class PythonServer {
    private static final Logger logger = LoggerFactory.getLogger(PythonServer.class);
    private Process process;

    public PythonServer() {}

    public void start() throws Exception {
        logger.info("Server started");
        String serverScript = this.getClass().getResource("/notification_server.py").getFile();
        process =
                new ProcessBuilder()
                        .command("python", serverScript)
                        .redirectErrorStream(true)
                        .start();

        new Thread(
                        () -> {
                            InputStreamReader reader =
                                    new InputStreamReader(process.getInputStream());
                            final BufferedReader bufferedReader = new BufferedReader(reader);
                            String line;
                            try {
                                while ((line = bufferedReader.readLine()) != null) {
                                    logger.info(line);
                                }
                            } catch (IOException e) {
                                // ignore
                            }
                        })
                .start();
    }

    public void stop() {
        process.destroyForcibly();
    }
}
