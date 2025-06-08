import logging
import os
import json
from typing import List
import azure.functions as func
from azure.storage.blob import BlobServiceClient

def main(events: List[func.EventHubEvent]):
    logging.warning("🚀 Function initialized.")

    try:
        connection_string = os.environ["BLOB_CONNECTION_STRING"]
        logging.warning("📡 Got blob connection string.")
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
                logging.warning("✅ Blob updated.")
            except Exception as e:
                logging.error(f"❌ Error processing event: {str(e)}")

    except Exception as conn_err:
        logging.error(f"❌ Blob connection error: {str(conn_err)}")
