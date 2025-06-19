import logging
import os
import json
from datetime import datetime
import azure.functions as func
from azure.storage.blob import BlobServiceClient, ContentSettings

def main(event: func.EventHubEvent):
    logging.info("Function triggered with a single event.")

    try:
        body = event.get_body().decode("utf-8")
        logging.info("Processing event: %s", body)

        data = json.loads(body)

        # Updated env var name to match what's configured
        connection_string = os.getenv("AzureWebJobsBLOB_CONNECTION_STRING")
        container_name = os.getenv("BLOB_CONTAINER_NAME", "telemetrydata")

        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)

        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
        blob_name = f"event_{timestamp}.json"

        # Upload both timestamped and latest blobs
        container_client.upload_blob(
            name=blob_name,
            data=json.dumps(data),
            overwrite=True,
            content_settings=ContentSettings(content_type="application/json")
        )

        container_client.upload_blob(
            name="latest.json",
            data=json.dumps(data),
            overwrite=True,
            content_settings=ContentSettings(content_type="application/json")
        )

        logging.info("Uploaded %s and updated latest.json", blob_name)

    except Exception as e:
        logging.error("Function error: %s", str(e))
