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
        
        if not body.strip():
            logging.warning("Empty event body received. Skipping.")
            return

        logging.info("Processing event: %s", body)
        data = json.loads(body)

        # Fetch storage connection and container name from environment
        connection_string = os.getenv("AzureWebJobsBLOB_CONNECTION_STRING")
        container_name = os.getenv("BLOB_CONTAINER_NAME", "telemetrydata")

        # Connect to blob storage
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)

        # Generate timestamped filename
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
        blob_name = f"event_{timestamp}.json"

        # Upload latest.json and timestamped file
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
