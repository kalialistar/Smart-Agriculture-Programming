# main.py를 통해 이티보드에서 라즈베리파이로 센서 데이터 값을 불러오는 코드

import serial
import time
import logging
from threading import Thread, Event, Lock
from collections import deque

# 로깅 설정
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# 시리얼 포트 설정
SERIAL_PORT = '/dev/ttyUSB1'  # 환경에 맞게 수정
BAUD_RATE = 115200
TIMEOUT = 1

# 팬 상태 및 목표 온도
TARGET_TEMPERATURE = 18
TEMPERATURE_DIFFERENCE = 2
fan_on = False

# 데이터 저장
data_lock = Lock()
sensor_data = {
    "중앙부": {"temperature": None, "humidity": None},
    "좌측면": {"temperature": None, "humidity": None},
    "우측면": {"temperature": None, "humidity": None},
    "히트박스": {"temperature": None, "humidity": None},
    "외부": {"temperature": None, "humidity": None},
    "fan_state": "ON"
}

# 그래프 데이터 저장
MAX_GRAPH_LENGTH = 60
graph_data = {
    "중앙부 온도": deque([0] * MAX_GRAPH_LENGTH, maxlen=MAX_GRAPH_LENGTH),
    "중앙부 습도": deque([0] * MAX_GRAPH_LENGTH, maxlen=MAX_GRAPH_LENGTH),
    "좌측면 온도": deque([0] * MAX_GRAPH_LENGTH, maxlen=MAX_GRAPH_LENGTH),
    "좌측면 습도": deque([0] * MAX_GRAPH_LENGTH, maxlen=MAX_GRAPH_LENGTH),
    "우측면 온도": deque([0] * MAX_GRAPH_LENGTH, maxlen=MAX_GRAPH_LENGTH),
    "우측면 습도": deque([0] * MAX_GRAPH_LENGTH, maxlen=MAX_GRAPH_LENGTH),
    "히트박스 온도": deque([0] * MAX_GRAPH_LENGTH, maxlen=MAX_GRAPH_LENGTH),
    "히트박스 습도": deque([0] * MAX_GRAPH_LENGTH, maxlen=MAX_GRAPH_LENGTH),
    "외부 온도": deque([0] * MAX_GRAPH_LENGTH, maxlen=MAX_GRAPH_LENGTH),
    "외부 습도": deque([0] * MAX_GRAPH_LENGTH, maxlen=MAX_GRAPH_LENGTH),
}


# 데이터 처리 함수
def process_sensor_data(data):
    try:
        if "온도:" in data and "습도:" in data:
            parts = data.split(", ")
            if len(parts) == 2:
                sensor_info, temp_part = parts[0].split(" 온도:")
                hum_part = parts[1].split("습도:")[1]
                sensor_name = sensor_info.strip()

                # 온도/습도 값 변환
                temperature = float(temp_part.replace("°C", "").strip())
                humidity = float(hum_part.replace("%", "").strip())

                with data_lock:
                    if sensor_name in sensor_data:
                        sensor_data[sensor_name]["temperature"] = temperature
                        sensor_data[sensor_name]["humidity"] = humidity
                        graph_data[f"{sensor_name} 온도"].append(temperature)
                        graph_data[f"{sensor_name} 습도"].append(humidity)

                # 팬 상태 제어
                if sensor_name == "중앙부":
                    global fan_on
                    if temperature >= TARGET_TEMPERATURE + TEMPERATURE_DIFFERENCE:
                        if not fan_on:
                            sensor_data["fan_state"] = "ON"
                            fan_on = True
                    elif temperature <= TARGET_TEMPERATURE:
                        if fan_on:
                            sensor_data["fan_state"] = "OFF"
                            fan_on = False

    except Exception as e:
        logging.error(f"데이터 처리 중 오류 발생: {e}")


# 시리얼 데이터 수신 스레드
def read_serial(stop_event):
    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=TIMEOUT) as ser:
            while not stop_event.is_set():
                line = ser.readline().decode('utf-8').strip()
                if line:
                    process_sensor_data(line)
                time.sleep(1)  # 1초마다 데이터 읽기
    except Exception as e:
        logging.error(f"시리얼 포트 오류 발생: {e}")


# 스레드 시작
def start_sensor_thread():
    stop_event = Event()
    thread = Thread(target=read_serial, args=(stop_event,), daemon=True)
    thread.start()
    return stop_event


if __name__ == "__main__":
    stop_event = start_sensor_thread()
    try:
        while True:
            with data_lock:
                # 주기적으로 센서 데이터 출력
                logging.info("현재 센서 데이터: %s", sensor_data)
            time.sleep(5)  # 10초마다 출력
    except KeyboardInterrupt:
        logging.info("프로그램 종료")
        stop_event.set()
