import logging
import os
import json
from datetime import datetime
import azure.functions as func
from azure.storage.blob import BlobServiceClient

def main(events: func.EventHubEvent):
    logging.info("Function triggered with events batch.")

    try:
        connection_string = os.environ["BLOB_CONNECTION_STRING"]
        container_name = "telemetrydata"

        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)

        for event in events:
            try:
                body = event.get_body().decode('utf-8')
                logging.info(f" Received event: {body}")

                data = json.loads(body)

                # Write individual file
                timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S%f")[:-3]
                blob_name = f"event_{timestamp}.json"
                blob_client = container_client.get_blob_client(blob_name)
                blob_client.upload_blob(json.dumps(data), overwrite=True)

                # Optional: also update latest.json
                latest_blob = container_client.get_blob_client("latest.json")
                latest_blob.upload_blob(json.dumps(data), overwrite=True)

                logging.info(f" Uploaded {blob_name} and updated latest.json")

            except json.JSONDecodeError as jde:
                logging.error(f" JSON decode error on: {body} → {str(jde)}")
            except Exception as inner:
                logging.error(f" Inner error: {str(inner)}")

    except Exception as outer:
        logging.error(f" Blob connection/setup error: {str(outer)}")
