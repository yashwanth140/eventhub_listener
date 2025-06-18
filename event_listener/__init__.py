import logging
import os
import json
from datetime import datetime
from azure.storage.blob import BlobServiceClient, ContentSettings
import azure.functions as func
from typing import List

def main(events: List[func.EventHubEvent]):
    logging.info("⚡ Function triggered with %d events", len(events))

    try:
        connection_string = os.getenv("BLOB_CONNECTION_STRING")
        container_name = os.getenv("BLOB_CONTAINER_NAME", "telemetrydata")

        if not connection_string:
            raise ValueError("❌ Missing BLOB_CONNECTION_STRING")

        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)

        for event in events:
            try:
                body = event.get_body().decode("utf-8")
                logging.info("➡ Event received: %s", body)
                data = json.loads(body)

                timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S%f")[:-3]
                blob_name = f"event_{timestamp}.json"

                # Write to unique blob
                container_client.upload_blob(
                    blob_name,
                    json.dumps(data),
                    overwrite=True,
                    content_settings=ContentSettings(content_type="application/json")
                )

                # Overwrite latest.json
                container_client.upload_blob(
                    "latest.json",
                    json.dumps(data),
                    overwrite=True,
                    content_settings=ContentSettings(content_type="application/json")
                )

            except Exception as inner:
                logging.error("❗ Failed to process event: %s", str(inner))

    except Exception as outer:
        logging.error("❗ Function error: %s", str(outer))
