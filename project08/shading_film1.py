import requests
import vonage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import streamlit as st
import time
import re
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from threading import Thread
from datetime import datetime, timedelta
from matplotlib import font_manager, rc

# 한글 폰트 설정 (Windows의 경우)
font_path = 'C:/Windows/Fonts/malgun.ttf'  # Windows 환경에서의 한글 폰트 경로
try:
    font_prop = font_manager.FontProperties(fname=font_path)
    font_name = font_prop.get_name()
    rc('font', family=font_name)
except:
    st.warning("한글 폰트를 찾을 수 없습니다. 그래프에서 한글이 제대로 표시되지 않을 수 있습니다.")

# 발신자 이메일과 앱 비밀번호
SENDER_EMAIL = "jbnushading@gmail.com"
SENDER_PASSWORD = "zvrx ilcp jmfv qfrm"

# Vonage API 설정
client = vonage.Client(key="a2b8f260", secret="X1ly0LQHIJRtY1Vp")
sms = vonage.Sms(client)

# 실시간 데이터를 저장할 데이터프레임 생성
data = pd.DataFrame(columns=["시간", "외부 기온", "외부 습도", "풍속", "일사량"])

# 사용자 알림 상태 저장 (중복 알림 방지)
if 'alert_sent' not in st.session_state:
    st.session_state.alert_sent = {}

# 실시간 기상 데이터 초기화 (session state)
if 'latest_time' not in st.session_state:
    st.session_state.latest_time = None
if 'latest_temperature' not in st.session_state:
    st.session_state.latest_temperature = None
if 'latest_humidity' not in st.session_state:
    st.session_state.latest_humidity = None
if 'latest_wind_speed' not in st.session_state:
    st.session_state.latest_wind_speed = None
if 'latest_irradiance' not in st.session_state:
    st.session_state.latest_irradiance = None

# 냉해 발생 조건 정의
frost_conditions = {
    "냉해": {
        "temperature_max": -2,  # 최저기온 -2°C 이하
        "humidity_min": 75,  # 상대습도 75% 이상
        "wind_speed_max": 2,  # 풍속 2 m/s 이하
        "irradiance_max_day": 300  # 낮 시간 일사량 300 W/m² 이하
    }
}


# 이메일 형식 검증 함수
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None


# 전화번호 형식 검증 함수 (82로 시작하는 12자리 숫자)
def is_valid_phone(phone):
    return re.match(r'^82\d{10}$', phone) is not None


# 발신 이메일 서비스 설정 함수
def get_smtp_settings():
    return {
        'smtp_server': 'smtp.gmail.com',
        'port': 587,
        'email': SENDER_EMAIL,
        'password': SENDER_PASSWORD
    }


# SMS 전송 함수
def send_sms(message, phone_number):
    if phone_number and is_valid_phone(phone_number):
        try:
            to_number = '+' + phone_number  # '+'를 앞에 추가하여 국제 형식으로 변환
            response_data = sms.send_message({
                "from": "AgriFrost",
                "to": to_number,
                "text": message[:70],
                "type": "unicode"
            })
            if response_data["messages"][0]["status"] == "0":
                st.success("SMS 전송 성공!")
            else:
                st.error(f"SMS 전송 실패: {response_data['messages'][0]['error-text']}")
        except Exception as e:
            st.error(f"SMS 전송 실패: {e}")
    elif phone_number and not is_valid_phone(phone_number):
        st.error("올바른 전화번호 형식이 아닙니다. 82로 시작하는 12자리 숫자를 입력하세요.")


# 이메일 발송 함수
def send_email(message, recipient_email):
    smtp_settings = get_smtp_settings()
    if smtp_settings is None:
        st.error("올바른 이메일 서비스를 선택하세요.")
        return

    if recipient_email and is_valid_email(recipient_email):
        try:
            msg = MIMEMultipart()
            msg['From'] = smtp_settings['email']
            msg['To'] = recipient_email
            msg['Subject'] = 'AgriFrost Alert'
            msg.attach(MIMEText(message, 'plain'))

            with smtplib.SMTP(smtp_settings['smtp_server'], smtp_settings['port']) as server:
                server.starttls()
                server.login(smtp_settings['email'], smtp_settings['password'])
                server.sendmail(smtp_settings['email'], recipient_email, msg.as_string())
            st.success("이메일 전송 완료!")
        except Exception as e:
            st.error(f"이메일 전송 오류: {e}")
    elif recipient_email and not is_valid_email(recipient_email):
        st.error("올바른 이메일 형식이 아닙니다.")


# 기상 데이터 불러오는 함수 (풍속 및 일사량 포함)
def fetch_plotting_data():
    current_time = datetime.now()
    # 이전 8시간의 정각 시간 생성
    times = [(current_time - timedelta(hours=i)).replace(minute=0, second=0, microsecond=0) for i in range(8)]
    times.reverse()  # 시간 순서대로 정렬

    timestamps = []
    temperatures = []
    humidities = []
    wind_speeds = []
    irradiances = []

    for time_point in times:
        url = f"http://203.239.47.148:8080/dspnet.aspx?Site=85&Dev=1&Year={time_point.year}&Mon={time_point.month:02d}&Day={time_point.day:02d}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data_lines = response.text.splitlines()

            # 해당 시간의 데이터를 찾음
            record_found = False
            for record in data_lines:
                fields = record.split(",")
                if len(fields) < 7:
                    continue
                try:
                    record_time = datetime.strptime(fields[0], '%Y-%m-%d %H:%M:%S')
                    if record_time == time_point:
                        timestamps.append(record_time)
                        temperature = float(fields[1])
                        humidity = float(fields[2])  # 외부 습도 (가정)
                        wind_speed = float(fields[3])  # 풍속 (가정)
                        irradiance = float(fields[6])  # 일사량
                        temperatures.append(temperature)
                        humidities.append(humidity)
                        wind_speeds.append(wind_speed)
                        irradiances.append(irradiance)
                        record_found = True
                        break
                except:
                    continue
            if not record_found:
                # 데이터가 없을 경우 None으로 채움
                timestamps.append(time_point)
                temperatures.append(None)
                humidities.append(None)
                wind_speeds.append(None)
                irradiances.append(None)
        except Exception as e:
            st.error(f"데이터 불러오기 실패: {e}")
            return None, None, None, None, None

    return timestamps, temperatures, humidities, wind_speeds, irradiances


# 낮 시간 여부 확인 함수
def is_daytime(time_point):
    return 9 <= time_point.hour < 18


# 냉해 발생 조건 체크 및 알림 함수
def check_frost_and_alert(record_time, temperature, humidity, wind_speed, irradiance, phone_number, recipient_email):
    condition = frost_conditions["냉해"]
    daytime = is_daytime(record_time)

    # 조건 확인
    temperature_condition = temperature is not None and temperature <= condition["temperature_max"]
    humidity_condition = humidity is not None and humidity >= condition["humidity_min"]
    wind_speed_condition = wind_speed is not None and wind_speed <= condition["wind_speed_max"]

    if daytime:
        irradiance_condition = irradiance is not None and irradiance <= condition["irradiance_max_day"]
    else:
        irradiance_condition = True  # 밤에는 일사량을 고려하지 않음

    # 낮과 밤에 따른 조건 분기
    if daytime:
        all_conditions_met = temperature_condition and humidity_condition and wind_speed_condition and irradiance_condition
    else:
        all_conditions_met = temperature_condition and humidity_condition and wind_speed_condition

    # 모든 조건이 충족되면 냉해 발생 가능
    if all_conditions_met:
        # 중복 알림 방지
        if "냉해" not in st.session_state.alert_sent:
            alert_message = f"경고: 냉해 발생 가능성이 높습니다! 적절한 조치를 취하세요."
            send_sms(alert_message, phone_number)
            send_email(alert_message, recipient_email)
            st.session_state.alert_sent["냉해"] = True
    else:
        # 조건 미충족 시 알림 상태 초기화
        if "냉해" in st.session_state.alert_sent:
            del st.session_state.alert_sent["냉해"]


# 실시간 모니터링 함수
def monitor_frost(phone_number, recipient_email):
    while st.session_state.get('thread_started', False):
        timestamps, temperatures, humidities, wind_speeds, irradiances = fetch_plotting_data()
        if timestamps:
            # 최신 데이터는 마지막 인덱스에 저장
            latest_index = -1
            record_time = timestamps[latest_index]
            temperature = temperatures[latest_index]
            humidity = humidities[latest_index]
            wind_speed = wind_speeds[latest_index]
            irradiance = irradiances[latest_index]

            st.session_state.latest_time = record_time
            st.session_state.latest_temperature = temperature
            st.session_state.latest_humidity = humidity
            st.session_state.latest_wind_speed = wind_speed
            st.session_state.latest_irradiance = irradiance

            # 데이터 업데이트
            update_data(timestamps, temperatures, humidities, wind_speeds, irradiances)

            # 냉해 체크 및 알림
            check_frost_and_alert(record_time, temperature, humidity, wind_speed, irradiance, phone_number,
                                  recipient_email)
        time.sleep(600)  # 10분마다 실행


# 그래프 그리기 함수
def plot_graph(parameter, ylabel, actual_color, min_value, max_value, y_ticks, threshold=None):
    if data.empty:
        st.write(f"{parameter} 데이터를 가져오는 중입니다...")
        return

    try:
        fig, ax = plt.subplots(figsize=(6, 6))  # 정사각형 크기로 설정

        # 시간 기준으로 데이터 정렬
        data_sorted = data.sort_values(by="시간")

        # 해당 파라미터 데이터 추가
        ax.plot(data_sorted["시간"], data_sorted[parameter], label=parameter, color=actual_color, marker='o')

        # 임계값 선 추가
        if threshold is not None:
            if parameter == "외부 기온":
                ax.axhline(y=threshold, color='green', linestyle='--', label='임계값 (-2°C)')
            elif parameter == "외부 습도":
                ax.axhline(y=threshold, color='green', linestyle='--', label='임계값 (75%)')
            elif parameter == "풍속":
                ax.axhline(y=threshold, color='green', linestyle='--', label='임계값 (2 m/s)')
            elif parameter == "일사량":
                # 낮 시간에만 임계값 선 표시
                daytime = is_daytime(datetime.now())
                if daytime:
                    ax.axhline(y=threshold, color='green', linestyle='--', label='임계값 (300 W/m²)')

        # 냉해 발생 지점 표시
        if parameter in ["외부 기온", "외부 습도", "풍속", "일사량"]:
            frost_indices = (
                    (data_sorted["외부 기온"] <= frost_conditions["냉해"]["temperature_max"]) &
                    (data_sorted["외부 습도"] >= frost_conditions["냉해"]["humidity_min"]) &
                    (data_sorted["풍속"] <= frost_conditions["냉해"]["wind_speed_max"])
            )
            if parameter == "일사량":
                # 낮 시간에만 일사량 고려
                frost_indices &= data_sorted["시간"].apply(is_daytime)
                frost_indices &= data_sorted["일사량"] <= frost_conditions["냉해"]["irradiance_max_day"]
            frost_data = data_sorted[frost_indices]
            if not frost_data.empty:
                ax.scatter(frost_data["시간"], frost_data[parameter], color='red', label='냉해 발생', zorder=5)

        ax.set_xlabel("시간", fontsize=10)
        ax.set_ylabel(ylabel, fontsize=10)

        ax.set_xticks(data_sorted["시간"])
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        fig.autofmt_xdate(rotation=45)

        # Y축 범위 설정 및 틱 설정
        ax.set_ylim(min_value, max_value)
        ax.set_yticks(y_ticks)

        # 배경을 흰색으로 설정
        ax.set_facecolor('white')
        fig.patch.set_facecolor('white')

        # 레전드를 그래프 내 우측 상단에 배치
        ax.legend(loc='upper right', fontsize='small')

        plt.title(f"{parameter} 모니터링", fontsize=12)
        st.pyplot(fig)
    except Exception as e:
        st.error(f"그래프를 그리는 중 오류가 발생했습니다: {e}")


# 실시간 데이터를 업데이트하고 그래프를 그리는 함수
def update_and_plot_graphs():
    # 데이터 업데이트는 이미 모니터링 함수에서 처리됨
    # 단, 첫 실행 시 데이터를 한번 더 가져올 수 있음
    if data.empty:
        timestamps, temperatures, humidities, wind_speeds, irradiances = fetch_plotting_data()
        if timestamps:
            update_data(timestamps, temperatures, humidities, wind_speeds, irradiances)


    # Streamlit의 Tabs를 사용하여 그래프 선택 가능하게 설정
    tabs = st.tabs(["외부 기온", "외부 습도", "풍속", "일사량"])

    with tabs[0]:
        plot_graph(
            parameter="외부 기온",
            ylabel="기온 (°C)",
            actual_color="#FF0000",
            min_value=-10,
            max_value=40,
            y_ticks=list(range(-10, 41, 5)),
            threshold=frost_conditions["냉해"]["temperature_max"]
        )

    with tabs[1]:
        plot_graph(
            parameter="외부 습도",
            ylabel="습도 (%)",
            actual_color="#0000FF",
            min_value=0,
            max_value=100,
            y_ticks=list(range(0, 101, 10)),
            threshold=frost_conditions["냉해"]["humidity_min"]
        )

    with tabs[2]:
        plot_graph(
            parameter="풍속",
            ylabel="풍속 (m/s)",
            actual_color="#800080",
            min_value=0,
            max_value=15,
            y_ticks=list(range(0, 16, 1)),
            threshold=frost_conditions["냉해"]["wind_speed_max"]
        )

    with tabs[3]:
        plot_graph(
            parameter="일사량",
            ylabel="일사량 (W/m²)",
            actual_color="#FFD700",
            min_value=0,
            max_value=500,
            y_ticks=list(range(0, 501, 50)),
            threshold=frost_conditions["냉해"]["irradiance_max_day"]
        )


# 데이터 업데이트 함수
def update_data(timestamps, temperatures, humidities, wind_speeds, irradiances):
    global data
    new_data = pd.DataFrame({
        "시간": timestamps,
        "외부 기온": temperatures,
        "외부 습도": humidities,
        "풍속": wind_speeds,
        "일사량": irradiances
    })
    data = pd.concat([data, new_data], ignore_index=True)
    # 중복 데이터 제거 (시간 기준)
    data.drop_duplicates(subset=["시간"], inplace=True)
    # 데이터 정렬
    data.sort_values(by="시간", inplace=True)
    data.reset_index(drop=True, inplace=True)


# Streamlit UI
st.markdown(
    """
    <style>
    .title {
        font-size: 35px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
        width: 100%;
    }
    </style>
    <div class="title">십자화과 채소 냉해 모니터링 및 알림 시스템</div>
    """,
    unsafe_allow_html=True
)

# 사용자 입력 (간소화)
recipient_phone = st.text_input('전화번호 입력 (82로 시작하는 12자리 숫자, 예: 821012345678)', max_chars=12)
recipient_email = st.text_input('수신 이메일 입력')

# 모니터링 시작 버튼
if st.button('모니터링 시작') and not st.session_state.get('thread_started', False):
    if not (recipient_phone or recipient_email):
        st.error("전화번호 또는 이메일을 입력하세요.")
    else:
        valid_phone = is_valid_phone(recipient_phone)
        valid_email = is_valid_email(recipient_email)

        if (valid_phone or valid_email):
            if valid_phone:
                send_sms("냉해 모니터링이 시작되었습니다.", recipient_phone)
            if valid_email:
                send_email("냉해 모니터링이 시작되었습니다.", recipient_email)

            thread = Thread(target=monitor_frost, args=(recipient_phone, recipient_email), daemon=True)
            thread.start()
            st.session_state.thread_started = True
            st.success("모니터링이 시작되었습니다.")

# Streamlit UI (모니터링 시작 후 추가 UI 표시 부분)
if st.session_state.get('thread_started', False):
    st.markdown("---")

    # "모니터링 중지" 버튼 추가
    if st.button("모니터링 중지"):
        st.session_state.thread_started = False
        st.experimental_rerun()

    # 그래프 시각화
    st.subheader("실시간 기상 데이터 그래프")
    update_and_plot_graphs()
else:
    st.write("모니터링을 시작하려면 '모니터링 시작' 버튼을 클릭하세요.")

    plt.tight_layout()
    plt.savefig("project08/graphs.png")  # 그래프를 파일로 저장
    st.pyplot(fig)


