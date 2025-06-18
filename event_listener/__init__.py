import logging
import json
import azure.functions as func

def main(event: func.EventHubEvent, outputBlob: func.Out[str]) -> None:
    try:
        message = event.get_body().decode('utf-8')
        logging.info(f"✅ Event received: {message}")
        data = json.loads(message)
        outputBlob.set(json.dumps(data, indent=2))
        logging.info("📤 Data written to Blob Storage.")
    except Exception as e:
        logging.error(f"❌ Error: {e}")
