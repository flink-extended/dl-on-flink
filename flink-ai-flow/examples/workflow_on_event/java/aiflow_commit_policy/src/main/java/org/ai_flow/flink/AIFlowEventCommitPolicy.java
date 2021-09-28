package org.ai_flow.flink;

import com.google.gson.Gson;
import org.aiflow.notification.client.NotificationClient;
import org.apache.flink.table.filesystem.PartitionCommitPolicy;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class AIFlowEventCommitPolicy implements PartitionCommitPolicy {

	private static final Logger LOG = LoggerFactory.getLogger(AIFlowEventCommitPolicy.class);
	private static final Gson GSON = new Gson();

	private NotificationClient notificationClient = null;

	@Override
	public void commit(Context context) throws Exception {
		LOG.info("Committed partition {} to AIFlow Notification.", context.partitionSpec());

		try {
			if (notificationClient == null) {
				notificationClient = new NotificationClient("localhost:50051",
						"workflow_on_event", "", false,
						0, 0, 0);
			}
			LOG.info("Prepare to send event {} to notification service.", GSON.toJson(context));
			notificationClient.sendEvent("hourly_data", "ready", "DATA_EVENT", GSON.toJson(context));
			LOG.info("Finish to send event to notification service ");
		} catch (Exception e) {
			LOG.error("Failed to send event", e);
		}

	}
}
