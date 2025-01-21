# Dexcom Dashboard

This project creates a simple tracking service for monitoring a Dexcom device via their API. To start it you will need to copy the `sample.env` to a file called `.env`. Put in your Dexcom login credentials and run `docker compose up`!

This will start 3 services. 

1. Dexcom-Monitor - A container that runs the the main.py file that reads glucose levels every 5 minutes
2. Promethius - Service that collects the glucose measurments from Dexcom-Monitor and stores them
3. Grafana - Visualization for the data with thresholds