import logging
import os
import json
import azure.functions as func
from azure.storage.blob import BlobServiceClient

def main(events: func.EventHubEvent):
    logging.info("✅ Function triggered with events batch.")

    try:
        connection_string = os.environ["BLOB_CONNECTION_STRING"]
        container_name = "telemetrydata"
        blob_name = "latest.json"

        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(blob_name)

        for event in events:
            try:
                body = event.get_body().decode('utf-8')
                logging.info(f"📩 Received event: {body}")

                # Validate JSON
                data = json.loads(body)

                # Upload to Blob
                blob_client.upload_blob(json.dumps(data), overwrite=True)
                logging.info("✅ Uploaded latest.json to blob storage.")

            except json.JSONDecodeError as jde:
                logging.error(f"❌ Invalid JSON format: {str(jde)}")
            except Exception as inner:
                logging.error(f"❌ Inner processing error: {str(inner)}")

    except Exception as outer:
        logging.error(f"❌ Outer error during blob connection or setup: {str(outer)}")
