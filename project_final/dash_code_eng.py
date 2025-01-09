# main_code.py를 통해 받아온 센서 데이터로 그래프와 데이터 프레임을 보여주는 웹서버를 만든 코드

import time
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.font_manager as fm
from main_code import sensor_data, graph_data, start_sensor_thread, data_lock

# Streamlit 설정
st.set_page_config(page_title="온실 환경 대시보드", layout="wide")  # 'wide' 레이아웃으로 설정

# 제목을 가운데 정렬
st.markdown("<h1 style='text-align: center;'>온실 내부 온도 균일 제어 시스템</h1>", unsafe_allow_html=True)

# "실시간 온도 데이터" 제목을 가운데 정렬하고 간격을 띄움
st.markdown("<h2 style='text-align: center; padding-top: 30px;'>실시간 온도 데이터 그래프</h2>", unsafe_allow_html=True)

# 팬 상태
fan_state_placeholder = st.empty()

# 센서 데이터 그래프
central_chart = st.empty()

# 센서 테이블
st.markdown("<h3 style='text-align: center; padding-top: 30px;'>실시간 온도 데이터 값</h3>", unsafe_allow_html=True)
sensor_table = st.empty()

# 팬 상태 표시를 위한 별도 테이블
st.markdown("<h3 style='text-align: center; padding-top: 30px;'>팬 상태</h3>", unsafe_allow_html=True)
fan_state_display = st.empty()

# 센서 스레드 시작: Streamlit에서 한 번만 실행되도록 보장
@st.cache_resource
def initialize_sensor_thread():
    return start_sensor_thread()

stop_event = initialize_sensor_thread()

# Function to plot temperature graphs
def plot_temperature_graph(ax, time_data, temp_data, title):
    ax.plot(time_data, temp_data, color='red')  # Set graph line color to red
    ax.set_xlabel('Time (seconds)', color='black')  # X-axis label
    ax.set_ylabel('Temperature (°C)', color='black')  # Y-axis label
    ax.set_title(title, color='black')  # Graph title
    ax.grid(False)  # Disable grid
    ax.tick_params(axis='x', colors='black')
    ax.tick_params(axis='y', colors='black')

try:
    while True:
        with data_lock:
            # Set graph size
            fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(20, 6))  # Set larger graph size

            # Temperature graphs for the center, left side, and right side
            plot_temperature_graph(ax1, list(range(len(graph_data["Center Temperature"]))), list(graph_data["Center Temperature"]), "Center Temperature")
            plot_temperature_graph(ax2, list(range(len(graph_data["Left Side Temperature"]))), list(graph_data["Left Side Temperature"]), "Left Side Temperature")
            plot_temperature_graph(ax3, list(range(len(graph_data["Right Side Temperature"]))), list(graph_data["Right Side Temperature"]), "Right Side Temperature")

            # Display matplotlib graph in Streamlit
            central_chart.pyplot(fig)

            # 센서 데이터 테이블 업데이트
            sensor_values = [
                ["중앙부", sensor_data["중앙부"]["temperature"], sensor_data["중앙부"]["humidity"]],
                ["좌측면", sensor_data["좌측면"]["temperature"], sensor_data["좌측면"]["humidity"]],
                ["우측면", sensor_data["우측면"]["temperature"], sensor_data["우측면"]["humidity"]],
                # 히트박스와 외부 데이터는 테이블에만 표시
                ["히트박스", sensor_data["히트박스"]["temperature"], sensor_data["히트박스"]["humidity"]],
                ["외부", sensor_data["외부"]["temperature"], sensor_data["외부"]["humidity"]],
            ]
            sensor_table.table(
                {
                    "위치": [row[0] for row in sensor_values],
                    "온도 (°C)": [row[1] for row in sensor_values],
                    "습도 (%)": [row[2] for row in sensor_values],
                }
            )

            fan_state = sensor_data["fan_state"]
            fan_state_display.markdown(
                f"<h4 style='text-align: center;'>팬 동작 여부: <span style='color: {'green' if fan_state == 'ON' else 'red'};'>{fan_state}</span></h4>",
                unsafe_allow_html=True
            )

        time.sleep(5)

except KeyboardInterrupt:
    stop_event.set()
    st.stop()
