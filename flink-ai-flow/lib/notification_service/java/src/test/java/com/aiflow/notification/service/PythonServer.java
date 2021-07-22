package com.aiflow.notification.service;

import java.util.logging.Logger;

public class PythonServer {
    private static final Logger logger = Logger.getLogger(PythonServer.class.getName());
    private Process process;

    public PythonServer(){
    }

    public void start() throws Exception {
        logger.info("Server started");
        String serverScript = this.getClass().getResource("/notification_server.py").getFile();
        process = Runtime.getRuntime().exec(String.format("python %s", serverScript));
    }

    public void stop() {
        process.destroyForcibly();
    }
}
