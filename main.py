import os
import time
import logging
import signal
import psycopg2
from pydexcom import Dexcom

# Configure logging
LOG_DIR = os.getenv("LOG_DIR", "/var/log/dexcom")
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "glucose_monitor.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Get credentials and database connection details from environment variables
DEXCOM_USERNAME = os.getenv("DEXCOM_USERNAME")
DEXCOM_PASSWORD = os.getenv("DEXCOM_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "glucose_data")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

if not DEXCOM_USERNAME or not DEXCOM_PASSWORD:
    raise ValueError("Dexcom username and password must be set in environment variables.")

# Initialize Dexcom client
dexcom = Dexcom(username=DEXCOM_USERNAME, password=DEXCOM_PASSWORD)

# Establish PostgreSQL connection
connection = psycopg2.connect(
    host=POSTGRES_HOST,
    port=POSTGRES_PORT,
    database=POSTGRES_DB,
    user=POSTGRES_USER,
    password=POSTGRES_PASSWORD
)
connection.autocommit = True
cursor = connection.cursor()

# Create a table if it does not exist
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS glucose_readings (
        id SERIAL PRIMARY KEY,
        value INTEGER NOT NULL,
        mmol_l FLOAT NOT NULL,
        trend_direction VARCHAR(50) NOT NULL,
        trend_arrow VARCHAR(5) NOT NULL,
        timestamp TIMESTAMP NOT NULL
    )
    """
)

# Signal handler to gracefully shutdown
def handle_shutdown(signum, frame):
    logging.info("Received shutdown signal. Closing database connection.")
    cursor.close()
    connection.close()
    exit(0)

signal.signal(signal.SIGTERM, handle_shutdown)
signal.signal(signal.SIGINT, handle_shutdown)

try:
    while True:
        # Fetch the current glucose reading
        glucose_reading = dexcom.get_current_glucose_reading()
        
        if glucose_reading:
            # Extract reading details
            value = glucose_reading.value
            mmol_l = glucose_reading.mmol_l
            trend_direction = glucose_reading.trend_direction
            trend_arrow = glucose_reading.trend_arrow
            timestamp = glucose_reading.datetime

            # Insert data into the PostgreSQL table
            cursor.execute(
                """
                INSERT INTO glucose_readings (value, mmol_l, trend_direction, trend_arrow, timestamp)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (value, mmol_l, trend_direction, trend_arrow, timestamp)
            )

            logging.info("Glucose reading processed successfully.")

        # Wait for 15 seconds before the next reading
        time.sleep(15)

except Exception as e:
    logging.error(f"An error occurred: {e}")
    handle_shutdown(None, None)

