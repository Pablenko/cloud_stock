from admin.configuration import load_configuration
from fastapi import FastAPI

SERVICE_DISCOVERY_PORT = 7432

app = FastAPI()
config = load_configuration()
current_service_taken = 0


def get_service_name():
    global current_service_taken
    config_length = len(config["stock"]["papers"])
    if current_service_taken >= config_length:
        return {"SERVICE_NAME": "UNKNOWN"}
    else:
        paper_name = config["stock"]["papers"][current_service_taken]
        current_service_taken += 1
        return {"SERVICE_NAME": paper_name}


@app.get("/request_service")
def handle_market_order():
    return get_service_name()
