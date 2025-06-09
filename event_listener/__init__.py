import logging
import os
import json
from typing import List
import azure.functions as func
from azure.storage.blob import BlobServiceClient, ResourceExistsError

def main(events: List[func.EventHubEvent]):
    logging.warning("🚀 Function initialized.")

    try:
        # Load connection string and prepare blob client
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
                
                # Optional: parse JSON to validate it's not malformed
                parsed_json = json.loads(body)

                blob_client.upload_blob(json.dumps(parsed_json), overwrite=True)
                logging.warning("✅ Blob updated successfully.")

            except json.JSONDecodeError as je:
                logging.error(f"❌ JSON parsing error: {je}")
            except ResourceExistsError as re:
                logging.error(f"⚠️ Blob already exists and cannot be overwritten: {re}")
            except Exception as e:
                logging.error(f"❌ Error processing event: {e}")

    except Exception as conn_err:
        logging.error(f"❌ Blob connection error: {conn_err}")
