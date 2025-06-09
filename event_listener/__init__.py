import logging
import os
import json
import azure.functions as func
from azure.storage.blob import BlobServiceClient, ResourceExistsError

def main(event: func.EventHubEvent):
    try:
        logging.info("✅ Azure Function triggered by Event Hub event.")

        # Decode event data
        event_data = event.get_body().decode('utf-8')
        logging.info(f"📦 Raw Event Data: {event_data}")

        # Parse JSON payload if needed
        try:
            data = json.loads(event_data)
            logging.info(f"🧠 Parsed Event JSON: {data}")
        except json.JSONDecodeError:
            data = {"raw_message": event_data}
            logging.warning("⚠️ Event data is not valid JSON. Storing as raw text.")

        # Get storage connection string from environment
        conn_str = os.environ.get("AzureWebJobsStorage")
        if not conn_str:
            raise ValueError("❌ AzureWebJobsStorage is not set in environment variables.")

        # Connect to blob storage
        blob_service_client = BlobServiceClient.from_connection_string(conn_str)
        container_name = "telemetrydata"  # Change as needed
        blob_name = "latest.json"

        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        blob_client.upload_blob(json.dumps(data), overwrite=True)

        logging.info(f"✅ Successfully wrote event data to blob '{blob_name}' in container '{container_name}'.")

    except Exception as e:
        logging.error(f"❌ Azure Function execution failed: {str(e)}", exc_info=True)
        raise
