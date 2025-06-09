import logging
import os
import json
from typing import List
import azure.functions as func

# Debug: Check if azure-storage-blob is importable
try:
    from azure.storage.blob import BlobServiceClient, ResourceExistsError
    logging.warning("✅ Successfully imported BlobServiceClient from azure.storage.blob")
except ImportError as imp_err:
    logging.error(f"❌ ImportError: {imp_err}")
    raise

def main(events: List[func.EventHubEvent]):
    logging.warning("🚀 Azure Function 'event_listener' triggered.")

    try:
        connection_string = os.environ["BLOB_CONNECTION_STRING"]
        logging.warning("🔐 Blob connection string retrieved.")

        container_name = "telemetrydata"
        blob_name = "latest.json"

        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(blob_name)

        for event in events:
            try:
                body = event.get_body().decode('utf-8')
                logging.warning(f"📩 Event received: {body}")
                
                blob_client.upload_blob(body, overwrite=True)
                logging.warning("✅ Uploaded data to Blob Storage.")
            except Exception as e:
                logging.error(f"❌ Failed to process event: {str(e)}")

    except Exception as conn_err:
        logging.error(f"❌ Blob connection/setup failed: {str(conn_err)}")
