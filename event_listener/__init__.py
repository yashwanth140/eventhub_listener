import logging
import azure.functions as func

def main(events: func.EventHubEvent):
    for event in events:
        message = event.get_body().decode("utf-8")
        logging.info("📨 Event received: %s", message)
