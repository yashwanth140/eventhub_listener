import logging
import os
import json
from datetime import datetime
import azure.functions as func
from azure.storage.blob import BlobServiceClient, ContentSettings

def main(event: func.EventHubEvent):
    logging.info("Function triggered with a single event.")

    try:
        connection_string = os.getenv("BLOB_CONNECTION_STRING")
        container_name = os.getenv("BLOB_CONTAINER_NAME", "telemetrydata")

        if not connection_string:
            raise ValueError("Missing BLOB_CONNECTION_STRING environment variable.")

        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)

        body = event.get_body().decode("utf-8").strip()
        logging.info("Raw event body: %s", body)

        if not body:
            logging.warning("Empty event body received. Skipping.")
            return

        try:
            data = json.loads(body)
        except json.JSONDecodeError as je:
            logging.error("Invalid JSON received: %s", je)
            return

        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S%f")[:-3]
        blob_name = f"event_{timestamp}.json"

        # Upload event file
        container_client.upload_blob(
            name=blob_name,
            data=json.dumps(data),
            overwrite=True,
            content_settings=ContentSettings(content_type="application/json")
        )

        # Update latest.json for live feed
        container_client.upload_blob(
            name="latest.json",
            data=json.dumps(data),
            overwrite=True,
            content_settings=ContentSettings(content_type="application/json")
        )

        logging.info("Uploaded %s and updated latest.json", blob_name)

    except Exception as e:
        logging.error("Function-level failure: %s", str(e))
