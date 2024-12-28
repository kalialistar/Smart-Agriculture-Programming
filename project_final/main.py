# thonny 코드(이티보드 및 시스템 동작 코드)

from machine import Pin, I2C
from time import sleep
import dht
from ssd1306 import SSD1306_I2C

# I2C 설정
i2c = I2C(1, scl=Pin(22), sda=Pin(21))  # I2C 버스 1 사용
oled = SSD1306_I2C(128, 64, i2c)       # 128x64 해상도 OLED 초기화

# 센서 핀 설정
right_sensor = dht.DHT11(Pin(16))      # D5 (GPIO 16, 우측면)
left_sensor = dht.DHT11(Pin(15))       # D6 (GPIO 15, 좌측면)
center_sensor = dht.DHT11(Pin(13))     # D7 (GPIO 13, 중앙부)
heatbox_sensor = dht.DHT11(Pin(12))    # D4 (GPIO 12, 히트박스)
outside_sensor = dht.DHT11(Pin(27))    # D2 (GPIO 27, 외부 온습도)

# 릴레이 핀 설정 (히터 릴레이는 제거됨)
left_fan_relay = Pin(17, Pin.OUT)      # D8 (GPIO 17, 좌측면 팬 릴레이)
right_fan_relay = Pin(4, Pin.OUT)      # D9 (GPIO 4, 우측면 팬 릴레이)

# 설정 온도 및 상태 변수
target_temperature = 18               # 목표 온도
temperature_difference = 2            # 온도 차이 허용치
fan_on = False                        # 팬 작동 상태
fans_initial = True                   # 초기 팬 상태 여부

# 팬 제어 함수
def control_fans(state):
    """
    팬을 ON 또는 OFF 상태로 제어하는 함수.
    두 팬을 동시에 제어하여 항상 동기화되도록 합니다.
    """
    left_fan_relay.value(1 if state else 0)
    right_fan_relay.value(1 if state else 0)
    fan_state = "ON" if state else "OFF"
    print(f"팬 상태: {fan_state}")
    if state:
        print("팬 작동 중: 릴레이가 ON 상태입니다.")
    else:
        print("팬 작동 멈춤: 릴레이가 OFF 상태입니다.")

# 온도 읽기 함수
def read_temperature(sensor):
    """
    DHT11 센서에서 온도와 습도를 읽는 함수.
    읽기에 실패할 경우 None을 반환합니다.
    """
    try:
        sensor.measure()
        return sensor.temperature(), sensor.humidity()
    except Exception as e:
        print("센서 읽기 오류:", e)
        return None, None

# 초기 팬 켜기 (무조건 작동)
control_fans(True)
fan_on = True
print("초기 상태: 팬 ON")

while True:
    # 센서 데이터 읽기
    center_temp, center_hum = read_temperature(center_sensor)
    left_temp, left_hum = read_temperature(left_sensor)
    right_temp, right_hum = read_temperature(right_sensor)
    heatbox_temp, heatbox_hum = read_temperature(heatbox_sensor)
    outside_temp, outside_hum = read_temperature(outside_sensor)

    # 팬 상태 디버깅
    print(f"팬 릴레이 상태: Left Fan={left_fan_relay.value()}, Right Fan={right_fan_relay.value()}")

    # 데이터 출력 (디버깅용)
    print(f"중앙부 온도: {center_temp}°C, 습도: {center_hum}%")
    print(f"좌측면 온도: {left_temp}°C, 습도: {left_hum}%")
    print(f"우측면 온도: {right_temp}°C, 습도: {right_hum}%")
    print(f"히트박스 온도: {heatbox_temp}°C, 습도: {heatbox_hum}%")
    print(f"외부 온도: {outside_temp}°C, 습도: {outside_hum}%")

    # OLED 화면에 데이터 출력
    oled.fill(0)  # 화면 초기화
    oled.text("Center:", 0, 0)
    if center_temp is not None and center_hum is not None:
        oled.text(f"T:{center_temp}C H:{center_hum}%", 0, 10)
    else:
        oled.text("Error", 0, 10)

    oled.text("Left:", 0, 30)
    if left_temp is not None and left_hum is not None:
        oled.text(f"T:{left_temp}C H:{left_hum}%", 0, 40)
    else:
        oled.text("Error", 0, 40)

    oled.text("Right:", 0, 50)
    if right_temp is not None and right_hum is not None:
        oled.text(f"T:{right_temp}C H:{right_hum}%", 0, 60)
    else:
        oled.text("Error", 0, 60)

    oled.show()  # OLED 화면 갱신

    # 팬 제어 로직
    if center_temp is not None and left_temp is not None and right_temp is not None:
        if fans_initial:
            # 초기 상태: 팬이 항상 작동 중
            if center_temp >= target_temperature:
                control_fans(False)  # 팬 OFF
                fan_on = False
                fans_initial = False
                print("설정 온도에 도달. 팬 OFF")
        else:
            # 팬 작동 조건: 중앙부 온도가 좌측면과 우측면 평균보다 2도 이상 높을 때
            average_side_temp = (left_temp + right_temp) / 2
            temp_diff = center_temp - average_side_temp
            print(f"평균 측면 온도: {average_side_temp}°C, 중앙부와 평균 온도 차이: {temp_diff}°C")
            if temp_diff > temperature_difference:
                if not fan_on:
                    control_fans(True)  # 팬 ON
                    fan_on = True
                    print("온도 차이 발생: 팬 ON")
            else:
                if fan_on:
                    control_fans(False)  # 팬 OFF
                    fan_on = False
                    print("온도 차이 해소: 팬 OFF")

    # 1초 대기 후 반복
    sleep(10)
