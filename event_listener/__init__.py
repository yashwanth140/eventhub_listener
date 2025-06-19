import logging
import os
import json
from datetime import datetime
import azure.functions as func
from azure.storage.blob import BlobServiceClient, ContentSettings

def main(event: func.EventHubEvent, outputBlob: func.Out[str]):
    logging.info("Function triggered with a single event.")

    try:
        body = event.get_body().decode("utf-8")
        logging.info("Processing event: %s", body)

        data = json.loads(body)

        # Update latest.json via output binding
        outputBlob.set(json.dumps(data))
        logging.info("✅ latest.json updated via output binding.")

        # Upload timestamped version separately
        connection_string = os.getenv("BLOB_CONNECTION_STRING")
        container_name = os.getenv("BLOB_CONTAINER_NAME", "telemetrydata")

        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)

        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
        blob_name = f"event_{timestamp}.json"

        container_client.upload_blob(
            name=blob_name,
            data=json.dumps(data),
            overwrite=True,
            content_settings=ContentSettings(content_type="application/json")
        )
        logging.info("✅ Uploaded event_%s.json", timestamp)

    except Exception as e:
        logging.error("❌ Function error: %s", str(e))
