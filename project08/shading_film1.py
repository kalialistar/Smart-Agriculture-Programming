import requests
import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd

# API 호출 함수
def fetch_weather_data():
    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": 35.822,
        "lon": 127.149,
        "appid": "c20b80b57a1b2c567c850a1c0bcb1db2",  # 실제 API 키
        "units": "metric"
    }
    response = requests.get(url, params=params)
    data = response.json()
    return {
        "time": datetime.now().replace(minute=0, second=0, microsecond=0),  # 정각 기준 시간
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "wind_speed": data["wind"]["speed"],
        "cloudiness": data["clouds"]["all"]
    }

# 데이터 저장용 리스트 (최대 8개의 정각 데이터만 유지)
weather_data = []

# Streamlit 인터페이스 설정
st.title("실시간 날씨 데이터 모니터링")
st.write("현재 시각에서 2개의 데이터만 수집하여 그래프를 그려봅니다.")

# 그래프 생성
def update_weather_data():
    global weather_data
    new_data = fetch_weather_data()
    weather_data.append(new_data)

    if len(weather_data) > 8:
        weather_data.pop(0)

    # 데이터프레임으로 변환
    df = pd.DataFrame(weather_data)

    # 그래프 생성
    fig, axs = plt.subplots(2, 2, figsize=(12, 8))

    # 온도 그래프
    axs[0, 0].plot(df["time"], df["temperature"], '-o', color="red", label="온도 (°C)")
    axs[0, 0].set_title("온도")
    axs[0, 0].set_xlabel("시간")
    axs[0, 0].set_ylabel("°C")
    axs[0, 0].legend()

    # 습도 그래프
    axs[0, 1].plot(df["time"], df["humidity"], '-o', color="blue", label="습도 (%)")
    axs[0, 1].set_title("습도")
    axs[0, 1].set_xlabel("시간")
    axs[0, 1].set_ylabel("%")
    axs[0, 1].legend()

    # 풍속 그래프
    axs[1, 0].plot(df["time"], df["wind_speed"], '-o', color="green", label="풍속 (m/s)")
    axs[1, 0].set_title("풍속")
    axs[1, 0].set_xlabel("시간")
    axs[1, 0].set_ylabel("m/s")
    axs[1, 0].legend()

    # 구름량 그래프
    axs[1, 1].plot(df["time"], df["cloudiness"], '-o', color="gray", label="구름량 (%)")
    axs[1, 1].set_title("구름량")
    axs[1, 1].set_xlabel("시간")
    axs[1, 1].set_ylabel("%")
    axs[1, 1].legend()

    plt.tight_layout()
    plt.savefig("project08/graphs.png")  # 그래프를 파일로 저장
    st.pyplot(fig)
    
# Streamlit에서 버튼을 클릭하여 업데이트 테스트
if st.button("날씨 데이터 업데이트"):
    update_weather_data()
