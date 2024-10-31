import requests
import vonage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import smtplib
import streamlit as st
import math
import re
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from threading import Timer

# 발신자 이메일과 앱 비밀번호 고정
SENDER_EMAIL = "jbnushading@gmail.com"
SENDER_PASSWORD = "zvrx ilcp jmfv qfrm"

# Nexmo(Vonage) API 설정
client = vonage.Client(key="89282f8a", secret="NJmve0B6Ot19OQYW")
sms = vonage.Sms(client)

# 필름 종류별 감쇠 계수와 두께 범위 설정
FILM_PROPERTIES = {
    "PE (80~200 µm)": {"attenuation": (0.08, 0.12), "thickness": (80, 200)},
    "PO (150~250 µm)": {"attenuation": (0.1, 0.14), "thickness": (150, 250)},
    "PVC (200~300 µm)": {"attenuation": (0.12, 0.18), "thickness": (200, 300)},
    "EVA (100~250 µm)": {"attenuation": (0.1, 0.15), "thickness": (100, 250)},
    "형판유리 (3~6 mm)": {"attenuation": (0.05, 0.08), "thickness": (3000, 6000)},  # µm 단위로 변환
    "판유리 (3~6 mm)": {"attenuation": (0.04, 0.07), "thickness": (3000, 6000)},
    "열선흡수유리 (3~6 mm)": {"attenuation": (0.07, 0.1), "thickness": (3000, 6000)},
    "비닐하우스 비닐 (150~200 µm)": {"attenuation": (0.15, 0.2), "thickness": (150, 200)},
}

# 차광막 상태와 시간을 관리
shade_status = "Open"
shade_close_time = None

# 실시간 데이터를 저장할 데이터프레임 생성
data = pd.DataFrame(columns=["시간", "외부 기온", "내부 기온", "외부 일사량", "내부 일사량"])

# 발신 이메일 서비스 선택에 따른 SMTP 설정 함수
def get_smtp_settings():
    return {
        'smtp_server': 'smtp.gmail.com',
        'port': 587,
        'email': SENDER_EMAIL,
        'password': SENDER_PASSWORD
    }

# Lambert-Beer 법칙을 통한 내부 일사량 계산 함수
def calculate_internal_irradiance(external_irradiance, material_attenuation, thickness):
    return external_irradiance * math.exp(-material_attenuation * thickness)

# 내부 기온 계산 함수
def calculate_internal_temperature(external_temperature, internal_irradiance, area, heat_constant=0.1):
    return external_temperature + heat_constant * (internal_irradiance * area)

# 이메일 형식 검증 함수
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

# 전화번호 형식 검증 함수
def is_valid_phone(phone):
    return re.match(r'^82\d{10}$', phone) is not None

# Streamlit 페이지 스타일링
st.markdown(
    """
    <style>
    .main { background-color: #F0FFF0; }
    h1 { color: #228B22; text-align: center; font-family: 'Arial', sans-serif; font-size: 30px; margin-bottom: 50px; }
    .css-18e3th9 { padding-top: 1rem; }
    .stButton button { display: block; margin: 0 auto; background-color: #4CAF50; color: white; font-size: 20px; border-radius: 12px; padding: 10px 24px; border: none; }
    input, select, textarea { font-family: 'Arial', sans-serif'; font-size: 16px; padding: 8px; border-radius: 8px; border: 1px solid #4CAF50; margin-bottom: 10px; width: 100%; }
    """,
    unsafe_allow_html=True
)

st.markdown('<h1>전북대 온실 차광막 제어 및 알림 시스템</h1>', unsafe_allow_html=True)

# 사용자 입력 필드
recipient_phone = st.text_input('전화번호 입력 (한국은 8210 뒤 8자리 입력, 예: 821012345678)', max_chars=12)
recipient_email = st.text_input('수신 이메일 입력')
temp_threshold = st.number_input("기온 임계값 (℃)", min_value=-50.0, max_value=50.0, value=30.0)
radiation_threshold = st.number_input("일사량 임계값 (W/m²)", min_value=0.0, max_value=3000.0, value=700.0)

# 필름 종류 선택
film_type = st.selectbox("필름 종류 선택", list(FILM_PROPERTIES.keys()))
film_info = FILM_PROPERTIES[film_type]
st.write(f"선택된 필름의 감쇠 계수 범위: {film_info['attenuation'][0]} ~ {film_info['attenuation'][1]}")
st.write(f"선택된 필름의 두께 범위: {film_info['thickness'][0]} ~ {film_info['thickness'][1]} µm")

# 감쇠 계수와 두께 직접 입력 또는 범위 내에서 선택
attenuation_input = st.radio("감쇠 계수 설정 방식", ("기본값 사용", "직접 입력"))
if attenuation_input == "기본값 사용":
    material_attenuation = sum(film_info['attenuation']) / 2  # 범위의 평균값 사용
else:
    material_attenuation = st.number_input("필름 감쇠 계수 입력", min_value=film_info['attenuation'][0], max_value=film_info['attenuation'][1])

thickness_input = st.radio("두께 설정 방식", ("기본값 사용", "직접 입력"))
if thickness_input == "기본값 사용":
    film_thickness = sum(film_info['thickness']) / 2  # 범위의 평균값 사용
else:
    film_thickness = st.number_input("필름 두께 입력 (µm)", min_value=film_info['thickness'][0], max_value=film_info['thickness'][1])

# 온실 면적 입력
area = st.number_input("온실 면적 (m²)", min_value=1.0, max_value=10000.0, value=100.0)

# 기상데이터 불러오는 함수
def fetch_weather_data():
    current_time = datetime.now()
    url = f"http://203.239.47.148:8080/dspnet.aspx?Site=85&Dev=1&Year={current_time.year}&Mon={current_time.month:02d}&Day={current_time.day:02d}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.text.splitlines()

        # 가장 최근 6개의 정각 데이터 선택
        recent_records = []
        for record in reversed(data):
            time_str = record.split(",")[0]
            time = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
            if time.minute == 0 and len(recent_records) < 6:
                recent_records.append(record)
            if len(recent_records) >= 6:
                break

        records = [r.split(",") for r in reversed(recent_records)]
        timestamps = [r[0] for r in records]
        temperatures = [float(r[1]) for r in records]
        irradiances = [float(r[6]) for r in records]

        return timestamps, temperatures, irradiances, current_time
    except Exception as e:
        st.error(f"데이터 불러오기 실패: {e}")
        return None, None, None, None

# 실시간 데이터를 업데이트하는 함수
def update_data(timestamps, temperatures, irradiances):
    global data
    for i in range(len(timestamps)):
        new_data = pd.DataFrame({
            "시간": [timestamps[i]],
            "외부 기온": [temperatures[i]],
            "내부 기온": [calculate_internal_temperature(temperatures[i], calculate_internal_irradiance(irradiances[i], material_attenuation, film_thickness / 1000), area)],
            "외부 일사량": [irradiances[i]],
            "내부 일사량": [calculate_internal_irradiance(irradiances[i], material_attenuation, film_thickness / 1000)]
        })
        data = pd.concat([data, new_data], ignore_index=True)

# 실시간 온도 그래프 그리기 함수
def plot_temperature_graph():
    st_graph = st.empty()
    fig, ax = plt.subplots()

    # 시간 기준으로 데이터 정렬
    data_sorted = data.sort_values(by="시간")

    # 그래프 시간 범위 설정 (현재 시각부터 과거 6시간까지)
    current_time = datetime.now()
    time_range_start = (current_time - timedelta(hours=6)).replace(minute=0, second=0, microsecond=0)
    time_range_end = current_time.replace(minute=0, second=0, microsecond=0)

    ax.set_xlim([time_range_start, time_range_end])
    ax.set_ylim([0, 40])

    # 실시간 온도 데이터 추가
    ax.plot(data_sorted["시간"], data_sorted["내부 기온"], label="내부 기온 (°C)", color="red")
    ax.axhline(y=temp_threshold, color='r', linestyle='--', label="기온 임계값 (°C)")

    ax.set_xlabel("시간")
    ax.set_ylabel("기온 (°C)")

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    fig.autofmt_xdate()

    ax.legend(loc="upper left")

    plt.title("실시간 내부 기온 모니터링")
    st_graph.pyplot(fig)

# 실시간 일사량 그래프 그리기 함수
def plot_radiation_graph():
    st_graph = st.empty()
    fig, ax = plt.subplots()

    # 시간 기준으로 데이터 정렬
    data_sorted = data.sort_values(by="시간")

    # 그래프 시간 범위 설정 (현재 시각부터 과거 6시간까지)
    current_time = datetime.now()
    time_range_start = (current_time - timedelta(hours=6)).replace(minute=0, second=0, microsecond=0)
    time_range_end = current_time.replace(minute=0, second=0, microsecond=0)

    ax.set_xlim([time_range_start, time_range_end])
    ax.set_ylim([0, 500])

    # 실시간 일사량 데이터 추가
    ax.plot(data_sorted["시간"], data_sorted["내부 일사량"], label="내부 일사량 (W/m²)", color="blue")
    ax.axhline(y=radiation_threshold, color='b', linestyle='--', label="일사량 임계값 (W/m²)")

    ax.set_xlabel("시간")
    ax.set_ylabel("일사량 (W/m²)")

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    fig.autofmt_xdate()

    ax.legend(loc="upper left")

    plt.title("실시간 내부 일사량 모니터링")
    st_graph.pyplot(fig)

# 모니터링 시작 함수
def start_monitoring():
    timestamps, temperatures, irradiances, fetch_time = fetch_weather_data()
    if timestamps is not None and temperatures is not None and irradiances is not None:
        update_data(timestamps, temperatures, irradiances)
        plot_temperature_graph()
        plot_radiation_graph()
        st.success("모니터링이 시작되었습니다. 1시간마다 데이터를 갱신합니다.")
        schedule_next_run()

# 다음 실행 예약 함수
def schedule_next_run():
    now = datetime.now()
    next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    delay = (next_hour - now).total_seconds()
    Timer(delay, start_monitoring).start()  # 1시간마다 실행

# 모니터링 시작 버튼
if st.button('모니터링 시작'):
    start_monitoring()

# 초기 그래프 업데이트
plot_temperature_graph()
plot_radiation_graph()
