import time
import streamlit as st
import matplotlib.pyplot as plt
from main_code_eng import sensor_data, graph_data, start_sensor_thread, data_lock

# Streamlit 설정
st.set_page_config(page_title="Greenhouse Dashboard", layout="wide")

# 제목을 가운데 정렬
st.markdown("<h1 style='text-align: center;'>Greenhouse Temperature Control System</h1>", unsafe_allow_html=True)

# 센서 데이터 그래프
st.markdown("<h2 style='text-align: center;'>Real-Time Temperature Graph</h2>", unsafe_allow_html=True)
central_chart = st.empty()

# 센서 테이블
st.markdown("<h3 style='text-align: center;'>Real-Time Sensor Data</h3>", unsafe_allow_html=True)
sensor_table = st.empty()

# 팬 상태 표시
st.markdown("<h3 style='text-align: center;'>Fan State</h3>", unsafe_allow_html=True)
fan_state_display = st.empty()

# 센서 스레드 시작: Streamlit에서 한 번만 실행되도록 보장
@st.cache_resource
def initialize_sensor_thread():
    return start_sensor_thread()

initialize_sensor_thread()

# Function to plot temperature graphs
def plot_temperature_graph(ax, time_data, temp_data, title):
    ax.plot(time_data, temp_data, color="red")
    ax.set_xlabel("Time (seconds)", color="black")
    ax.set_ylabel("Temperature (°C)", color="black")
    ax.set_title(title, color="black")
    ax.grid(False)
    ax.tick_params(axis="x", colors="black")
    ax.tick_params(axis="y", colors="black")

# Streamlit 대시보드 UI 업데이트
while True:
    with data_lock:
        # 그래프 생성
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(20, 6))

        # 각 센서의 그래프 업데이트
        plot_temperature_graph(ax1, list(range(len(graph_data["Center Temperature"]))), list(graph_data["Center Temperature"]), "Center Temperature")
        plot_temperature_graph(ax2, list(range(len(graph_data["Left Temperature"]))), list(graph_data["Left Temperature"]), "Left Temperature")
        plot_temperature_graph(ax3, list(range(len(graph_data["Right Temperature"]))), list(graph_data["Right Temperature"]), "Right Temperature")

        # Streamlit에 그래프 표시
        central_chart.pyplot(fig)

        # 센서 데이터 테이블 업데이트
        sensor_values = [
            ["Center", sensor_data["Center"]["temperature"], sensor_data["Center"]["humidity"]],
            ["Left", sensor_data["Left"]["temperature"], sensor_data["Left"]["humidity"]],
            ["Right", sensor_data["Right"]["temperature"], sensor_data["Right"]["humidity"]],
            ["Heatbox", sensor_data["Heatbox"]["temperature"], sensor_data["Heatbox"]["humidity"]],
            ["External", sensor_data["External"]["temperature"], sensor_data["External"]["humidity"]],
        ]
        sensor_table.table(
            {
                "Location": [row[0] for row in sensor_values],
                "Temperature (°C)": [row[1] for row in sensor_values],
                "Humidity (%)": [row[2] for row in sensor_values],
            }
        )

        # 팬 상태 업데이트
        fan_state = sensor_data["fan_state"]
        fan_state_display.markdown(
            f"<h4 style='text-align: center;'>Fan State: <span style='color: {'green' if fan_state == 'ON' else 'red'};'>{fan_state}</span></h4>",
            unsafe_allow_html=True,
        )

    # 데이터 업데이트를 위해 3초 대기
    time.sleep(3)
