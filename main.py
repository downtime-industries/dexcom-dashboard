import os
from sys import stdout
import time
import logging
import signal
from pydexcom import Dexcom
from prometheus_client import Gauge, start_http_server
from dotenv import load_dotenv

load_dotenv()

# Configure logging
LOG_DIR = os.getenv("LOG_DIR", "/var/log/dexcom")
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "glucose_monitor.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Get credentials from environment variables
DEXCOM_USERNAME = os.getenv("DEXCOM_USERNAME")
DEXCOM_PASSWORD = os.getenv("DEXCOM_PASSWORD")
PROMETHEUS_PORT = int(os.getenv("PROMETHEUS_PORT", 8000))

if not DEXCOM_USERNAME or not DEXCOM_PASSWORD:
    raise ValueError("Dexcom username and password must be set in environment variables.")
else: 
    logging.debug(f"Dexcom credentials loaded successfully.")

# Initialize Dexcom client
dexcom = Dexcom(username=DEXCOM_USERNAME, password=DEXCOM_PASSWORD)

# Set up Prometheus metrics
glucose_value_gauge = Gauge('glucose_value', 'Current glucose value in mg/dL')
glucose_mmol_gauge = Gauge('glucose_mmol', 'Current glucose value in mmol/L')
trend_direction_gauge = Gauge('trend_direction', 'Current trend direction as numeric value')

# Signal handler to gracefully shutdown
def handle_shutdown(signum, frame):
    logging.info("Received shutdown signal. Exiting.")
    exit(0)

signal.signal(signal.SIGTERM, handle_shutdown)
signal.signal(signal.SIGINT, handle_shutdown)

# Start Prometheus metrics server
start_http_server(PROMETHEUS_PORT)
logging.info(f"Prometheus metrics server started on port {PROMETHEUS_PORT}")

try:
    while True:
        # Fetch the current glucose reading
        glucose_reading = dexcom.get_current_glucose_reading()

        logging.debug(f"Glucose reading: {glucose_reading}")

        if glucose_reading:
            # Extract reading detailsd
            value = glucose_reading.value
            mmol_l = glucose_reading.mmol_l
            trend_direction = glucose_reading.trend

            # Update Prometheus metrics
            glucose_value_gauge.set(value)
            glucose_mmol_gauge.set(mmol_l)
            trend_direction_gauge.set(trend_direction)

            logging.debug("Glucose metrics updated successfully.")

        # Wait for 15 seconds before the next reading
        time.sleep(15)

except Exception as e:
    logging.error(f"An error occurred: {e}")
    handle_shutdown(None, None)
