import logging
import os
import json
from datetime import datetime
import azure.functions as func
from azure.storage.blob import BlobServiceClient, ContentSettings

def main(events: list[func.EventHubEvent]):
    logging.info("Function triggered with a batch of events.")

    try:
        connection_string = os.getenv("BLOB_CONNECTION_STRING")
        container_name = os.getenv("BLOB_CONTAINER_NAME", "telemetrydata")

        if not connection_string:
            raise ValueError("Missing BLOB_CONNECTION_STRING environment variable.")

        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)

        for event in events:
            try:
                body = event.get_body().decode("utf-8")
                logging.info("Processing event: %s", body)

                data = json.loads(body)
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
                logging.error("Error processing individual event: %s", str(e))

    except Exception as e:
        logging.error("Function-level failure: %s", str(e))
