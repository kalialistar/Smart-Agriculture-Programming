import serial
import time
import logging
from threading import Thread, Event, Lock
from collections import deque

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Serial port setup
SERIAL_PORT = "/dev/ttyUSB0"  # Adjust according to your environment
BAUD_RATE = 115200
TIMEOUT = 1

# Data storage
data_lock = Lock()
sensor_data = {
    "Center": {"temperature": None, "humidity": None},
    "Left": {"temperature": None, "humidity": None},
    "Right": {"temperature": None, "humidity": None},
    "Heatbox": {"temperature": None, "humidity": None},
    "External": {"temperature": None, "humidity": None},
    "fan_state": "ON",
}

# Graph data storage
MAX_GRAPH_LENGTH = 60
graph_data = {
    "Center Temperature": deque([0] * MAX_GRAPH_LENGTH, maxlen=MAX_GRAPH_LENGTH),
    "Center Humidity": deque([0] * MAX_GRAPH_LENGTH, maxlen=MAX_GRAPH_LENGTH),
    "Left Temperature": deque([0] * MAX_GRAPH_LENGTH, maxlen=MAX_GRAPH_LENGTH),
    "Left Humidity": deque([0] * MAX_GRAPH_LENGTH, maxlen=MAX_GRAPH_LENGTH),
    "Right Temperature": deque([0] * MAX_GRAPH_LENGTH, maxlen=MAX_GRAPH_LENGTH),
    "Right Humidity": deque([0] * MAX_GRAPH_LENGTH, maxlen=MAX_GRAPH_LENGTH),
    "Heatbox Temperature": deque([0] * MAX_GRAPH_LENGTH, maxlen=MAX_GRAPH_LENGTH),
    "Heatbox Humidity": deque([0] * MAX_GRAPH_LENGTH, maxlen=MAX_GRAPH_LENGTH),
    "External Temperature": deque([0] * MAX_GRAPH_LENGTH, maxlen=MAX_GRAPH_LENGTH),
    "External Humidity": deque([0] * MAX_GRAPH_LENGTH, maxlen=MAX_GRAPH_LENGTH),
}

# Process sensor data
def process_sensor_data(data):
    try:
        # Parse data in the format "센서명 온도: XX°C, 습도: XX%"
        if "온도:" in data and "습도:" in data:
            parts = data.split(", ")
            if len(parts) == 2:
                sensor_info, temp_part = parts[0].split(" 온도:")
                hum_part = parts[1].split("습도:")[1]
                sensor_name = sensor_info.strip()

                # Map 한글 센서 이름 to English
                sensor_mapping = {
                    "중앙부": "Center",
                    "좌측면": "Left",
                    "우측면": "Right",
                    "히트박스": "Heatbox",
                    "외부": "External",
                }
                english_sensor_name = sensor_mapping.get(sensor_name)

                if not english_sensor_name:
                    logging.warning(f"Unknown sensor name: {sensor_name}")
                    return

                # Convert temperature and humidity values
                temperature = float(temp_part.replace("°C", "").strip())
                humidity = float(hum_part.replace("%", "").strip())

                with data_lock:
                    if english_sensor_name in sensor_data:
                        # Update sensor data
                        sensor_data[english_sensor_name]["temperature"] = temperature
                        sensor_data[english_sensor_name]["humidity"] = humidity
                        # Update graph data
                        graph_data[f"{english_sensor_name} Temperature"].append(temperature)
                        graph_data[f"{english_sensor_name} Humidity"].append(humidity)

                logging.info(f"Updated {english_sensor_name}: Temp={temperature}°C, Hum={humidity}%")

    except Exception as e:
        logging.error(f"Error processing data: {e}, Raw data: {data}")


# Serial data reading thread
def read_serial(stop_event):
    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=TIMEOUT) as ser:
            while not stop_event.is_set():
                line = ser.readline().decode("utf-8").strip()
                if line:
                    logging.info(f"Raw data received: {line}")
                    process_sensor_data(line)
                time.sleep(1)  # Read data every second
    except Exception as e:
        logging.error(f"Serial port error: {e}")


# Start the sensor thread
def start_sensor_thread():
    stop_event = Event()
    thread = Thread(target=read_serial, args=(stop_event,), daemon=True)
    thread.start()
    return stop_event


# Pretty print sensor data
def log_sensor_data():
    with data_lock:
        header = f"{'Sensor':<10} {'Temperature (°C)':<20} {'Humidity (%)':<15}"
        logging.info("\n" + "=" * 50)
        logging.info(header)
        logging.info("-" * 50)
        for sensor, values in sensor_data.items():
            if sensor == "fan_state":
                continue
            temp = values["temperature"] if values["temperature"] is not None else "N/A"
            hum = values["humidity"] if values["humidity"] is not None else "N/A"
            logging.info(f"{sensor:<10} {temp:<20} {hum:<15}")
        logging.info("=" * 50)
        # Log fan state
        fan_state = sensor_data.get("fan_state", "N/A")
        logging.info(f"Fan State: {fan_state}")


if __name__ == "__main__":
    stop_event = start_sensor_thread()
    try:
        while True:
            log_sensor_data()
            time.sleep(3)  # Log every 3 seconds
    except KeyboardInterrupt:
        logging.info("Program terminated")
        stop_event.set()
